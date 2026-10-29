# Building from source

Back to [README.md](README.md). Technical notes and record breakdowns are in [NOTES.md](NOTES.md).

This repository contains no plugin binaries from other mods. It holds only the patch rules (`patch/`), the tools (`tools/`), FOMOD metadata (`fomod-src/`), and tests (`tests/`). You supply the original plugins; Spriggit serializes them on your machine, `tools/apply_patch.py` applies the compatibility rules, and Spriggit deserializes the final patch plugin.

## Platforms

Tested: macOS (arm64, Apple Silicon). Expected to work on Linux and Windows:
- **Linux:** requires `bash`, `python3`, and the .NET 10 SDK.
- **Windows:** run `bash build.sh` via WSL or Git Bash (ensure `python3` and `dotnet` are in PATH).

## What you need

Obtain these three plugins from their official Nexus mod pages and place them into `inputs/` (create the directory):

| File in `inputs/` | Source | Target Version |
|---|---|---|
| `Odin - Skyrim Magic Overhaul.esp` | [Odin - Skyrim Magic Overhaul](https://www.nexusmods.com/skyrimspecialedition/mods/46000) by EnaiSiaion | **3.2.0** |
| `MysticismMagic.esp` | [Mysticism - A Magic Overhaul](https://www.nexusmods.com/skyrimspecialedition/mods/27839) by SimonMagus | **2.5.0** |
| `Adamant.esp` | [Adamant - A Perk Overhaul](https://www.nexusmods.com/skyrimspecialedition/mods/30191) by SimonMagus | **6.0.4** |

`patch/inputs.sha256` lists the SHA256 hashes of the files this patch was authored and verified against. A different hash prints a warning during `build.sh`.

Required tools:
- .NET 10 SDK (`dotnet --version` >= 10.0)
- Python 3 (`python3`)
- Spriggit 0.41.0 (`Spriggit.Yaml.Skyrim.dll`)

## Spriggit

[Spriggit](https://github.com/Mutagen-Modding/Spriggit) converts Skyrim plugins (`.esp`, `.esm`, `.esl`) into clean YAML text and back.

To install the global CLI:
```bash
dotnet tool install --global Spriggit.CLI --version 0.41.0
```

On macOS and Linux where the raw CLI tracker may fail, `build.sh` automatically detects the underlying `Spriggit.Yaml.Skyrim.dll` from your NuGet cache (`~/.nuget/packages/spriggit.yaml.skyrim/0.41.0/tools/net10.0/any/Spriggit.Yaml.Skyrim.dll`) or temporary directory. You can also explicitly specify it via:
```bash
export SPRIGGIT_DLL="/path/to/Spriggit.Yaml.Skyrim.dll"
```

## Build

```bash
bash build.sh
```

Output:
- `dist/Odin-Adamant-Mysticism-Patch.esp` (ESL-flagged standalone plugin)
- `dist/Odin-Mysticism-Adamant Compatibility Patch (FOMOD).zip` (Complete auto-detecting FOMOD installer)

### Build Pipeline:
1. Validates input plugin SHA256 hashes against `patch/inputs.sha256`.
2. Serializes `Odin - Skyrim Magic Overhaul.esp`, `MysticismMagic.esp`, and `Adamant.esp` to YAML using Spriggit.
3. `tools/apply_patch.py` parses the serialized trees and executes the rules defined in `patch/rules.json`:
   - Forwards 353 winning Simonrim overrides (preferring Adamant over Mysticism) to preserve all perk hook effects and school archetypes.
   - Prunes 17 duplicate spell books from 24 `ODN_F_...` runtime distribution FormLists.
   - Forwards Simonrim keywords (`MAG_MagicDamageSun`, `MAG_MagicDamagePoison`, `MAG_MagicCircleSpell`) onto 10 unique Odin spells.
4. Deserializes the patch YAML to `Odin-Adamant-Mysticism-Patch.esp` with ESL (`Small`) flag enabled.
5. `tools/package.py` validates `info.xml` and `ModuleConfig.xml`, stages the package directory, and builds the distribution zip archive.

## Testing

Run unit tests:
```bash
python3 -m unittest discover tests
```
The test suite validates mock patch application, FormList pruning, and keyword injection in isolation without requiring live mod installations.
