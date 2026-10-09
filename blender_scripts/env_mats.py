"""Flat-colour materials for houses and the jeep.

Everything here is a plain Principled BSDF (colour / roughness / metallic / emission / alpha) so it
exports to glTF -> Godot 4 without baking.
"""
import bpy
import wb


def _glassy(m, alpha):
    b = wb._bsdf(m)
    wb._set(b, "Alpha", alpha)
    for attr, val in (("surface_render_method", "BLENDED"), ("blend_method", "BLEND")):
        try:
            setattr(m, attr, val)
        except (AttributeError, TypeError):
            pass
    return m


def make():
    mb = wb.mat_basic
    M = {}
    # --- house shell
    M["plaster"] = mb("HSE_Plaster", "#EBDCBC", rough=0.95)
    M["plaster_old"] = mb("HSE_PlasterOld", "#C6B797", rough=0.95)
    M["plaster_new"] = mb("HSE_PlasterFresh", "#F3E9D3", rough=0.95)
    M["timber"] = mb("HSE_Timber", "#8E5531", rough=0.75)
    M["timber_dk"] = mb("HSE_TimberDark", "#663A1E", rough=0.75)
    M["timber_old"] = mb("HSE_TimberOld", "#6C5A48", rough=0.85)
    M["plank_a"] = mb("HSE_Plank_A", "#9C6339", rough=0.7)
    M["plank_b"] = mb("HSE_Plank_B", "#83512E", rough=0.7)
    M["plank_c"] = mb("HSE_Plank_C", "#AC7143", rough=0.7)
    M["end_grain"] = mb("HSE_EndGrain", "#C99B63", rough=0.8)
    M["bark"] = mb("HSE_Bark", "#5C452E", rough=0.95)
    M["stone_a"] = mb("HSE_Stone_A", "#A9A295", rough=0.9)
    M["stone_b"] = mb("HSE_Stone_B", "#8F887A", rough=0.9)
    M["stone_c"] = mb("HSE_Stone_C", "#BFB7A6", rough=0.9)
    M["mortar"] = mb("HSE_Mortar", "#6F695F", rough=0.95)
    # --- roofs
    M["slate_a"] = mb("HSE_Slate_A", "#4A5A8F", rough=0.6)
    M["slate_b"] = mb("HSE_Slate_B", "#5869A0", rough=0.6)
    M["slate_c"] = mb("HSE_Slate_C", "#3D4B7C", rough=0.6)
    M["slate_old"] = mb("HSE_SlateOld", "#5E6577", rough=0.8)
    M["moss"] = mb("HSE_Moss", "#5F7A33", rough=0.95)
    M["terra_a"] = mb("HSE_Terra_A", "#B85B33", rough=0.65)
    M["terra_b"] = mb("HSE_Terra_B", "#C96C3E", rough=0.65)
    M["terra_c"] = mb("HSE_Terra_C", "#A14C2A", rough=0.65)
    # --- glass / metal / glow
    M["glass_warm"] = _glassy(mb("HSE_GlassWarm", "#FFC66B", rough=0.1, emit="#FFB24D", emit_str=2.2), 0.82)
    M["glass_dark"] = _glassy(mb("HSE_GlassDark", "#2B3A40", rough=0.1), 0.55)
    M["glass_clear"] = _glassy(mb("HSE_GlassClear", "#D3E8EC", rough=0.05), 0.22)
    M["iron"] = mb("HSE_Iron", "#26282A", metal=0.6, rough=0.5)
    M["copper"] = mb("HSE_Copper", "#B2622F", metal=0.7, rough=0.4)
    M["fire"] = mb("HSE_Fire", "#FF7A1F", emit="#FF7A1F", emit_str=10.0)
    M["fire_core"] = mb("HSE_FireCore", "#FFD36A", emit="#FFD36A", emit_str=14.0)
    M["ash"] = mb("HSE_Ash", "#3B3734", rough=1.0)
    M["lamp_glow"] = mb("HSE_LampGlow", "#FFD28A", emit="#FFC970", emit_str=8.0)
    M["lamp_off"] = mb("HSE_LampOff", "#4A4E4F", rough=0.3)
    # --- plants
    M["leaf_a"] = mb("HSE_Leaf_A", "#4F8C2F", rough=0.7)
    M["leaf_b"] = mb("HSE_Leaf_B", "#69A63B", rough=0.7)
    M["leaf_c"] = mb("HSE_Leaf_C", "#3A7128", rough=0.7)
    M["vine"] = mb("HSE_Vine", "#5B4A2C", rough=0.9)
    M["grass"] = mb("HSE_Grass", "#7EA545", rough=0.95)
    M["grass_dk"] = mb("HSE_GrassDark", "#5E8A35", rough=0.95)
    M["dirt"] = mb("HSE_Dirt", "#8B6D4B", rough=1.0)
    M["flower_red"] = mb("HSE_FlowerRed", "#D8463A", rough=0.6)
    M["flower_yel"] = mb("HSE_FlowerYellow", "#F2C440", rough=0.6)
    M["flower_pur"] = mb("HSE_FlowerPurple", "#9160B8", rough=0.6)
    # --- interior
    M["fab_teal"] = mb("HSE_Fabric_Teal", "#2E6B66", rough=0.95)
    M["fab_cream"] = mb("HSE_Fabric_Cream", "#EFE5D1", rough=0.95)
    M["fab_red"] = mb("HSE_Fabric_Red", "#A53E2F", rough=0.95)
    M["fab_mustard"] = mb("HSE_Fabric_Mustard", "#C9962E", rough=0.95)
    M["clay"] = mb("HSE_Clay", "#BA653B", rough=0.8)
    M["ceramic"] = mb("HSE_Ceramic", "#E8E2D4", rough=0.3)
    M["paint_teal"] = mb("HSE_PaintTeal", "#3B8D87", rough=0.6)
    M["paint_white"] = mb("HSE_PaintWhite", "#EEE9DD", rough=0.7)
    M["book_a"] = mb("HSE_Book_A", "#7B2E28", rough=0.8)
    M["book_b"] = mb("HSE_Book_B", "#2F4F6E", rough=0.8)
    M["book_c"] = mb("HSE_Book_C", "#4F6B35", rough=0.8)
    # --- jeep
    M["car_body"] = mb("CAR_Teal", "#2FA09A", metal=0.25, rough=0.38)
    M["car_plastic"] = mb("CAR_Plastic", "#3B3B3A", rough=0.75)
    M["car_rubber"] = mb("CAR_Rubber", "#2B2927", rough=0.95)
    M["car_rim"] = mb("CAR_Rim", "#303234", metal=0.5, rough=0.45)
    M["car_chrome"] = mb("CAR_Chrome", "#C9CED3", metal=1.0, rough=0.15)
    M["car_head"] = mb("CAR_Headlight", "#FFF3CF", rough=0.05, emit="#FFF0C4", emit_str=1.5)
    M["car_ind"] = mb("CAR_Indicator", "#FF8A1C", rough=0.2, emit="#FF8A1C", emit_str=0.8)
    M["car_tail"] = mb("CAR_Tail", "#C2271F", rough=0.2, emit="#C2271F", emit_str=0.6)
    M["car_glass"] = _glassy(mb("CAR_Glass", "#DCE9EE", rough=0.05), 0.16)
    M["car_seat"] = mb("CAR_Seat", "#3C3F44", rough=0.9)
    M["car_dash"] = mb("CAR_Interior", "#2A2C2E", rough=0.8)
    M["car_mud"] = mb("CAR_Mud", "#6E5C45", rough=1.0)
    M["car_grille"] = mb("CAR_Grille", "#1C1D1E", rough=0.7)
    return M
