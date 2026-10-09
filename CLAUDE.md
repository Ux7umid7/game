# CLAUDE.md — Island Weapon Pack (Blender)

Context for Claude Code sessions working on this repo. The owner writes in **Uzbek**; reply in Uzbek.

## What this is
**Target engine: Godot 4** (owner's decision). Stylized (cozy, chunky, beveled) weapon & item
models for an open-world island adventure game,
built **entirely from Python scripts** in Blender 5.1. `weapon_pack.blend` is a build output —
change the scripts, then rebuild; don't hand-edit the .blend and expect the scripts to follow.

### Game concept (from the owner)
1. **"Orol: yangi hayot"** — player arrives on an island, repairs an old house, chops wood, fishes,
   crafts, trades with villagers, explores caves/treasure. Weapons defend against enemies in
   dangerous zones.
2. **"Tinch kun, xavfli tun"** — calm days (build, gather, explore), robots attack at night;
   defend the base, set traps, upgrade weapons.
3. **"Besh qahramon — bitta sir"** — restore old structures to uncover the island's secret,
   switch between 5 characters with unique traversal abilities.

The original reference image showed 5 weapons (AR carbine, pistol, SMG w/ folding stock,
pump shotgun, scoped bolt-action rifle) in an olive / rust-brown / teal-tape / dark-metal palette.

## Contents
| Item (collection / root empty) | Script | Notes / additions over the reference |
|---|---|---|
| `AR_Carbine` | `blender_scripts/w_ar.py` | red-dot sight, vertical fore-grip, flashlight |
| `Pistol` | `w_pistol.py` | suppressor, under-rail light |
| `SMG` | `w_smg.py` | holo sight, stock tape, real holes in handguard |
| `Shotgun` | `w_shotgun.py` | buttstock shell carrier (5 shells), shell in ejection port |
| `Sniper` | `w_sniper.py` | bipod, cheek riser, sling studs |
| `Crossbow` | `w_extras.py` → `build_crossbow` | new item |
| `Hatchet` | `build_hatchet` | wood chopping / melee |
| `FlareGun` | `build_flaregun` | + spare flare cartridge (night signalling) |
| `EMP_Grenade` | `build_grenade` | glowing cyan bands (anti-robot) |
| `Ammo_Crate` | `build_ammo` | + loose rifle rounds and shotgun shells |

Other scripts: `wb.py` (helpers + all materials), `stage.py` (layout, backdrop, lights, cameras),
`build_all.py` (rebuilds everything), `render_headless.py` (build + save + render from CLI).

## Conventions (keep these)
- **Axes:** +X = muzzle/forward, +Z = up, **−Y = weapon's right side** (faces the sheet camera).
- **Units:** metres, real-world scale (AR ≈ 0.93 m, pistol ≈ 0.2 m without suppressor).
- Each item = its own collection under `Weapon_Pack`, with a root **Empty** named exactly like the
  collection; all parts are parented to it. Build each item at the origin; `stage.LAYOUT` moves roots.
- Part names are prefixed per item (`AR_`, `PST_`, `SMG_`, `SG_`, `SNP_`, `XB_`, `AXE_`, `FLR_`,
  `EMP_`, `AMMO_`). Parts stay separate objects (magazines etc. can be animated).
- Materials are named `WPN_*` and created in `wb.make_materials()`; access them via the `M` dict
  (`M["metal"]`, `M["olive"]`, `M["teal"]`, `M["wood"]`, `M["camo"]`, ...). Look up shader nodes by
  `type`, never by name (the owner's Blender UI is Russian-localized).
- Geometry helpers in `wb.py`: `box`, `boxes`, `prism` (XZ outline extruded along Y), `cyl`, `cyls`,
  `lathe` (revolve a profile), `cut` (applied boolean difference), `mirror_y`, `add_bevel`.
  Chunky look = bevel modifier (angle-limited, harden normals) + `set_sharp_from_angle(35°)`.
- `wb.begin(name, pack)` deletes and recreates that item's collection contents, so every build
  script is safe to re-run.

## How to rebuild
**Inside Blender:** Scripting tab → open `blender_scripts/build_all.py` → Run Script.

**From the command line (no GUI, recommended):**
```bash
blender --background --factory-startup --python blender_scripts/render_headless.py -- --samples 64 --shot=SheetCam --shot=CloseCam
```
Writes `weapon_pack.blend` and `renders/<Camera>.png`. `--no-render` only builds and saves.
On the owner's PC Blender lives at `D:\umid\prilojeniya\blender.exe` (not on PATH).
A 1920×1080 Cycles CPU render at 64 samples takes ~1.5 min.

**Via MCP:** the "MCP for Blender" add-on (`mcp__blender__*` tools) can drive a live Blender:
`runpy.run_path(".../blender_scripts/build_all.py", run_name="__main__")`.

## Known issues / gotchas
- **EEVEE crashes the owner's Blender** (the GPU driver can't handle the Rendered viewport, and Material
  Preview came back blank). Use Solid view in the GUI and render with **Cycles CPU** (already set
  in the file). Don't switch a live session into EEVEE Rendered via MCP.
- `camo`, `wood`, `wood_dk` and `axe_head` are **procedural** node materials; they won't survive
  glTF export to Godot (only flat Principled colours do). Bake them to image textures first
  (UV unwrap → bake Base Color). Plain `WPN_*` colour materials export fine.
- The parent folder on the owner's machine sits inside a git repo rooted at the user's home
  directory — always run git commands from this repo's root.

## Godot pipeline (planned)
- Export each item as **glTF binary (`.glb`)**, one file per root empty (select root + children,
  "Selected Objects", +Y Up on). Godot 4 converts Blender's Z-up automatically.
- Weapon forward is +X in Blender; in Godot the model's forward is −Z, so either rotate on export or
  wrap the imported scene in a Node3D rotated −90° about Y.
- Apply the bevel modifiers on export (glTF exporter "Apply Modifiers"), and apply root scale 1.0.
- Godot can also import `.blend` files directly if the Blender path is set in Editor Settings, but
  committed `.glb` files are more reliable for collaborators.

## Possible next steps (owner hasn't asked yet)
- Bake procedural textures + export each item as `.glb` for Godot (`exports/` folder).
- More island items: fishing rod, pickaxe, traps (idea #2), robot enemies.
