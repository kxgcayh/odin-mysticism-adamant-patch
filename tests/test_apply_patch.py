"""Run: python3 -m unittest discover tests."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RULES_PATH = os.path.join(HERE, "patch", "rules.json")

def put(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)

class TestApplyPatch(unittest.TestCase):
    def test_mock_patch_application(self):
        root = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, root)
        
        odin_dir = os.path.join(root, "odin")
        myst_dir = os.path.join(root, "myst")
        adam_dir = os.path.join(root, "adam")
        out_dir = os.path.join(root, "out")
        mock_rules_path = os.path.join(root, "rules.json")

        mock_rules = {
            "duplicate_books_to_prune": ["199C43:Odin - Skyrim Magic Overhaul.esp"],
            "spell_keyword_additions": {
                "03EB82:Odin - Skyrim Magic Overhaul.esp": ["ADA002:Update.esm"]
            }
        }
        with open(mock_rules_path, "w", encoding="utf-8") as f:
            json.dump(mock_rules, f)

        # 1. Vanilla overlap: Healing spell (Adamant should beat Mysticism)
        put(os.path.join(odin_dir, "Spells", "ODN_Healing - 012FCC_Skyrim.esm.yaml"),
            "FormKey: 012FCC:Skyrim.esm\nEditorID: ODN_Healing\n")
        put(os.path.join(myst_dir, "Spells", "MAG_Healing - 012FCC_Skyrim.esm.yaml"),
            "FormKey: 012FCC:Skyrim.esm\nEditorID: MAG_Healing_Myst\n")
        put(os.path.join(adam_dir, "Spells", "MAG_Healing - 012FCC_Skyrim.esm.yaml"),
            "FormKey: 012FCC:Skyrim.esm\nEditorID: MAG_Healing_Adamant\n")

        # 2. FormList with duplicate book
        put(os.path.join(odin_dir, "FormLists", "ODN_F_Books - 11BB8A_Odin - Skyrim Magic Overhaul.esp.yaml"),
            "FormKey: 11BB8A:Odin - Skyrim Magic Overhaul.esp\nItems:\n- 199C43:Odin - Skyrim Magic Overhaul.esp\n- KEEP_ME:Odin - Skyrim Magic Overhaul.esp\n")

        # 3. Unique spell needing keywords
        put(os.path.join(odin_dir, "Spells", "ODN_DestroyLiving - 03EB82_Odin - Skyrim Magic Overhaul.esp.yaml"),
            "FormKey: 03EB82:Odin - Skyrim Magic Overhaul.esp\nEditorID: ODN_DestroyLiving\nEffects:\n- BaseEffect: 123456:Skyrim.esm\n")

        cmd = [
            sys.executable, os.path.join(HERE, "tools", "apply_patch.py"),
            odin_dir, myst_dir, adam_dir, mock_rules_path, out_dir
        ]
        r = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)

        # Assertions
        # 1. Adamant won the healing spell override
        with open(os.path.join(out_dir, "Spells", "MAG_Healing - 012FCC_Skyrim.esm.yaml")) as f:
            out_healing = f.read()
        self.assertIn("MAG_Healing_Adamant", out_healing)

        # 2. Duplicate book was pruned from FormList
        with open(os.path.join(out_dir, "FormLists", "ODN_F_Books - 11BB8A_Odin - Skyrim Magic Overhaul.esp.yaml")) as f:
            out_fl = f.read()
        self.assertNotIn("199C43:Odin - Skyrim Magic Overhaul.esp", out_fl)
        self.assertIn("KEEP_ME:Odin - Skyrim Magic Overhaul.esp", out_fl)

        # 3. Keyword was added to unique spell
        with open(os.path.join(out_dir, "Spells", "ODN_DestroyLiving - 03EB82_Odin - Skyrim Magic Overhaul.esp.yaml")) as f:
            out_spell = f.read()
        self.assertIn("Keywords:", out_spell)
        self.assertIn("ADA002:Update.esm", out_spell)

if __name__ == "__main__":
    unittest.main()
