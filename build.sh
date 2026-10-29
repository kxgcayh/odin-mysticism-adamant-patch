#!/usr/bin/env bash
# Build Odin-Adamant-Mysticism-Patch.esp from input plugins and package the FOMOD zip.
# Inputs (put them in inputs/, see BUILDING.md):
#   Odin - Skyrim Magic Overhaul.esp
#   MysticismMagic.esp
#   Adamant.esp
# Output: dist/Odin - Mysticism - Adamant Compatibility Patch (FOMOD).zip
# Needs: dotnet (.NET 10+), python3, and Spriggit.Yaml.Skyrim 0.41.0 (SPRIGGIT_DLL or auto-detected).
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
ROOT="$PWD"
INPUTS="${INPUTS:-$ROOT/inputs}"
BUILD="$ROOT/build"
DIST="$ROOT/dist"
ZIP="$DIST/Odin-Mysticism-Adamant Compatibility Patch (FOMOD).zip"
GAME=(-g SkyrimSE -p Spriggit.Yaml.Skyrim -v 0.41.0)

ODIN="Odin - Skyrim Magic Overhaul.esp"
MYST="MysticismMagic.esp"
ADAM="Adamant.esp"

find_dll() {
  if [ -n "${SPRIGGIT_DLL:-}" ]; then echo "$SPRIGGIT_DLL"; return; fi
  local dir base
  for dir in "$HOME/.nuget/packages" "${TMPDIR:-}" /tmp; do
    [ -n "$dir" ] || continue
    base="$dir/spriggit.yaml.skyrim/0.41.0"
    [ -d "$base" ] || base="$dir/Spriggit/Translations/Spriggit.Yaml.Skyrim/0.41.0"
    [ -d "$base" ] || continue
    find "$base" -name Spriggit.Yaml.Skyrim.dll 2>/dev/null | head -n 1
  done | head -n 1
}
DLL="$(find_dll || true)"
if [ -z "$DLL" ] || [ ! -f "$DLL" ]; then
  echo "Spriggit.Yaml.Skyrim.dll 0.41.0 not found. See BUILDING.md ('Spriggit'), or set SPRIGGIT_DLL." >&2
  exit 1
fi

for f in "$ODIN" "$MYST" "$ADAM"; do
  [ -f "$INPUTS/$f" ] || { echo "missing input: $INPUTS/$f (see BUILDING.md)" >&2; exit 1; }
done

(cd "$INPUTS" && python3 -I - "$ROOT/patch/inputs.sha256" <<'PY'
import hashlib, sys
for line in open(sys.argv[1]):
    want, name = line.split(None, 1); name = name.strip()
    got = hashlib.sha256(open(name, "rb").read()).hexdigest()
    if got != want:
        print(f"warning: {name} differs from the version this patch was written for", file=sys.stderr)
PY
)

rm -rf "$BUILD"
mkdir -p "$BUILD/orig/odin" "$BUILD/orig/myst" "$BUILD/orig/adam" "$BUILD/yaml/patch" "$BUILD/package/00 Core" "$BUILD/package/fomod" "$DIST"

spriggit() { dotnet "$DLL" "$@" | grep -E "Unhandled|rror" || true; }

echo "serializing the original input plugins"
spriggit serialize -i "$INPUTS/$ODIN" -o "$BUILD/orig/odin" "${GAME[@]}"
spriggit serialize -i "$INPUTS/$MYST" -o "$BUILD/orig/myst" "${GAME[@]}"
spriggit serialize -i "$INPUTS/$ADAM" -o "$BUILD/orig/adam" "${GAME[@]}"

echo "applying compatibility patch rules"
python3 -I tools/apply_patch.py "$BUILD/orig/odin" "$BUILD/orig/myst" "$BUILD/orig/adam" "$ROOT/patch/rules.json" "$BUILD/yaml/patch"

echo "deserializing patch plugin"
spriggit deserialize -i "$BUILD/yaml/patch" -o "$BUILD/package/00 Core/Odin-Adamant-Mysticism-Patch.esp"

[ -s "$BUILD/package/00 Core/Odin-Adamant-Mysticism-Patch.esp" ] || { echo "deserialize produced no patch esp" >&2; exit 1; }

# Copy to dist for direct standalone use
cp "$BUILD/package/00 Core/Odin-Adamant-Mysticism-Patch.esp" "$DIST/"

# Generate meta.ini for Mod Organizer 2 with custom GitHub URL
cat > "$BUILD/package/00 Core/meta.ini" <<'EOF'
[General]
gameName=SkyrimSE
modid=0
version=1.0.0.0
newestVersion=1.0.0.0
category="27,"
repository=Custom
uploader=kxgcayh
url=https://github.com/kxgcayh/odin-mysticism-adamant-patch.git
hasCustomURL=true
comments=Compatibility patch for Odin, Mysticism, and Adamant
EOF
cp "$BUILD/package/00 Core/meta.ini" "$BUILD/package/meta.ini"

cp README.md "$BUILD/package/README.txt"
cp fomod-src/info.xml fomod-src/ModuleConfig.xml "$BUILD/package/fomod/"

echo "packaging FOMOD distribution archive"
python3 -I tools/package.py "$BUILD/package" "$ZIP"
