# Odin - Mysticism - Adamant Compatibility Patch

**Version 1.1.0**

An ESL-flagged (`.esp`) compatibility patch that allows **Odin - Skyrim Magic Overhaul** to run harmoniously alongside the **Mysticism - A Magic Overhaul** and **Adamant - A Perk Overhaul** ("Simonrim") suite.

Skyrim Special Edition and Anniversary Edition (1.5.97 – 1.6.1170+).

### Target Versions
This patch is authored and verified against the latest versions of all three mods:
- **Odin - Skyrim Magic Overhaul**: **v3.2.0** or newer
- **Mysticism - A Magic Overhaul**: **v2.5.0** or newer
- **Adamant - A Perk Overhaul**: **v6.0.4** (Adamant 6.x) or newer

Older versions of Adamant (v5.x and earlier) used different perk entry points and are not supported.

## Requirements

- [Odin - Skyrim Magic Overhaul](https://www.nexusmods.com/skyrimspecialedition/mods/46000) 3.2.0 or newer
- [Mysticism - A Magic Overhaul](https://www.nexusmods.com/skyrimspecialedition/mods/27839) 2.5.0 or newer
- [Adamant - A Perk Overhaul](https://www.nexusmods.com/skyrimspecialedition/mods/30191) 6.0.4 or newer
- [SkyPatcher](https://www.nexusmods.com/skyrimspecialedition/mods/106659), only for the optional Dawnguard Cache Tomes Fix

## The Problem

Both Odin and Mysticism are comprehensive magic overhauls. Adamant is explicitly designed around Mysticism, embedding custom perk hook effects directly into vanilla spell records.
1. **Broken Adamant Perks:** When Odin loads after Adamant, it strips out Adamant's injected perk hook effects (such as `MAG_PerkResolve...` on *Healing* and other Restoration spells, perk procs on cloak spells, necromancy bonuses on reanimate spells, and armor hooks on *Dragonhide*).
2. **Duplicate Spell Tomes:** Both mods add ~200 new spells, with 17 identical spells (Bound Greatsword, Bound War Axe, Bound Warhammer, Bound Mace, Command, Command Rune, Fear Rune, Flame Tempest, Hush, Mute, Panic, Rage, Slowfall, Soothe, Soul Harvest, Thundering Grasp, Viperbolt). Because Odin dynamically injects tomes at runtime via Papyrus quests, vendors end up selling duplicate competing tomes with conflicting stats and costs.
3. **Keyword & Scaling Inconsistencies:** Odin's unique spells lack Simonrim's keyword conventions (e.g. `MAG_MagicDamageSun`, `MAG_MagicDamagePoison`, `MAG_MagicCircleSpell`), preventing them from scaling properly with Adamant's perk tree.


## The Catch: What is Kept, Replaced, and Lost

Because Skyrim's engine enforces the "Rule of One" (only one plugin can define a record's final stats), running two full magic overhauls requires deciding which mod owns the baseline magic mechanics. This patch treats **Mysticism + Adamant as the core foundation**, and **Odin as a specialized spell expansion**.

### What is Kept (The Gains)
- **All ~180 unique Odin spells, scrolls, and mechanics**:
  - **Utility & World Interaction:** *Milestones* (5-point teleport network), *Create Object*, *Barricade*, *Web*, *Alibi*, *Feet of Notorgo*, *Deep Storage / Buried Storage*.
  - **Unique Illusion:** *Simulacrum* (create illusive duplicates of enemies that fight for you), *Propaganda*, *Wizard Rend*, *Shadow Legion*, *Elevram's Sty*.
  - **Unique Summons:** *Conjure Daedroth*, *Conjure Gloom Wraith*, *Conjure Clannfear*, *Conjure Xivilai*, *Exhume Wolf*.
  - **Restoration & Poison/Sun:** *Poison Nova*, *Accelerated Decay*, *Spider Touch*, *Sunhand*, *Radiant Beam*, *Sunstorm*, *Purifying Dawn*, *Hallowed Strikes*, *Blazing Strikes*.
  - **Unique Destruction:** *Ice Nova*, *Blast Wave*, *Arctic Blast*, *Frostbloom*.
- **Full Adamant perk scaling:** Simonrim damage and school keywords are forwarded onto Odin's unique spells so Adamant perks properly scale their magnitudes and durations.
- **Full Adamant perk integrity:** All Adamant perks work as SimonMagus designed without silent script failure.

### What is Replaced (Simonrim Wins)
- **All vanilla spells and effects:** When both mods modify a vanilla spell (e.g. *Flames, Fireball, Ice Storm, Fast Healing, Steadfast Ward, Oakflesh, Bound Bow, Atronach Summons*), **Mysticism and Adamant's version wins**.
- **17 Duplicate Spells:** Where both mods add the exact same spell (*Bound Greatsword/Mace/War Axe/Warhammer, Command, Command Rune, Fear Rune, Flame Tempest, Hush, Mute, Panic, Rage, Slowfall, Soothe, Soul Harvest, Thundering Grasp, Viperbolt*), **Mysticism's versions are used**.

### What is Lost (The Trade-Off)
- **Odin's changes to vanilla spells:** You will not experience EnaiSiaion's rebalance of vanilla spells (e.g., Odin's take on vanilla wards or concentration healing mechanics).
- **Odin's versions of the 17 duplicate tomes:** Pruned from vendor and loot distribution to prevent duplicate books with conflicting stats in shop inventories.

## The Solution

This patch adopts the **Simonrim Authoritative Baseline + Odin Expansion** architecture:
- **Load Order Priority:**
  ```text
  MysticismMagic.esp
  Adamant.esp
  Odin - Skyrim Magic Overhaul.esp
  Odin-Adamant-Mysticism-Patch.esp
  ```
- **353 Winning Overrides:** Forwards Simonrim's (Mysticism and Adamant) versions of all 353 conflicting vanilla records (112 Spells, 89 Magic Effects, 55 Scrolls, 40 Object Effects, 23 Keywords, 16 NPCs, 11 Books, 4 Weapons, 2 Constructible Objects, 1 Projectile), fully restoring Adamant's perk hook effects and balance.
- **Vendor & Loot Deduplication:** Prunes the 17 duplicate spell tomes from Odin's 24 distribution `ODN_F_...` FormLists. Odin's runtime quest will never inject duplicate tomes; Mysticism's versions remain canonical.
- **Keyword Integration:** Forwards necessary Simonrim keywords onto Odin's unique spells (Sun damage, Poison damage, Circle spells) so they scale seamlessly with Adamant's perk trees.
- **Light Plugin:** ESL-flagged (`[ESL]`), taking up 0 regular load order slots.
- **Auto-Detecting FOMOD Installer:** The included installer automatically verifies `plugins.txt` and only enables the patch option if all three required plugins are active.

## Optional: Dawnguard Cache Tomes Fix (Odin only)

A separate installer option for any Odin user, with or without Mysticism and Adamant. Requires [SkyPatcher](https://www.nexusmods.com/skyrimspecialedition/mods/106659).

Odin's `ODN_PopulateList_Script` (quest `ODN_PopulateLists`) runs once and adds Odin's tomes to vanilla leveled lists. Its Dawnguard step is `DLC1_WESC_DawnguardCacheItem.AddForm(ODN_Res_Litem_DawnguardSpells, 1, 1)`, but the script declares `ODN_Res_Litem_DawnguardSpells` as a `FormList` while Odin's plugin binds the leveled list `ODN_Res_Litem_DawnguardSpells` (`261219`). The property cannot bind, so it is `None` and the call adds nothing. The Papyrus log shows the failed binding at every new game. The Dawnguard supply caches (`DLC1_WESC_DawnguardCacheItem`, `Dawnguard.esm` `0181A5`) therefore never get Odin's 8 sun tomes: Sun Fire, Stendarr's Aura, Vampire's Bane, Sunstorm, Purifying Dawn, Radiant Beam, Sunhand and Sun Rune.

The option installs one SkyPatcher line that makes the same addition, level 1 and count 1:

```text
filterByLLs=Dawnguard.esm|0181A5:addToLLs=Odin - Skyrim Magic Overhaul.esp|261219~1~1
```

No plugin, no load order slot, no conflict with other edits to that list. None of the 8 tomes is among the 17 duplicates the main patch removes, so the two options work together.

## Install

Download `Odin-Mysticism-Adamant Compatibility Patch (FOMOD).zip` from the [Latest GitHub Release](https://github.com/kxgcayh/odin-mysticism-adamant-patch/releases/latest) and install it via Mod Organizer 2 or Vortex.

## Build from Source

See [BUILDING.md](BUILDING.md) for instructions on building the plugin yourself (Spriggit, input files, `build.sh`) and running the test suite.

## Verification Status

- Verified via round-trip Spriggit serialization with zero schema errors.
- Automated test suite in `tests/test_apply_patch.py` verifies record prioritization, FormList pruning, and keyword forwarding.
- ESL flag (`Small`) verified in binary header.
- Dawnguard Cache Tomes Fix: script behaviour read from Odin 3.2.0's compiled `ODN_PopulateList_Script.pex` (decompiled); FormIDs and the 8 tome records read from `Odin - Skyrim Magic Overhaul.esp` and `Dawnguard.esm`; no other active plugin in the maintainer's 871-plugin load order overrides `DLC1_WESC_DawnguardCacheItem`. Not yet confirmed in game.

## Credits and Permissions

Re-checked on 2026-11-11 against each mod's Nexus permission block and author notes: the permissions below still match.

- **[Odin - Skyrim Magic Overhaul](https://www.nexusmods.com/skyrimspecialedition/mods/46000)** by **EnaiSiaion**.
  - Permissions: Modification and patching are open with credit to the creator.
  - Credits: Mihailmods for the Daedroth, Clannfear, Xivilai, and Wraith meshes.
- **[Mysticism - A Magic Overhaul](https://www.nexusmods.com/skyrimspecialedition/mods/27839)** by **SimonMagus**.
  - Permissions: Open permissions (*"All of my work has open permissions. You do not need to ask permission to make patches, ports, forks, or any other derivative work from my mods."*).
  - Credits: SimonMagus & Simonrim contributors, Jay093 (poison spell meshes), Madcat221 (Holy Ground assets).
- **[Adamant - A Perk Overhaul](https://www.nexusmods.com/skyrimspecialedition/mods/30191)** by **SimonMagus**.
  - Permissions: Open permissions for patches, forks, and derivative works.

### Distribution & Non-Commercial Terms
- **Free and Open:** This patch is free, open-source, and granted under the same open permissions as the underlying mods.
- **No Monetization:** Do not sell, charge money for, or paywall this patch or its generated files on any platform.
- **No Bundled Assets:** This repository contains no bundled proprietary meshes, textures, or plugin binaries from the original mods; it only distributes compatibility delta definitions and build tooling.

## More mods

Other Skyrim mods by kxgcayh:

- [waccf-simonrim-skypatcher-patch](https://github.com/kxgcayh/waccf-simonrim-skypatcher-patch): Restores Simonrim enchantments, charges and names, and Gourmet effects, over WACCF's SkyPatcher configs.
- [tposc-compat-patch](https://github.com/kxgcayh/tposc-compat-patch): The People Of Skyrim Complete patch: forwards USSEP fixes and keeps its landscape and navmesh over Cutting Room Floor.
- [beasthhbb-ibeasts-jkj-patch](https://github.com/kxgcayh/beasthhbb-ibeasts-jkj-patch): Fixes headless and dark-faced Khajiit when Project ja-Kha'jay is used with BeastHHBB and iBeasts.
- [lawless-tamrielic-patch-update](https://github.com/kxgcayh/lawless-tamrielic-patch-update): Updates the Lawless Bandit War plugins for Tamrielic Distribution 2.0 and later.
- [UntarnishedUI-QuickLootIE-Patch](https://github.com/kxgcayh/UntarnishedUI-QuickLootIE-Patch): Untarnished UI skins for QuickLoot IE 4.x.
- [WhereWasI](https://github.com/kxgcayh/WhereWasI): SKSE plugin: a recap on save load after a break.

## License

The code, build tooling, and documentation in this repository (`tools/`, `build.sh`, `tests/`, `patch/`, `fomod-src/`, the Markdown files) are licensed under the [MIT License](LICENSE). Built plugins are derived from the respective mods and remain under their original permissions.
