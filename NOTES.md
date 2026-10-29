# Technical Notes: Odin - Mysticism - Adamant Compatibility Patch

## Overview

This repository provides an automated compatibility patch generator for running **Odin - Skyrim Magic Overhaul** alongside **Mysticism - A Magic Overhaul** and **Adamant - A Perk Overhaul** ("Simonrim").

- Patch Version: **1.0.0**
- Supported Game Editions: Skyrim Special Edition (SSE) and Skyrim Anniversary Edition (AE) 1.5.97 – 1.6.1170+.
- Target Plugin: `Odin-Adamant-Mysticism-Patch.esp` (ESL-flagged, load order slot: FE:xxx).
- Target Mod Versions:
  - **Odin - Skyrim Magic Overhaul**: v3.2.0+
  - **Mysticism - A Magic Overhaul**: v2.5.0+
  - **Adamant - A Perk Overhaul**: v6.0.4+ (Adamant 6.x)

### The Trade-Off & Design Philosophy
Skyrim's engine enforces the "Rule of One" (the last loaded plugin wins a given record). Because both Odin and Mysticism attempt to overhaul all ~112 vanilla spells and add overlapping spells, this patch establishes a clear hierarchy:
- **Foundation:** Simonrim (Mysticism + Adamant) controls all vanilla spells, magic effects, and perk hook integrations.
- **Expansion:** Odin acts as a content expansion pack providing its ~180 unique spells, mechanics, and summons.

| Category | Winner / Source | Notes |
|---|---|---|
| **Vanilla Spells & Effects** (112 spells, 89 effects) | **Simonrim (Adamant / Mysticism)** | Restores Adamant perk hooks (`MAG_PerkResolve...`, cloak perks, necromancy hooks). Odin's versions of vanilla spells are replaced. |
| **17 Duplicate New Spells** | **Mysticism** | Pruned from Odin's `ODN_F_...` distribution formlists so vendors only carry Mysticism's versions. |
| **Odin Unique Spells** (~180 spells) | **Odin** | Preserved in full (*Milestones, Simulacrum, Create Object, Barricade, Daedroth, Gloom Wraith, etc.*) and patched with Simonrim damage keywords for Adamant perk scaling. |

---

## 1. The Core Incompatibility

`Adamant.esp` has `MysticismMagic.esp` as an explicit hard master. To avoid script overhead, Adamant's perk trees (Restoration, Destruction, Conjuration, Alteration, Illusion) rely on custom magic effects injected directly into vanilla spell records:

| Record FormKey | Vanilla EditorID | Injected Adamant Base Effect | Purpose in Adamant |
|---|---|---|---|
| `012FCC:Skyrim.esm` | `Healing` | `6A5B58:Adamant.esp`, `D132C2:Adamant.esp` | Restoration *Resolve* perk |
| `02F3B8:Skyrim.esm` | `Fast Healing` | `6A5B58:Adamant.esp`, `D132C2:Adamant.esp` | Restoration *Resolve* perk |
| `0B62EF:Skyrim.esm` | `Greater Healing` | `6A5B58`, `D132C2`, `D132C4`, `D132C3` | Restoration *Resolve* perk tiers |
| `02B385:Skyrim.esm` | `Flame Cloak Proc` | `85E2FC`, `B466EE`, `849EE7`, `ABDBAD`, `9E4055` | Destruction Cloak perk scaling |
| `02B392:Skyrim.esm` | `Lightning Cloak Proc`| `3B34FF:Adamant.esp` | Destruction Cloak perk scaling |
| `065BD7:Skyrim.esm` | `Reanimate Corpse` | `20F14A:Adamant.esp` | Conjuration Necromancy bonus |
| `096D94:Skyrim.esm` | `Revenant` | `20F14A:Adamant.esp` | Conjuration Necromancy bonus |
| `096D95:Skyrim.esm` | `Dread Zombie` | `20F14A:Adamant.esp` | Conjuration Necromancy bonus |
| `0C969E:Skyrim.esm` | `Raise Zombie (LH)` | `20F14B:Adamant.esp` | Dual-cast / Off-hand Necromancy |
| `0038B6:Dawnguard.esm` | `Vampire's Bane` | `3C7909:Adamant.esp`, `B5AB09:Adamant.esp` | Sun damage scaling |
| `0CDB70:Skyrim.esm` | `Dragonhide` | `09862F:Adamant.esp` | Alteration Armor cap logic |

### The Load Order Conflict
- **If Odin loads after Adamant:** Odin overrides these vanilla records with EnaiSiaion's implementations, stripping out Adamant's injected perk effects. In-game, taking the corresponding perks yields no effect on vanilla spells.
- **If Odin loads before Mysticism/Adamant:** Mysticism and Adamant overwrite all of Odin's changes to vanilla spells and effects, neutralizing Odin's rebalance of vanilla magic.

---

## 2. Technical Solution: Simonrim Baseline + Odin Expansion

The patch adopts the **Simonrim Authoritative Baseline + Odin Expansion** architecture:

```text
MysticismMagic.esp
Adamant.esp
Odin - Skyrim Magic Overhaul.esp
Odin-Adamant-Mysticism-Patch.esp (ESL)
```

### 1. Overlapping Overrides Forwarding (353 records)
When a vanilla record is overridden by both Odin and Simonrim, the patch forwards Simonrim's version (giving priority to Adamant over Mysticism):
- 112 Spells
- 89 Magic Effects
- 55 Scrolls
- 40 Object Effects
- 23 Keywords
- 16 NPCs
- 11 Books
- 4 Weapons
- 2 Constructible Objects
- 1 Projectile

This restores all Adamant perk hooks, condition checks, and school archetypes across the entire spell catalog.

### 2. Spell Tome Deduplication (24 FormLists, 17 Duplicate Spells)
Both mods add ~200 new spells. 17 new spells share identical names and mechanical purposes. Odin distributes tomes at runtime using quest `ODN_Quest_Populate...` which reads from 24 `ODN_F_...` FormLists:

| Duplicate Spell Name | Odin Book FormKey | Odin Spell EditorID | Mysticism Spell EditorID |
|---|---|---|---|
| Bound Greatsword | `199C45:Odin - Skyrim Magic Overhaul.esp` | `ODN_Con_Bound2_Spell_BoundGreatsword` | `MAG_BoundGreatsword` |
| Bound Mace | `199C43:Odin - Skyrim Magic Overhaul.esp` | `ODN_Con_Bound1_Spell_BoundMace` | `MAG_BoundMace` |
| Bound War Axe | `199C44:Odin - Skyrim Magic Overhaul.esp` | `ODN_Con_Bound1_Spell_BoundWarAxe` | `MAG_BoundWarAxe` |
| Bound Warhammer | `199C46:Odin - Skyrim Magic Overhaul.esp` | `ODN_Con_Bound2_Spell_BoundWarhammer` | `MAG_BoundWarhammer` |
| Command | `20AFD0:Odin - Skyrim Magic Overhaul.esp` | `ODN_Ill_Command2_Spell_Command` | `MAG_Command` |
| Command Rune | `233858:Odin - Skyrim Magic Overhaul.esp` | `ODN_Ill_Command3_Spell_CommandRune` | `MAG_CommandRune` |
| Fear Rune | `233857:Odin - Skyrim Magic Overhaul.esp` | `ODN_Ill_Fear3_Spell_FearRune` | `MAG_FearRune` |
| Flame Tempest | `26B451:Odin - Skyrim Magic Overhaul.esp` | `ODN_Des_Fire5_Spell_FlameTempest` | `MAG_FlameTempest` |
| Hush | `2C16A3:Odin - Skyrim Magic Overhaul.esp` | `ODN_Ill_Antimage2_Spell_Hush` | `MAG_Hush` |
| Mute | `21F417:Odin - Skyrim Magic Overhaul.esp` | `ODN_Ill_Antimage3_Spell_Mute` | `MAG_Mute` |
| Panic | `17B5DB:Odin - Skyrim Magic Overhaul.esp` | `ODN_Ill_Fear3_Spell_Panic` | `MAG_Panic` |
| Rage | `17B5D7:Odin - Skyrim Magic Overhaul.esp` | `ODN_I075_Rage_Book` | `MAG_Rage` |
| Slowfall | `27568C:Odin - Skyrim Magic Overhaul.esp` | `ODN_Alt_Buff2_Spell_SlowFall` | `MAG_Slowfall` |
| Soothe | `17B5D8:Odin - Skyrim Magic Overhaul.esp` | `ODN_Ill_Calm3_Spell_Soothe` | `MAG_Soothe` |
| Soul Harvest | `1AFD1F:Odin - Skyrim Magic Overhaul.esp` | `ODN_Con_SoulTrap3_Spell_SoulHarvest` | `MAG_SoulHarvest` |
| Thundering Grasp | `03DB2C:Odin - Skyrim Magic Overhaul.esp` | `ODN_Des_Shock4_Spell_ThunderingGrasp` | `MAG_ThunderingGrasp` |
| Viperbolt | `2611FA:Odin - Skyrim Magic Overhaul.esp` | `ODN_Res_Poison2_Spell_Viperbolt` | `MAG_Viperbolt` |

The patch overrides all 24 `ODN_F_...` FormLists and removes these 17 Book FormKeys. At runtime, Odin's script injects only its unique tomes; Mysticism's versions remain canonical in vendors and loot chests.

### 3. Simonrim Keyword Forwarding (10 Spells)
To allow Odin's unique spells to scale with Adamant perks, required Simonrim keywords are forwarded onto Odin's unique spell records:

| Odin Spell FormKey | EditorID | Forwarded Keyword FormKey | Keyword EditorID |
|---|---|---|---|
| `03EB82:Odin - Skyrim Magic Overhaul.esp` | `ODN_R050_DestroyLiving_Spell` | `ADA002:Update.esm` | `MAG_MagicDamageSun` |
| `1CC707:Odin - Skyrim Magic Overhaul.esp` | `ODN_R050_SunRune_Spell` | `ADA002:Update.esm` | `MAG_MagicDamageSun` |
| `1CC6EF:Odin - Skyrim Magic Overhaul.esp` | `ODN_R050_Sunhand_Spell` | `ADA002:Update.esm` | `MAG_MagicDamageSun` |
| `1CC6EB:Odin - Skyrim Magic Overhaul.esp` | `ODN_R075_RadiantBeam_Spell` | `ADA002:Update.esm` | `MAG_MagicDamageSun` |
| `261216:Odin - Skyrim Magic Overhaul.esp` | `ODN_R075_Sunstorm_Spell` | `ADA002:Update.esm` | `MAG_MagicDamageSun` |
| `261217:Odin - Skyrim Magic Overhaul.esp` | `ODN_R100_PurifyingDawn_Spell` | `ADA002:Update.esm` | `MAG_MagicDamageSun` |
| `2611EF:Odin - Skyrim Magic Overhaul.esp` | `ODN_R000_SpiderTouch_Spell` | `ADA001:Update.esm` | `MAG_MagicDamagePoison` |
| `26120E:Odin - Skyrim Magic Overhaul.esp` | `ODN_Res_Poison4_Spell_AcceleratedDecay` | `ADA001:Update.esm` | `MAG_MagicDamagePoison` |
| `261211:Odin - Skyrim Magic Overhaul.esp` | `ODN_Res_Poison5_Spell_PoisonNova` | `ADA001:Update.esm` | `MAG_MagicDamagePoison` |
| `03EB90:Odin - Skyrim Magic Overhaul.esp` | `ODN_R075_CircleOfAsh_Spell` | `487DE8:MysticismMagic.esp` | `MAG_MagicCircleSpell` |

---

## 3. FOMOD Auto-Detection Specification

The installer in `fomod-src/ModuleConfig.xml` utilizes strict FOMOD dependency evaluation:
- `<defaultType name="NotUsable"/>`: If any required plugin (`Odin - Skyrim Magic Overhaul.esp`, `MysticismMagic.esp`, `Adamant.esp`) is not active in `plugins.txt`, Mod Organizer 2 flags the option as `[Not Usable]` and disables the checkbox.
- `<dependencies operator="And">`: When all three required plugins are active in the profile's load order, the option switches to `Recommended` and is automatically selected.
