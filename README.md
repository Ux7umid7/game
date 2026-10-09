# Island Game Assets 🏝️

Orolda sarguzasht o'yini (Godot 4) uchun stilize qilingan 3D modellar. Hammasi Blender 5.1'da
Python skriptlar bilan yaratilgan.

## Uy — 3 xil variant, ichi bilan
O'yin hikoyasi: eski uyni topasan → ta'mirlaysan → kengaytirasan.

![Overview](renders/Cam_Overview.png)

| Eski uy | Ta'mirlangan uy | Kengaytirilgan uy |
|---|---|---|
| ![](renders/Cam_House_Ruined.png) | ![](renders/Cam_House_Cottage.png) | ![](renders/Cam_House_Upgraded.png) |

Kengaytirilgan uy — issiqxona, gul qutilari, panjara:

![Upgraded side](renders/Cam_House_Upgraded_Side.png)

Uy ichi (ta'mirlangan variant):

![Interior](renders/Cam_Interior.png)

## Jip
![Jeep](renders/Cam_Jeep.png)

## Qurollar
![Weapon sheet](renders/SheetCam.png)

## Fayllar
- `exports/*.glb` — Godot'ga to'g'ridan-to'g'ri import qilinadigan modellar (uy ×3, jip)
- `env_pack.blend` — uylar + jip sahnasi, `weapon_pack.blend` — qurollar
- `blender_scripts/` — hamma modellarni yasaydigan skriptlar
- `renders/` — render rasmlari
- `CLAUDE.md` — Claude Code uchun loyiha haqida to'liq ma'lumot

## Qayta qurish
Blender → Scripting → `blender_scripts/build_env.py` (yoki `build_all.py`) → Run Script

yoki terminaldan (render + Godot eksport bilan):
```bash
blender --background --factory-startup --python blender_scripts/render_headless.py -- --build build_env.py --blend env_pack.blend --export --shot=Cam_Overview
```
