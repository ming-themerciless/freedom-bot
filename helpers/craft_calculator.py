from typing import Dict, Any, Tuple, Optional

# Poisons table from PDF page 24-25
POISON_TABLE = {
    "assassin's blood": {"gp": 75, "j": 1.0, "e": 0.5, "m": 0.25},
    "truth serum": {"gp": 75, "j": 1.0, "e": 0.5, "m": 0.25},
    "carrion crawler mucus": {"gp": 100, "j": 1.0, "e": 0.5, "m": 0.25},
    "lolth's sting": {"gp": 100, "j": 1.0, "e": 0.5, "m": 0.25},
    "serpent venom": {"gp": 100, "j": 2.0, "e": 1.0, "m": 0.5},
    "malice": {"gp": 125, "j": 2.0, "e": 1.0, "m": 0.5},
    "pale tincture": {"gp": 125, "j": 2.0, "e": 1.0, "m": 0.5},
    "essence of ether": {"gp": 150, "j": 2.0, "e": 1.0, "m": 0.5},
    "biza's breath": {"gp": 200, "j": None, "e": 2.0, "m": 1.0},
    "oil of taggit": {"gp": 200, "j": None, "e": 2.0, "m": 1.0},
    "burnt othur fumes": {"gp": 250, "j": None, "e": 2.0, "m": 1.0},
    "torpor": {"gp": 300, "j": None, "e": 2.0, "m": 1.0},
    "wyvern poison": {"gp": 600, "j": None, "e": None, "m": 2.0},
    "midnight tears": {"gp": 750, "j": None, "e": None, "m": 2.5},
    "yserthrax's corruption": {"gp": 750, "j": None, "e": None, "m": 2.5},
    "purple worm poison": {"gp": 1500, "j": None, "e": None, "m": 3.0}
}

# Spell Scrolls & Tattoos table from PDF page 23-24
SCROLL_TATTOO_TABLE = {
    0: {"j": 1.0, "e": 0.5, "m": 0.25, "tattoo": 40, "scroll": 25},
    1: {"j": 2.0, "e": 1.0, "m": 0.5,  "tattoo": 60, "scroll": 40},
    2: {"j": None, "e": 1.5, "m": 1.0, "tattoo": 80, "scroll": 50},
    3: {"j": None, "e": 2.0, "m": 1.5, "tattoo": 150, "scroll": 100},
    4: {"j": None, "e": None, "m": 2.0, "tattoo": 300, "scroll": 200},
    5: {"j": None, "e": None, "m": 3.0, "tattoo": 450, "scroll": 300},
    6: {"j": None, "e": None, "m": 5.0, "tattoo": None, "scroll": 400},
    7: {"j": None, "e": None, "m": 10.0, "tattoo": None, "scroll": 600},
    8: {"j": None, "e": None, "m": 15.0, "tattoo": None, "scroll": 1000},
    9: {"j": None, "e": None, "m": 20.0, "tattoo": None, "scroll": 2000}
}

# Brews table from PDF page 27
# Key: (spell_level, has_concentration)
BREW_TABLE = {
    (0, False): {"j": 0.5, "e": 0.25, "m": 0.125, "gp": 25},
    (0, True):  {"j": 1.0, "e": 0.5,  "m": 0.25,  "gp": 30},
    (1, False): {"j": 2.0, "e": 1.0,  "m": 0.5,   "gp": 40},
    (1, True):  {"j": None, "e": 1.5, "m": 1.0,   "gp": 50},
    (2, False): {"j": None, "e": 2.0, "m": 1.5,   "gp": 100},
    (2, True):  {"j": None, "e": None, "m": 2.0,   "gp": 200},
    (3, False): {"j": None, "e": None, "m": 3.0,   "gp": 300}
}

def calculate_craft(
    craft_type: str,
    rarity: str,
    tool: str,
    tool_level: str,
    quantity: int,
    item_name: str,
    base_price: Optional[float] = None,
    spell_level: Optional[int] = None,
    has_concentration: bool = False,
    extra_cost: float = 0.0,
    is_masterpiece: bool = False,
    gather_ingredients: bool = False,
    has_master_tool: bool = False
) -> Dict[str, Any]:
    """
    Validates crafting options and calculates GP, Moradinium, DT cost, and earned CRP.
    Returns a dictionary with the results, or raises a ValueError on validation error.
    """
    tool_clean = tool.strip().lower()
    tool_level_abbr = {"journeyman": "j", "expert": "e", "master": "m"}.get(tool_level, tool_level)

    # 1. Enforce Tool-specific constraints
    if craft_type == "scroll" and "calligrapher" not in tool_clean:
        raise ValueError("Scrolls require Calligrapher's Supplies.")
    if craft_type == "tattoo" and "painter" not in tool_clean:
        raise ValueError("Spellwrought Tattoos require Painter's Supplies.")
    if craft_type == "brew" and "brewer" not in tool_clean:
        raise ValueError("Brews require Brewer's Supplies.")
    if craft_type == "meal" and "cook" not in tool_clean:
        raise ValueError("Fancy meals require Cook's Utensils.")
    if gather_ingredients and "herbalism" not in tool_clean:
        raise ValueError("Gathering ingredients is only allowed when using a Herbalism Kit.")

    # 2. Check tool level vs rarity allowance
    rarity_allowed = {
        "journeyman": ["standard", "common"],
        "expert": ["standard", "common", "uncommon"],
        "master": ["standard", "common", "uncommon", "rare", "very rare", "legendary"]
    }
    if rarity not in rarity_allowed.get(tool_level, []):
        raise ValueError(
            f"{tool_level.capitalize()} level with {tool} is insufficient to craft a {rarity} item. Requires higher proficiency."
        )

    # 3. Validation for Masterpieces
    if is_masterpiece:
        if tool_level != "master":
            raise ValueError("You must have Master level in the tool to craft a Masterpiece.")
        if craft_type != "non-consumable":
            raise ValueError("Masterpieces must be non-consumable items.")

    # 4. Meal-specific validations
    if craft_type == "meal":
        if rarity not in ("common", "uncommon", "rare"):
            raise ValueError("Fancy meals can only be crafted in common (1 effect), uncommon (2 effects), or rare (3 effects) rarity.")

    # 5. Gather-ingredients-specific validations
    if gather_ingredients:
        if craft_type == "non-consumable":
            raise ValueError("Gathering ingredients is only allowed for consumables, potions, or drugs (not non-consumables).")

    # 6. Rarity/Price parameter validations
    if rarity == "standard" and base_price is None:
        raise ValueError("Base price must be specified when crafting a standard item.")
    if craft_type in ("scroll", "tattoo", "brew") and spell_level is None:
        raise ValueError("Spell level must be specified for scrolls, tattoos, and brews.")

    gp_cost = 0.0
    moradinium_cost = 0
    dt_cost = 0.0
    is_legendary_project = (rarity == "legendary" and craft_type == "non-consumable")

    if is_legendary_project:
        gp_cost = 100000.0 * quantity
        moradinium_cost = 256 * quantity
        # DT cost is handled dynamically by roll progression
    else:
        if craft_type == "non-consumable":
            if rarity == "standard":
                gp_cost = (base_price / 2.0) * quantity
                dt_div = {"journeyman": 10.0, "expert": 25.0, "master": 75.0}[tool_level]
                dt_cost = (base_price / dt_div) * quantity
            elif rarity == "common":
                gp_cost = 50.0 * quantity
                moradinium_cost = 1 * quantity
                dt_cost = {"journeyman": 5.0, "expert": 3.0, "master": 1.0}[tool_level] * quantity
            elif rarity == "uncommon":
                gp_cost = 200.0 * quantity
                moradinium_cost = 4 * quantity
                dt_cost = {"expert": 5.0, "master": 3.0}[tool_level] * quantity
            elif rarity == "rare":
                gp_cost = 2000.0 * quantity
                moradinium_cost = 16 * quantity
                dt_cost = 5.0 * quantity
            elif rarity == "very rare":
                gp_cost = 20000.0 * quantity
                moradinium_cost = 64 * quantity
                dt_cost = 20.0 * quantity

        elif craft_type in ("consumable", "meal"):
            if rarity == "standard":
                base_gp = (base_price / 2.0) * quantity
                dt_div = {"journeyman": 25.0, "expert": 50.0, "master": 100.0}[tool_level]
                dt_cost = (base_price / dt_div) * quantity
            elif rarity == "common":
                base_gp = 25.0 * quantity
                dt_cost = {"journeyman": 1.0, "expert": 0.5, "master": 0.25}[tool_level] * quantity
            elif rarity == "uncommon":
                base_gp = 50.0 * quantity
                dt_cost = {"expert": 1.0, "master": 0.5}[tool_level] * quantity
            elif rarity == "rare":
                base_gp = 200.0 * quantity
                dt_cost = 1.0 * quantity
            elif rarity == "very rare":
                base_gp = 400.0 * quantity
                dt_cost = 5.0 * quantity
            elif rarity == "legendary":
                base_gp = 1000.0 * quantity
                dt_cost = 20.0 * quantity

            # Fancy meal costs 5% of standard consumable GP cost
            if craft_type == "meal":
                gp_cost = base_gp * 0.05
            else:
                gp_cost = base_gp + extra_cost

        elif craft_type in ("scroll", "tattoo"):
            level_data = SCROLL_TATTOO_TABLE.get(spell_level)
            if not level_data:
                raise ValueError(f"Invalid spell level {spell_level}.")
            
            item_base_gp = level_data.get(craft_type)
            if item_base_gp is None:
                raise ValueError(f"Cannot craft a {craft_type} of spell level {spell_level}.")
            
            dt_per_item = level_data.get(tool_level_abbr)
            if dt_per_item is None:
                raise ValueError(
                    f"Your level {tool_level} is insufficient to craft a {spell_level}-level {craft_type}."
                )
            
            gp_cost = float(item_base_gp) * quantity + extra_cost
            dt_cost = float(dt_per_item) * quantity

        elif craft_type == "brew":
            level_data = BREW_TABLE.get((spell_level, has_concentration))
            if not level_data:
                raise ValueError(
                    f"No brew recipe found for spell level {spell_level} (concentration: {has_concentration})."
                )
            
            dt_per_item = level_data.get(tool_level_abbr)
            if dt_per_item is None:
                raise ValueError(
                    f"Your level {tool_level} is insufficient to brew a {spell_level}-level spell (concentration: {has_concentration})."
                )
            
            gp_cost = float(level_data["gp"]) * quantity + extra_cost
            dt_cost = float(dt_per_item) * quantity

        elif craft_type == "poison":
            clean_item = item_name.strip().lower()
            poison_data = POISON_TABLE.get(clean_item)
            if not poison_data:
                # Fallback to standard consumable calculation if item name is custom
                if rarity == "common":
                    gp_cost = 25.0 * quantity + extra_cost
                    dt_cost = {"journeyman": 1.0, "expert": 0.5, "master": 0.25}[tool_level] * quantity
                elif rarity == "uncommon":
                    gp_cost = 50.0 * quantity + extra_cost
                    dt_cost = {"expert": 1.0, "master": 0.5}[tool_level] * quantity
                elif rarity == "rare":
                    gp_cost = 200.0 * quantity + extra_cost
                    dt_cost = 1.0 * quantity
                elif rarity == "very rare":
                    gp_cost = 400.0 * quantity + extra_cost
                    dt_cost = 5.0 * quantity
                elif rarity == "legendary":
                    gp_cost = 1000.0 * quantity + extra_cost
                    dt_cost = 20.0 * quantity
                else:  # standard
                    gp_cost = (base_price / 2.0) * quantity + extra_cost
                    dt_div = {"journeyman": 25.0, "expert": 50.0, "master": 100.0}[tool_level]
                    dt_cost = (base_price / dt_div) * quantity
            else:
                dt_per_item = poison_data.get(tool_level_abbr)
                if dt_per_item is None:
                    raise ValueError(
                        f"Your level {tool_level} is insufficient to craft poison '{item_name}'."
                    )
                gp_cost = float(poison_data["gp"]) * quantity + extra_cost
                dt_cost = float(dt_per_item) * quantity

    # 7. Apply Herbalism Kit gather ingredients override: GP = 0, DT doubled
    if gather_ingredients:
        gp_cost = 0.0
        dt_cost = dt_cost * 2.0

    # 8. Override DT for masterpieces
    if is_masterpiece:
        dt_cost = 0.0

    # 9. Calculate CRP updates
    earned_crp = 0.0
    if not has_master_tool:
        if rarity == "common":
            if craft_type == "non-consumable":
                earned_crp = 2.5 * quantity
            else:
                # consumable, poison, brew, scroll, tattoo, meal
                earned_crp = 0.5 * quantity
        elif rarity == "uncommon":
            if craft_type == "non-consumable":
                earned_crp = 7.5 * quantity
            else:
                # consumable, poison, brew, scroll, tattoo, meal
                earned_crp = 1.5 * quantity

    return {
        "gp_cost": gp_cost,
        "moradinium_cost": moradinium_cost,
        "dt_cost": dt_cost,
        "is_legendary_project": is_legendary_project,
        "earned_crp": earned_crp
    }
