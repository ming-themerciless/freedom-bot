from __future__ import annotations
from typing import List, Tuple, Dict, Any
import re
import discord

class Skills:
    def __init__(self, crp=0, crafting=None, tool_proficiencies=None, languages=None, downtime_progress="-"):
        self.crp = crp
        self.crp_dict: Dict[str, float | int] = {}
        # Dictionaries instead of lists of strings
        self.crafting: Dict[str, str] = {}
        self.tool_proficiencies: Dict[str, str | None] = {}
        self.languages: Dict[str, bool] = {}
        self.downtime_progress: Dict[str, Dict[str, Any]] = {}
        self.crp_modified = False

    def load_from_sheet_data(self, get_val):
        # 1. Crafting Reputation
        val = get_val('crp')
        raw_str = str(val).strip() if val is not None else ""
        self.crp_dict = {}
        self.crp_modified = False
        if raw_str in ("", "-", "0"):
            self.crp = 0
        else:
            if ":" in raw_str:
                parts = [p.strip() for p in raw_str.split(",") if p.strip()]
                for part in parts:
                    if ":" in part:
                        t_name, t_val = part.split(":", 1)
                        t_name = t_name.strip()
                        try:
                            f_val = float(t_val.strip().replace(",", "."))
                            self.crp_dict[t_name.lower()] = int(f_val) if f_val.is_integer() else f_val
                        except ValueError:
                            pass
                self.crp = raw_str
            else:
                try:
                    f_val = float(raw_str.replace(",", "."))
                    self.crp = int(f_val) if f_val.is_integer() else f_val
                    self.crp_dict["general"] = self.crp
                except ValueError:
                    self.crp = val

        # 2. Crafting Skills (Column X): e.g. "Expert Smith, Journeyman Alchemist"
        skills_val = str(get_val('skills') or "")
        self.crafting = {}
        for s in re.split(r"[,;.]\s*", skills_val):
            s = s.strip()
            if not s:
                continue
            name, level = self._parse_item_level(s)
            self.crafting[name] = level or "journeyman"

        # 3. Tool Proficiencies (Column Y): e.g. "Smith's Tools (expert), Dice Set"
        prof_val = str(get_val('proficiencies') or "")
        self.tool_proficiencies = {}
        for p in re.split(r"[,;.]\s*", prof_val):
            p = p.strip()
            if not p:
                continue
            name, level = self._parse_item_level(p)
            self.tool_proficiencies[name] = level

        # 4. Languages (Column Z): e.g. "Common, Elvish"
        lang_val = str(get_val('languages') or "")
        self.languages = {}
        for l in lang_val.split(","):
            l = l.strip()
            if not l:
                continue
            self.languages[l] = True

        # 5. Downtime Progress (Column V): e.g. "45% (master) smith"
        progress_str = str(get_val('downtime_progress') or "").strip()
        self.downtime_progress = {}
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

                # Normalize scroll names and levels
                if target_name.lower() in ("scrolls", "scroll", "scroll proficiency"):
                    target_name = "Scroll"
                    if level_found in ("scroll", "scroll proficiency", "language", "journeyman", "expert", "master"):
                        level_found = "scroll"
                        orig_level_found = "scroll"

                target_key = target_name.lower()
                if target_key in self.downtime_progress:
                    # Merge percent by summing them (up to 100%) to heal split progress from the bug
                    existing_proj = self.downtime_progress[target_key]
                    new_percent = min(existing_proj["percent"] + percent, 100.0)
                    existing_proj["percent"] = new_percent
                    # Keep the higher level or the current level
                    if existing_proj["level"] in ("scroll", "scroll proficiency", "language") and level_found not in ("scroll", "scroll proficiency", "language"):
                        existing_proj["level"] = level_found
                        existing_proj["orig_level"] = orig_level_found
                    # Update raw representation
                    orig_lvl = existing_proj["orig_level"]
                    pct_str = str(int(new_percent)) if new_percent.is_integer() else f"{new_percent:.1f}"
                    if orig_lvl == "scroll":
                        existing_proj["raw"] = f"{pct_str}% Scrolls"
                    else:
                        existing_proj["raw"] = f"{pct_str}% ({orig_lvl}) {existing_proj['name']}"
                else:
                    self.downtime_progress[target_key] = {
                        "percent": percent,
                        "level": level_found,
                        "orig_level": orig_level_found,
                        "name": target_name,
                        "raw": frag
                    }

    def get_sheet_data(self) -> Dict[str, Any]:
        # 2. Crafting Skills
        skills_str = ", ".join(f"{lvl.capitalize()} {name}" for name, lvl in self.crafting.items())
        
        # 3. Tool Proficiencies
        profs_str = ", ".join(f"{name} ({lvl})" if lvl and lvl != "scroll" else name for name, lvl in self.tool_proficiencies.items())
        
        # 4. Languages
        langs_str = ", ".join(self.languages.keys())
        
        # 5. Downtime Progress
        progress_parts = []
        for proj in self.downtime_progress.values():
            pct = proj["percent"]
            pct_str = str(int(pct)) if pct.is_integer() else f"{pct:.1f}"
            if proj["level"] == "scroll":
                progress_parts.append(f"{pct_str}% Scrolls")
            else:
                progress_parts.append(f"{pct_str}% ({proj['orig_level']}) {proj['name']}")
        progress_str = ", ".join(progress_parts) if progress_parts else "-"

        data = {
            'skills': skills_str if skills_str else "-",
            'proficiencies': profs_str if profs_str else "-",
            'languages': langs_str if langs_str else "-",
            'downtime_progress': progress_str
        }

        if self.crp_modified:
            # 1. CRP list
            if self.crp_dict:
                if len(self.crp_dict) == 1 and "general" in self.crp_dict:
                    crp_val = self.crp_dict["general"]
                else:
                    crp_val = ", ".join(f"{t.capitalize()}: {v}" for t, v in self.crp_dict.items())
            else:
                crp_val = "-" if self.crp == 0 else self.crp
            data['crp'] = crp_val

        return data

    def get_summary(self) -> str:
        if not self.crp_dict:
            return f"**Crafting Reputation:** {self.crp}"
        if len(self.crp_dict) == 1 and "general" in self.crp_dict:
            return f"**Crafting Reputation:** {self.crp_dict['general']}"
        parts = [f"{t.capitalize()}: {v}" for t, v in self.crp_dict.items()]
        return f"**Crafting Reputation:** {', '.join(parts)}"

    def _clean_tool_name(self, name: str) -> str:
        cleaned = name.strip()
        if not cleaned:
            return ""
        if cleaned.lower() in ("scrolls", "scroll", "scroll proficiency"):
            return "Scroll"
        first_word = cleaned.split()[0].rstrip(".,;:")
        if first_word.endswith("'s") or first_word.endswith("’s"):
            return first_word[:-2]
        if first_word.endswith("'") or first_word.endswith("’"):
            return first_word[:-1]
        return first_word

    def _parse_item_level(self, item: str) -> Tuple[str, str | None]:
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

    def get_current_tool_level(self, tool_name: str) -> str | None:
        clean_search = self._clean_tool_name(tool_name).lower()
        
        # Check crafting skills
        for name, level in self.crafting.items():
            if self._clean_tool_name(name).lower() == clean_search:
                return level
        # Check tool proficiencies
        for name, level in self.tool_proficiencies.items():
            if self._clean_tool_name(name).lower() == clean_search:
                if level:
                    return level
                return "scroll" if clean_search == "scroll" else "journeyman"
        return None

    def learn_proficiency(self, actor, bot: discord.Client, ability_modifier: int, downtime: int, gp_cost_override: int = None,
                          tool: str = None, new_target: str = None, new_type: str = None,
                          roll_mode: str = "normal") -> Tuple[List[Dict[str, Any]], int, int, str, str]:
        from helpers.utils import roll_dice

        # 1. Validation of inputs
        actor.resources.validate_downtime(downtime)

        # 2. Select or Initialize project to promote
        selected_project = None
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

        if self.downtime_progress:
            if clean_search:
                selected_project = self.downtime_progress.get(clean_search)
                if not selected_project:
                    for key, proj in self.downtime_progress.items():
                        proj_is_tool = proj["level"] in ("journeyman", "expert", "master")
                        proj_clean = self._clean_tool_name(proj["name"]).lower() if proj_is_tool else proj["name"].lower()
                        if proj_clean == clean_search:
                            selected_project = proj
                            break
            else:
                if len(self.downtime_progress) == 1:
                    selected_project = list(self.downtime_progress.values())[0]
                else:
                    proj_names = [f"'{p['name']} ({p['level']})'" for p in self.downtime_progress.values()]
                    raise ValueError(f"Multiple active learning projects found: {', '.join(proj_names)}. Please specify 'tool' or 'new_target' to choose which one to promote.")

        if not selected_project:
            if not search_name:
                raise ValueError("No active downtime progress. Please select a tool or specify a new target name to start learning.")
            
            if is_tool:
                cleaned_target = self._clean_tool_name(search_name)
                current_level = self.get_current_tool_level(cleaned_target)
                if cleaned_target.lower() == "scroll":
                    if current_level is not None:
                        raise ValueError("You already have Scroll Proficiency.")
                    selected_level = "scroll"
                else:
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

            selected_project = {
                "percent": 0.0,
                "level": selected_level,
                "orig_level": selected_level,
                "name": target_name,
                "raw": ""
            }
            self.downtime_progress[target_name.lower()] = selected_project

        # 3. Parse selected project details
        current_percent = selected_project["percent"]
        level = selected_project["level"]
        name = selected_project["name"]

        if level in ("journeyman", "expert", "master"):
            name = self._clean_tool_name(name)

        # Enforce the one-Master-tool limit
        if level == "master":
            cleaned_target = self._clean_tool_name(name).lower()
            has_other_master = False
            other_master_name = None
            for p_name, p_lvl in self.crafting.items():
                if p_lvl == "master":
                    p_clean = self._clean_tool_name(p_name).lower()
                    if p_clean != cleaned_target:
                        has_other_master = True
                        other_master_name = p_name
                        break
            if not has_other_master:
                for p_name, p_lvl in self.tool_proficiencies.items():
                    if p_lvl == "master":
                        p_clean = self._clean_tool_name(p_name).lower()
                        if p_clean != cleaned_target:
                            has_other_master = True
                            other_master_name = p_name
                            break
            if has_other_master:
                raise ValueError(f"You can only become a Master in one artisan's tool. You are already a Master in '{other_master_name}'.")

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
        selected_project["percent"] = current_percent
        if current_percent >= 100:
            self.downtime_progress.pop(name.lower(), None)
            
            if level == "master":
                self.crp = "Master"
                self.crp_dict = {}
                self.crp_modified = True

            if level == "language":
                self.languages[name] = True
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
                    clean_target = name.lower()
                    to_remove = [k for k in self.crafting.keys() if self._clean_tool_name(k).lower() == clean_target]
                    for k in to_remove:
                        self.crafting.pop(k)
                    self.crafting[name] = level

                    to_remove_prof = [k for k in self.tool_proficiencies.keys() if self._clean_tool_name(k).lower() == clean_target]
                    for k in to_remove_prof:
                        self.tool_proficiencies.pop(k)
                    self.tool_proficiencies[full_name] = None
                else:
                    clean_target = name.lower()
                    to_remove_prof = [k for k in self.tool_proficiencies.keys() if self._clean_tool_name(k).lower() == clean_target]
                    for k in to_remove_prof:
                        self.tool_proficiencies.pop(k)
                    self.tool_proficiencies[full_name] = level
        else:
            orig_level = selected_project["orig_level"]
            pct_str = str(int(current_percent)) if current_percent == int(current_percent) else str(current_percent)
            if orig_level == "scroll":
                selected_project["raw"] = f"{pct_str}% Scrolls"
            else:
                selected_project["raw"] = f"{pct_str}% ({orig_level}) {name}"

        return rolls_info, total_spent_dt, total_spent_gp, name, level
