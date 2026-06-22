from __future__ import annotations
from typing import List, Tuple, Dict, Any
import re
import discord

class Skills:
    def __init__(self, crp=0, crafting=None, tool_proficiencies=None, languages=None, downtime_progress="-"):
        self.crp = crp
        self.crafting = crafting or []
        self.tool_proficiencies = tool_proficiencies or []
        self.languages = languages or []
        self.downtime_progress = downtime_progress

    def load_from_sheet_data(self, get_val):
        val = get_val('crp')
        raw_str = str(val).strip() if val is not None else ""
        if raw_str in ("", "-", "0"):
            self.crp = 0
        else:
            try:
                self.crp = int(float(raw_str.replace(",", ".")))
            except ValueError:
                self.crp = val

        skills_val = str(get_val('skills') or "")
        self.crafting = [s.strip() for s in skills_val.split(",") if s.strip()]
        prof_val = str(get_val('proficiencies') or "")
        self.tool_proficiencies = [p.strip() for p in prof_val.split(",") if p.strip()]
        lang_val = str(get_val('languages') or "")
        self.languages = [l.strip() for l in lang_val.split(",") if l.strip()]
        self.downtime_progress = str(get_val('downtime_progress') or "")

    def get_sheet_data(self) -> Dict[str, Any]:
        return {
            'crp': "-" if self.crp == 0 else self.crp,
            'skills': ", ".join(self.crafting),
            'proficiencies': ", ".join(self.tool_proficiencies),
            'languages': ", ".join(self.languages),
            'downtime_progress': self.downtime_progress
        }

    def get_summary(self) -> str:
        return f"**Crafting Reputation:** {self.crp}"

    def _clean_tool_name(self, name: str) -> str:
        """
        Extracts the first word of the tool name and strips any 's or ' suffix.
        e.g., "Leatherworker's Tools" -> "Leatherworker"
              "Thieves' Tools" -> "Thieves"
        """
        cleaned = name.strip()
        if not cleaned:
            return ""
        first_word = cleaned.split()[0]
        if first_word.endswith("'s") or first_word.endswith("’s"):
            return first_word[:-2]
        if first_word.endswith("'") or first_word.endswith("’"):
            return first_word[:-1]
        return first_word

    def _parse_item_level(self, item: str) -> Tuple[str, str | None]:
        """
        Parses a proficiency string to extract the tool name and level.
        Supports:
          - "Tool Name (level)" -> ("Tool Name", "level")
          - "Level Tool Name" -> ("Tool Name", "level")
        """
        item_str = item.strip()
        levels = ["journeyman", "expert", "master"]
        
        # 1. Try "Tool Name (level)"
        match_paren = re.match(r"^(.+?)\s*\((journeyman|expert|master)\)$", item_str, re.IGNORECASE)
        if match_paren:
            return match_paren.group(1).strip(), match_paren.group(2).lower()
            
        # 2. Try "Level Tool Name"
        levels_pattern = "|".join(levels)
        match_prefix = re.match(rf"^({levels_pattern})\s+(.+)$", item_str, re.IGNORECASE)
        if match_prefix:
            return match_prefix.group(2).strip(), match_prefix.group(1).lower()
            
        return item_str, None

    def get_current_tool_level(self, tool_name: str) -> str:
        """
        Inspects the character's crafting skills list and tool proficiencies list
        to find the current level of the tool.
        Returns:
            str or None: The level if found ('journeyman', 'expert', 'master'), else None.
        """
        clean_search = self._clean_tool_name(tool_name).lower()
        
        # Check crafting skills (Column X)
        for item in self.crafting:
            name, level = self._parse_item_level(item)
            if level:
                item_clean = self._clean_tool_name(name).lower()
                if item_clean == clean_search:
                    return level
        # Check tool proficiencies (Column Y)
        for item in self.tool_proficiencies:
            name, level = self._parse_item_level(item)
            if level:
                item_clean = self._clean_tool_name(name).lower()
                if item_clean == clean_search:
                    return level
        return None

    def learn_proficiency(self, actor, bot: discord.Client, ability_modifier: int, downtime: int, gp_cost_override: int = None,
                          tool: str = None, new_target: str = None, new_type: str = None,
                          roll_mode: str = "normal") -> Tuple[List[Dict[str, Any]], int, int, str, str]:
        """
        Deducts downtime and gold from the actor to make learning rolls toward a language or skill/tool proficiency.
        Updates the downtime progress, and moves the proficiency to crafting/proficiencies/languages if it reaches 100%.
        
        Returns:
            Tuple[List[Dict[str, Any]], int, int, str, str]: Roll details, total spent downtime, total spent gold, target name, and target level.
        """
        from helpers.utils import roll_dice

        # 1. Validation of inputs
        actor.resources.validate_downtime(downtime)

        # Parse the current progress list
        progress_str = self.downtime_progress.strip()
        projects = []
        if progress_str not in ("", "-", "None"):
            fragments = [f.strip() for f in progress_str.split(",") if f.strip()]
            for frag in fragments:
                pct_match = re.search(r"(\d+(?:\.\d+)?)%", frag)
                if not pct_match:
                    continue
                percent = float(pct_match.group(1))
                rest = frag.replace(pct_match.group(0), "").strip()
                
                known_levels = ["scroll proficiency", "weapon mastery", "martial weapon", "thieves tools", "gaming set", 
                                "journeyman", "expert", "master", "language", "instrument", "vehicle", "scroll"]
                level_found = None
                orig_level_found = ""
                
                paren_match = re.search(r"\(([^)]+)\)", rest)
                if paren_match:
                    level_cand = paren_match.group(1).strip()
                    level_found = level_cand.lower()
                    orig_level_found = level_cand
                    rest = rest.replace(paren_match.group(0), "").strip()
                else:
                    for kl in known_levels:
                        m = re.search(rf"\b{kl}\b", rest, re.IGNORECASE)
                        if m:
                            level_found = kl
                            orig_level_found = m.group(0)
                            rest = re.sub(rf"\b{kl}\b", "", rest, flags=re.IGNORECASE).strip()
                            break
                
                target_name = re.sub(r"\s+", " ", rest).strip()
                if not target_name:
                    target_name = orig_level_found
                    level_found = "language" if "scroll" not in target_name.lower() else "scroll"
                
                if not level_found:
                    level_found = "language"
                    orig_level_found = "language"
                
                projects.append({
                    "raw": frag,
                    "percent": percent,
                    "level": level_found,
                    "orig_level": orig_level_found,
                    "name": target_name
                })

        # 2. Select or Initialize project to promote
        selected_project = None
        selected_index = -1
        
        search_name = (tool or new_target)
        if search_name:
            search_name = search_name.strip()
            
        is_tool = False
        if tool:
            is_tool = True
        elif search_name and not new_type:
            is_tool = True

        clean_search = ""
        if search_name:
            if is_tool:
                clean_search = self._clean_tool_name(search_name).lower()
            else:
                clean_search = search_name.lower()

        if projects:
            if clean_search:
                for idx, proj in enumerate(projects):
                    proj_is_tool = proj["level"] in ("journeyman", "expert", "master")
                    if proj_is_tool:
                        proj_clean = self._clean_tool_name(proj["name"]).lower()
                    else:
                        proj_clean = proj["name"].lower()
                    
                    if proj_clean == clean_search:
                        selected_project = proj
                        selected_index = idx
                        break
            
            if not selected_project and not search_name:
                if len(projects) == 1:
                    selected_project = projects[0]
                    selected_index = 0
                else:
                    proj_names = [f"'{p['name']} ({p['level']})'" for p in projects]
                    raise ValueError(f"Multiple active learning projects found: {', '.join(proj_names)}. Please specify 'tool' or 'new_target' to choose which one to promote.")

        if not selected_project:
            if not search_name:
                raise ValueError("No active downtime progress. Please select a tool or specify a new target name to start learning.")
            
            if is_tool:
                cleaned_target = self._clean_tool_name(search_name)
                current_level = self.get_current_tool_level(cleaned_target)
                if current_level is None:
                    selected_level = "journeyman"
                elif current_level == "journeyman":
                    selected_level = "expert"
                elif current_level == "expert":
                    selected_level = "master"
                else:
                    raise ValueError(f"'{cleaned_target}' is already at master level.")
                target_name = cleaned_target
            else:
                if not new_type:
                    raise ValueError(f"Please select a type (language/instrument/etc.) to start learning '{search_name}'.")
                selected_level = new_type.strip().lower()
                target_name = search_name

            new_proj = {
                "raw": "",
                "percent": 0.0,
                "level": selected_level,
                "orig_level": selected_level,
                "name": target_name
            }
            projects.append(new_proj)
            selected_project = new_proj
            selected_index = len(projects) - 1

        # 3. Parse selected project details
        current_percent = selected_project["percent"]
        level = selected_project["level"]
        name = selected_project["name"]

        if level in ("journeyman", "expert", "master"):
            name = self._clean_tool_name(name)

        if current_percent >= 100:
            raise ValueError(f"Downtime progress for '{name}' is already at 100%.")

        # 4. Determine GP cost per roll
        if gp_cost_override is not None:
            gp_cost_per_roll = gp_cost_override
        else:
            gp_costs = {
                "journeyman": 0,
                "expert": 25,
                "master": 100,
                "language": 10,
                "instrument": 10,
                "gaming set": 10,
                "martial weapon": 20,
                "weapon mastery": 25,
                "vehicle": 0,
                "thieves tools": 50,
                "scroll": 50,
                "scroll proficiency": 50
            }
            if name.lower() in ("thieves", "scroll", "scroll proficiency"):
                gp_cost_per_roll = 50
            else:
                gp_cost_per_roll = gp_costs.get(level, 10)

        # 5. Perform rolls
        rolls_count = downtime // 5
        rolls_info = []
        total_spent_dt = 0
        total_spent_gp = 0

        for _ in range(rolls_count):
            try:
                actor.resources.deduct(gold=gp_cost_per_roll)
            except ValueError as e:
                if total_spent_dt == 0:
                    raise ValueError(f"Not enough gold to start learning. Requires {gp_cost_per_roll} GP per roll. Details: {e}")
                break

            results, total = roll_dice(bot, modifier=ability_modifier, roll_mode=roll_mode, actor_name=actor.name)
            is_nat_20 = (results[0] == 20)
            
            gained = max(0, total + (1 if is_nat_20 else 0))
            current_percent += gained
            total_spent_dt += 5
            total_spent_gp += gp_cost_per_roll

            rolls_info.append({
                "roll": results[0],
                "modifier": ability_modifier,
                "total": total,
                "nat_20": is_nat_20,
                "gained": gained,
                "new_percent": min(current_percent, 100)
            })

            if current_percent >= 100:
                current_percent = 100
                break

        actor.resources.downtime -= total_spent_dt

        # Update or clear project in the list
        if current_percent >= 100:
            projects.pop(selected_index)
            
            if level == "language":
                existing_lower = [lang.lower() for lang in self.languages]
                if name.lower() not in existing_lower:
                    self.languages.append(name)
            else:
                crafting_tools = {
                    "alchemist", "brewer", "calligrapher", "carpenter", "cartographer",
                    "cobbler", "cook", "glassblower", "herbalism", "jeweler",
                    "leatherworker", "mason", "painter", "poisoner", "potter",
                    "smith", "tinker", "weaver", "woodcarver"
                }
                full_names_map = {
                    "alchemist": "Alchemist's Supplies",
                    "brewer": "Brewer's Supplies",
                    "calligrapher": "Calligrapher's Supplies",
                    "carpenter": "Carpenter's Tools",
                    "cartographer": "Cartographer's Tools",
                    "cobbler": "Cobbler's Tools",
                    "cook": "Cook's Utensils",
                    "glassblower": "Glassblower's Tools",
                    "herbalism": "Herbalism Kit",
                    "jeweler": "Jeweler's Tools",
                    "leatherworker": "Leatherworker's Tools",
                    "mason": "Mason's Tools",
                    "painter": "Painter's Supplies",
                    "poisoner": "Poisoner's Kit",
                    "potter": "Potter's Tools",
                    "smith": "Smith's Tools",
                    "tinker": "Tinker's Tools",
                    "weaver": "Weaver's Tools",
                    "woodcarver": "Woodcarver's Tools",
                    "disguise": "Disguise Kit",
                    "forgery": "Forgery Kit",
                    "thieves": "Thieves' Tools",
                    "scroll": "Scrolls",
                    "scroll proficiency": "Scrolls"
                }
                full_name = full_names_map.get(name.lower(), name)

                if name.lower() in crafting_tools:
                    new_entry_x = f"{name} ({level})"
                    cleaned_crafting = []
                    for item in self.crafting:
                        parsed_name, parsed_level = self._parse_item_level(item)
                        if self._clean_tool_name(parsed_name).lower() == name.lower():
                            continue
                        cleaned_crafting.append(item)
                    cleaned_crafting.append(new_entry_x)
                    self.crafting = cleaned_crafting

                    cleaned_profs = []
                    for item in self.tool_proficiencies:
                        parsed_name, parsed_level = self._parse_item_level(item)
                        if self._clean_tool_name(parsed_name).lower() == name.lower():
                            continue
                        cleaned_profs.append(item)
                    cleaned_profs.append(full_name)
                    self.tool_proficiencies = cleaned_profs
                else:
                    new_entry_y = f"{full_name} ({level})"
                    cleaned_profs = []
                    for item in self.tool_proficiencies:
                        parsed_name, parsed_level = self._parse_item_level(item)
                        if self._clean_tool_name(parsed_name).lower() == name.lower():
                            continue
                        cleaned_profs.append(item)
                    cleaned_profs.append(new_entry_y)
                    self.tool_proficiencies = cleaned_profs
        else:
            orig_level = selected_project["orig_level"]
            pct_str = str(int(current_percent)) if current_percent == int(current_percent) else str(current_percent)
            selected_project["raw"] = f"{pct_str}% ({orig_level}) {name}"
            selected_project["percent"] = current_percent

        if projects:
            formatted_list = []
            for p in projects:
                if p["raw"]:
                    formatted_list.append(p["raw"])
                else:
                    pct_str = str(int(p["percent"])) if p["percent"] == int(p["percent"]) else str(p["percent"])
                    formatted_list.append(f"{pct_str}% ({p['orig_level']}) {p['name']}")
            self.downtime_progress = ", ".join(formatted_list)
        else:
            self.downtime_progress = "-"

        return rolls_info, total_spent_dt, total_spent_gp, name, level
