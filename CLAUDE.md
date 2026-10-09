# CLAUDE.md — Island game assets (Blender → Godot 4)

Context for Claude Code sessions working on this repo. The owner writes in **Uzbek**; reply in Uzbek.

## What this is
**Target engine: Godot 4** (owner's decision). Stylized (cozy, chunky, beveled) 3D assets for an
open-world island adventure game, built **entirely from Python scripts** in Blender 5.1.
The `.blend` files and `exports/*.glb` are build outputs — change the scripts, then rebuild; don't
hand-edit the .blend and expect the scripts to follow.

Two packs:
| Pack | Build script | Output | Contents |
|---|---|---|---|
| Weapons | `blender_scripts/build_all.py` | `weapon_pack.blend` | 5 reference guns + 5 island items |
| Houses + jeep | `blender_scripts/build_env.py` | `env_pack.blend`, `exports/*.glb` | cottage ×3 variants (with interior), teal off-roader |

### Game concept (from the owner)
1. **"Orol: yangi hayot"** — player arrives on an island, repairs an old house, chops wood, fishes,
   crafts, trades with villagers, explores caves/treasure. Weapons defend against enemies in
   dangerous zones.
2. **"Tinch kun, xavfli tun"** — calm days (build, gather, explore), robots attack at night;
   defend the base, set traps, upgrade weapons.
3. **"Besh qahramon — bitta sir"** — restore old structures to uncover the island's secret,
   switch between 5 characters with unique traversal abilities.

## Weapons pack
Reference: 5 weapons (AR carbine, pistol, SMG w/ folding stock, pump shotgun, scoped bolt-action)
in an olive / rust-brown / teal-tape / dark-metal palette.

| Item (collection / root empty) | Script | Notes / additions over the reference |
|---|---|---|
| `AR_Carbine` | `w_ar.py` | red-dot sight, vertical fore-grip, flashlight |
| `Pistol` | `w_pistol.py` | suppressor, under-rail light |
| `SMG` | `w_smg.py` | holo sight, stock tape, real holes in handguard |
| `Shotgun` | `w_shotgun.py` | buttstock shell carrier (5 shells), shell in ejection port |
| `Sniper` | `w_sniper.py` | bipod, cheek riser, sling studs |
| `Crossbow` / `Hatchet` / `FlareGun` / `EMP_Grenade` / `Ammo_Crate` | `w_extras.py` | new island items |

Weapon axes: **+X = muzzle/forward**, +Z up, −Y = weapon's right side (faces the sheet camera).
Materials `WPN_*` from `wb.make_materials()`; `camo`, `wood`, `wood_dk`, `axe_head` are **procedural**
(won't survive glTF — bake before exporting weapons). Stage: `stage.py` (SheetCam, CloseCam).

## Houses + jeep pack (`env_pack.blend`)
Reference: a cozy stone-and-plaster cottage (blue slate roof, timber frame, ivy, porch, chimney,
dormer, lantern) and a teal 3-door off-roader (roof rack, round headlights, muddy tyres).

| Root (collection) | Script | What it is |
|---|---|---|
| `House_Ruined` | `h_house.py` variant `ruined` | "Eski uy": roof hole + missing/mossy tiles, boarded windows, hanging door, collapsed porch & woodshed, broken chimney, heavy ivy, weeds; inside: broken table, crates, debris, leaves, cold fireplace |
| `House_Cottage` | variant `cottage` | "Ta'mirlangan uy" = the reference: glowing windows, lit fireplace, furnished room (bed, table, kitchen counter, bookcase, armchair, rug…), door ajar |
| `House_Upgraded` | variant `upgraded` | "Kengaytirilgan uy": terracotta roof, teal shutters/door, greenhouse (+X side), flower boxes, picket fence, bench, mailbox, weather vane, hanging basket, extra decor |
| `Jeep` | `v_jeep.py` | off-roader with interior; 4 wheels + spare are separate objects with origin on the axle |

The three variants are the game story: find the old house → repair it → upgrade it. They share one
footprint, so the game can swap the model in place.

- **House axes:** front door faces **−Y**, +Z up, origin = footprint centre at ground level.
  Footprint 5.2 × 7.0 m (+ porch to y≈−5.7, woodshed to x≈−4.4, upgraded greenhouse to x≈4.5,
  fence at y=−8.4). Floor walking height `F0 = 0.48`, eaves 3.3 m, ridge ≈6.2 m. Door: `*_Door`
  object, origin on the hinge, rotate about local Z to open (positive = inward).
- **Jeep axes:** front = **−Y** (→ +Z in Godot, matching `VehicleBody3D`), left = +X, ground z=0.
  Wheels `JEEP_Wheel_FL/FR/RL/RR` at (±0.66, ∓1.12, 0.36), radius 0.36. Left-hand drive.
- Variant switches live in `h_house.VARIANTS` (roof palette, damage, ivy amount, porch/shed state,
  interior mode, extras list). Openings are in `h_house.OPENINGS` (per wall, local `u` coordinate:
  F: u=x, B: u=−x, L: u=−y, R: u=y). Furniture lives in `h_props.py`.
- Materials `HSE_*` / `CAR_*` (`env_mats.py`) are **flat Principled colours only** (plus emission /
  alpha), so they export to glTF → Godot without baking. Keep it that way.
- Interior point lights (`*_LampLight`, `*_FireLight`, `*_PorchLight`) exist only in the .blend; they
  are not exported (add OmniLight3D in Godot).
- Stage (`stage_env.py`, not exported): ground, dirt road, trees, rocks, grass, sun, cameras
  `Cam_Overview`, `Cam_House_Ruined/Cottage/Upgraded`, `Cam_House_Upgraded_Side`, `Cam_Interior`, `Cam_Jeep`.

## Shared helpers (`wb.py`)
- `wb.begin(name, pack)` recreates an asset's collection + root empty (safe to re-run).
- Weapon primitives: `box`, `boxes`, `prism`, `cyl`, `cyls`, `lathe`, `cut` (applied boolean),
  `mirror_y`, `add_bevel`. Chunky look = bevel (angle-limited, harden normals) + sharp edges at 35°.
- **`wb.Builder(name)`** — accumulates thousands of primitives with per-piece materials into ONE
  mesh (`box`, `box2`, `prism`, `poly` (flat, double-sided), `slab`, `cyl`, `lathe`), with a frame
  stack (`push(Matrix)`/`pop()`) for walls and roof slopes; `finish(bevel, segs, matrix=…)`.
  It writes vertices directly — do **not** reintroduce `bmesh.ops` calls per primitive (they scan the
  whole mesh and made the ruined house take 9 minutes instead of seconds).
- `wb.frame(origin, r, d)` builds a slope frame (u along r, v up-slope, w = outward normal).
- Look up shader nodes by `type`, never by name (the owner's Blender UI is Russian-localized).

## How to rebuild
On the owner's PC Blender lives at `D:\umid\prilojeniya\blender.exe` (not on PATH).

**Inside Blender:** Scripting tab → open `blender_scripts/build_all.py` or `build_env.py` → Run Script.

**Command line (recommended, no GUI):**
```bash
blender --background --factory-startup --python blender_scripts/render_headless.py -- --samples 64 --shot=SheetCam --shot=CloseCam
blender --background --factory-startup --python blender_scripts/render_headless.py -- --build build_env.py --blend env_pack.blend --export --samples 48 --shot=Cam_Overview --shot=Cam_House_Cottage --shot=Cam_Interior --shot=Cam_House_Ruined --shot=Cam_House_Upgraded --shot=Cam_House_Upgraded_Side --shot=Cam_Jeep
```
`--export` writes `exports/<Root>.glb` (one per asset, root moved to the origin, bevels applied).
`--no-render` only builds/saves. Env build ≈ 10 s; each Cycles CPU shot ≈ 1–3 min.

**Via MCP:** the "MCP for Blender" add-on (`mcp__blender__*` tools) can drive a live Blender:
`runpy.run_path(".../blender_scripts/build_env.py", run_name="__main__")`.

## Godot notes
- Import `exports/*.glb` directly. Godot converts Z-up → Y-up; house front ends up facing +Z.
- Godot 4 generates mesh LODs on import automatically — keep it on (houses ≈150–200k tris each).
- Glass materials are alpha-blended (`HSE_Glass*`, `CAR_Glass`); leaves/grass are single polygons and
  export double-sided.
- For collisions, use the import dialog (generate static/trimesh collision per mesh) or add simple
  box shapes for walls/floor; the door is its own node for an interaction script.

## Known issues / gotchas
- **EEVEE crashes the owner's Blender** (GPU driver can't handle the Rendered viewport; Material
  Preview came back blank). Use Solid view in the GUI and render with **Cycles CPU**. Don't switch a
  live session into EEVEE Rendered via MCP.
- **Overlapping coplanar faces render pitch black in Cycles** (each shadows the other). Give overlapping
  flat pieces (ground patches, path stones…) slightly different heights — this was the cause of the
  black spots on the grass, not normals or colour.
- Wall openings are one applied EXACT boolean (`use_self` on, because walls touch at the corners).
  Keep anything that overlaps the walls (like the dormer) in its own Builder, not in `Walls`.
- The parent folder on the owner's machine sits inside a git repo rooted at the user's home
  directory — always run git commands from this repo's root.

## Possible next steps (owner hasn't asked yet)
- Bake the weapons' procedural textures and export them as `.glb` too.
- Separate door leaves on the jeep (for enter/exit animations), LOD/collision meshes.
- More island content: fishing rod, pickaxe, traps (idea #2), robot enemies, villagers' houses
  (reuse `h_house.VARIANTS` with new palettes).
