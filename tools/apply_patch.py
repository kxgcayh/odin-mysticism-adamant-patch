#!/usr/bin/env python3
"""
apply_patch.py <odin_dir> <myst_dir> <adam_dir> <rules_json> <output_yaml_dir>
Applies compatibility rules between Odin, Mysticism, and Adamant to build patch YAML sources.
"""

import json
import os
import shutil
import sys
from collections import defaultdict

def index_records(src_dir):
    records = {} # FormKey: (relpath, abspath, rec_type)
    for root, _, files in os.walk(src_dir):
        for f in files:
            if f.endswith(".yaml") and "RecordData" not in f:
                path = os.path.join(root, f)
                rel = os.path.relpath(path, src_dir)
                rec_type = os.path.basename(root)
                fk = None
                with open(path, "r", encoding="utf-8", errors="ignore") as fp:
                    for line in fp:
                        if line.startswith("FormKey:"):
                            fk = line.split(":", 1)[1].strip()
                            break
                if fk:
                    records[fk] = (rel, path, rec_type)
    return records

def main():
    if len(sys.argv) < 6:
        print("Usage: apply_patch.py <odin_dir> <myst_dir> <adam_dir> <rules_json> <output_yaml_dir>", file=sys.stderr)
        sys.exit(1)

    odin_dir, myst_dir, adam_dir, rules_path, out_dir = sys.argv[1:6]

    with open(rules_path, "r", encoding="utf-8") as f:
        rules = json.load(f)

    if os.path.exists(out_dir):
        shutil.rmtree(out_dir)
    os.makedirs(out_dir, exist_ok=True)

    header_content = """SpriggitSource:
  PackageName: Spriggit.Yaml.Skyrim
  Version: 0.41.0
ModKey: Odin-Adamant-Mysticism-Patch.esp
GameRelease: SkyrimSE
ModHeader:
  Flags:
  - Small
  Stats:
    Version: 1.7
  Author: kxgcayh
  Description: v1.0.0 - Compatibility patch for Odin, Mysticism, and Adamant. Restores Simonrim/Adamant perk hooks, forwards keywords to Odin spells, and deduplicates spell distribution.
  MasterReferences:
  - Master: Skyrim.esm
    FileSize: 0
  - Master: Update.esm
    FileSize: 0
  - Master: Dawnguard.esm
    FileSize: 0
  - Master: HearthFires.esm
    FileSize: 0
  - Master: Dragonborn.esm
    FileSize: 0
  - Master: MysticismMagic.esp
    FileSize: 0
  - Master: Adamant.esp
    FileSize: 0
  - Master: Odin - Skyrim Magic Overhaul.esp
    FileSize: 0
  INTV: 1
"""
    with open(os.path.join(out_dir, "RecordData.yaml"), "w", encoding="utf-8") as f:
        f.write(header_content)

    print("Indexing serialized input records...")
    odin_recs = index_records(odin_dir)
    myst_recs = index_records(myst_dir)
    adam_recs = index_records(adam_dir)

    vanilla_masters = {"Skyrim.esm", "Update.esm", "Dawnguard.esm", "HearthFires.esm", "Dragonborn.esm"}
    odin_vanilla = {fk for fk in odin_recs if fk.split(":", 1)[-1] in vanilla_masters}
    simon_vanilla = {fk for fk in (set(myst_recs.keys()) | set(adam_recs.keys())) if fk.split(":", 1)[-1] in vanilla_masters}
    overlapping_vanilla = odin_vanilla & simon_vanilla

    expected_overlap = rules.get("expected_overlapping_vanilla_overrides")
    if expected_overlap and len(overlapping_vanilla) != expected_overlap:
        print(f"Warning: overlapping vanilla overrides ({len(overlapping_vanilla)}) differs from expected ({expected_overlap})", file=sys.stderr)

    for fk in sorted(overlapping_vanilla):
        if fk in adam_recs:
            rel, src_path, _ = adam_recs[fk]
        else:
            rel, src_path, _ = myst_recs[fk]
        dest_path = os.path.join(out_dir, rel)
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        shutil.copyfile(src_path, dest_path)

    dup_books = set(rules.get("duplicate_books_to_prune", []))
    odin_fl_dir = os.path.join(odin_dir, "FormLists")
    pruned_count = 0
    if os.path.isdir(odin_fl_dir):
        for f in os.listdir(odin_fl_dir):
            if f.startswith("ODN_F_") and f.endswith(".yaml"):
                fl_src = os.path.join(odin_fl_dir, f)
                lines = open(fl_src, "r", encoding="utf-8", errors="ignore").readlines()
                new_lines = []
                modified = False
                for line in lines:
                    s = line.strip()
                    if s.startswith("- ") and s[2:].strip() in dup_books:
                        modified = True
                    else:
                        new_lines.append(line)
                if modified:
                    pruned_count += 1
                    fl_dest = os.path.join(out_dir, "FormLists", f)
                    os.makedirs(os.path.dirname(fl_dest), exist_ok=True)
                    with open(fl_dest, "w", encoding="utf-8") as out_fp:
                        out_fp.writelines(new_lines)

    expected_fl = rules.get("expected_pruned_formlists")
    if expected_fl and pruned_count != expected_fl:
        print(f"Warning: pruned formlist count ({pruned_count}) differs from expected ({expected_fl})", file=sys.stderr)

    spell_kws = rules.get("spell_keyword_additions", {})
    patched_spells = 0
    for spell_fk, kws_to_add in spell_kws.items():
        if spell_fk in odin_recs:
            rel, src_path, _ = odin_recs[spell_fk]
            dest_path = os.path.join(out_dir, rel)
            lines = open(src_path, "r", encoding="utf-8", errors="ignore").readlines()
            
            has_keywords = any(l.strip() == "Keywords:" for l in lines)
            new_lines = []
            if has_keywords:
                for line in lines:
                    new_lines.append(line)
                    if line.strip() == "Keywords:":
                        for kw in kws_to_add:
                            new_lines.append(f"- {kw}\n")
            else:
                added = False
                for line in lines:
                    if line.strip() == "Effects:" and not added:
                        new_lines.append("Keywords:\n")
                        for kw in kws_to_add:
                            new_lines.append(f"- {kw}\n")
                        added = True
                    new_lines.append(line)
                if not added:
                    new_lines.append("Keywords:\n")
                    for kw in kws_to_add:
                        new_lines.append(f"- {kw}\n")

            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            with open(dest_path, "w", encoding="utf-8") as out_fp:
                out_fp.writelines(new_lines)
            patched_spells += 1

    expected_sp = rules.get("expected_patched_spells")
    if expected_sp and patched_spells != expected_sp:
        print(f"Warning: patched spell count ({patched_spells}) differs from expected ({expected_sp})", file=sys.stderr)

    print(f"Built patch YAML in {out_dir}:")
    print(f"  {len(overlapping_vanilla)} forwarded Simonrim overrides")
    print(f"  {pruned_count} pruned distribution FormLists")
    print(f"  {patched_spells} keyword-patched Odin spells")

if __name__ == "__main__":
    main()
