from __future__ import annotations
from typing import List, Tuple, Dict, Any
import math
import re
import discord

class Skills:
    # Homebrew rules 6.3.3.1 (PDF p.17): a master only takes a student on after
    # they have accumulated 100 crafting reputation points with that tool.
    MASTER_CRP_REQUIREMENT = 100

    # One column W fragment, in either accepted notation:
    #   canonical, confirmed by the maintainer 2026-07-30 -- "7.5 (Brewer)",
    #     amount first, tool in parentheses;
    #   legacy, the form the bot itself used to write   -- "Brewer: 7.5".
    # Both coexist in the live sheet by design (OD-34, 2026-07-30). The amount may
    # use a comma as its decimal separator, so fragments are matched by pattern
    # rather than by splitting the cell on commas.
    _CRP_FRAGMENT_RE = re.compile(
        r"(?P<amount>\d+(?:[.,]\d+)?)\s*\(\s*(?P<tool>[^)]+?)\s*\)"
        r"|(?P<legacy_tool>[^,;:()]+?)\s*:\s*(?P<legacy_amount>\d+(?:[.,]\d+)?)"
    )

    # Everything a cell may contain *between* fragments. A per-tool list is only
    # accepted when every character outside the matched fragments is one of these,
    # because a partial read is destructive: "7.5 (Brewer), BROKEN" read as
    # {"brewer": 7.5} is rewritten by the next /craft as a cell that no longer
    # contains "BROKEN" (sheet-inventory.md 3.2, F-S3a).
    _CRP_SEPARATOR_RE = re.compile(r"^[\s,;]*$")

    # The literal the sheet holds once a tool reaches Master rank. Further CRP
    # can never be spent (one Master rank for life, rules 6.3.3.1 p.17), so no
    # running total is kept -- see OD-29.
    _CRP_MASTERED = "master"

    def __init__(self, crp=0, crafting=None, tool_proficiencies=None, languages=None, downtime_progress="-"):
        self.crp = crp
        self.crp_dict: Dict[str, float | int] = {}
        # Dictionaries instead of lists of strings
        self.crafting: Dict[str, str] = {}
        self.tool_proficiencies: Dict[str, str | None] = {}
        self.languages: Dict[str, bool] = {}
        self.downtime_progress: Dict[str, Dict[str, Any]] = {}
        self.crp_modified = False
        self._crp_unparsed = False

    def load_from_sheet_data(self, get_val):
        # 1. Crafting Reputation
        val = get_val('crp')
        raw_str = str(val).strip() if val is not None else ""
        self.crp_dict = {}
        self.crp_modified = False
        self._crp_unparsed = False
        if raw_str in ("", "-", "0"):
            self.crp = 0
        elif raw_str.lower() == self._CRP_MASTERED:
            # A mastered tool. No per-tool total is kept or expected.
            self.crp = raw_str
        else:
            per_tool = self._parse_crp_cell(raw_str)
            if per_tool is not None:
                # A per-tool list, every fragment of it understood.
                self.crp_dict = per_tool
                self.crp = raw_str
            else:
                try:
                    f_val = float(raw_str.replace(",", "."))
                    self.crp = int(f_val) if f_val.is_integer() else f_val
                    self.crp_dict["general"] = self.crp
                except ValueError:
                    # Not a per-tool list, not a bare total, not the mastered
                    # literal. The raw value is kept verbatim and column W is
                    # pinned read-only until a maintainer reconciles it, so that
                    # nothing already in the cell can be overwritten by a value
                    # derived from a parse that did not understand it.
                    self.crp = val
                    self._crp_unparsed = True

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

        if self.crp_modified and not self._crp_unparsed:
            # 1. CRP list, written back in the sheet's own canonical form
            #    ("7.5 (Brewer)") so a save never rewrites the maintainer's
            #    convention into the legacy "Brewer: 7.5" one.
            #
            #    A cell the parser could not read in full is never written: it is
            #    omitted from the returned data, so the adapter leaves the
            #    existing cell untouched. add_tool_crp() refuses such a cell
            #    outright; this is the second line of defence, for any caller that
            #    sets crp_modified by hand.
            if self.crp_dict:
                if len(self.crp_dict) == 1 and "general" in self.crp_dict:
                    crp_val = self.crp_dict["general"]
                else:
                    crp_val = ", ".join(
                        f"{v:g} ({t.capitalize()})" for t, v in self.crp_dict.items()
                    )
            else:
                crp_val = "-" if self.crp == 0 else self.crp
            data['crp'] = crp_val

        return data

    def get_summary(self) -> str:
        if self._crp_unparsed:
            # Show the stored text as it stands rather than a number derived from
            # a parse that failed, and say so, so the row can be reconciled.
            return (
                f"**Crafting Reputation:** {self.crp} "
                "*(unreadable format -- ask the Guild Council to correct it)*"
            )
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
        fw_lower = first_word.lower()
        if fw_lower in ("herbalist", "herbalism"):
            return "Herbalism"
        if fw_lower in ("forger", "forgery"):
            return "Forgery"
        if fw_lower in ("thief", "thieves"):
            return "Thieves"
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

    def _parse_crp_cell(self, raw_str: str) -> Dict[str, float | int] | None:
        """Read a per-tool CRP cell, or return None if any of it is unrecognised.

        All or nothing by design. A cell is a per-tool list only when every
        fragment parses *and* nothing but separators sits between the fragments,
        because the parsed dictionary is what a later save writes back over the
        whole cell: accepting "7.5 (Brewer), BROKEN" as {"brewer": 7.5} would let
        the next /craft rewrite the cell without "BROKEN" in it. Returning None
        keeps the raw value and leaves column W read-only instead.

        Two fragments naming the same tool are **summed**, not overwritten. The
        key is the tool name case-folded, so "2.5 (Smith), 2.5 (SMITH)" is one
        tool holding 5 -- assigning each fragment straight into the dictionary
        dropped the earlier value and the next save wrote the survivor back over
        the whole cell, which is the same all-or-nothing violation in miniature.
        Consolidation is safe here because case is the only difference between the
        two names, so there is nothing to interpret. The first spelling seen keeps
        both the entry and its position, so the cell serialises deterministically.

        Names that differ by more than case stay separate. Merging them would mean
        applying _clean_tool_name()'s tool-to-artisan bridge to decide identity at
        read time, and that bridge collapses a name to its first word -- it merges
        anything sharing one, including a non-canonical spelling nobody has
        validated. Column W is free text, so OD-06's rule is that an unrecognised
        artisan must fail loudly at import rather than be guessed at; a silent
        read-time merge is exactly the guess it forbids. add_tool_crp() applies the
        bridge deliberately, and only when CRP is actually awarded for that tool.
        """
        parsed: Dict[str, float | int] = {}
        position = 0
        for match in self._CRP_FRAGMENT_RE.finditer(raw_str):
            if not self._CRP_SEPARATOR_RE.match(raw_str[position:match.start()]):
                return None
            position = match.end()

            amount, tool = match.group("amount"), match.group("tool")
            if amount is None:
                amount, tool = match.group("legacy_amount"), match.group("legacy_tool")
            tool_key = tool.strip().lower()
            if not tool_key:
                return None
            # The pattern only admits digits with one optional [.,] group, so the
            # conversion cannot fail once the fragment has matched. It can still
            # overflow to infinity on a long enough digit run, on its own or once
            # a duplicate is added to it; such a cell is unreadable rather than
            # worth writing an infinite total back over.
            value = float(amount.replace(",", "."))
            previous = parsed.get(tool_key)
            if previous is not None:
                value += float(previous)
            if not math.isfinite(value):
                return None
            parsed[tool_key] = int(value) if value.is_integer() else value

        if not parsed or not self._CRP_SEPARATOR_RE.match(raw_str[position:]):
            return None
        return parsed

    @property
    def crp_unparsed(self) -> bool:
        """True when column W held something this class could not read in full.

        Callers must not record crafting reputation against such a row: the raw
        cell is preserved and needs maintainer reconciliation first.
        """
        return self._crp_unparsed

    def _is_mastered(self) -> bool:
        """True when column W holds the terminal "Master" literal (OD-29)."""
        return isinstance(self.crp, str) and self.crp.strip().lower() == self._CRP_MASTERED

    def can_record_tool_crp(self) -> bool:
        """True when earned crafting reputation can be added safely.

        False for a cell that could not be parsed in full, and for a mastered
        character, whose cell holds "Master" rather than a total and must not be
        replaced by one (rules 6.3.3.1 p.17: one Master rank for life, so further
        reputation can never be spent).
        """
        return not self._crp_unparsed and not self._is_mastered()

    def add_tool_crp(self, tool_name: str, amount: float) -> float:
        """Add earned crafting reputation to one tool; return its new total.

        The tool is identified with the same normalisation get_tool_crp() uses, so
        an award lands on the entry the Master gate will later read instead of
        creating a second spelling of the same tool. Without this, "2.5 (Smith's
        Tools)" plus an award for "Smith's Tools" produced
        "2.5 (Smith's tools), 2.5 (Smith)" and the gate saw only half the total.
        Any duplicate spellings already in the cell are folded into one entry.
        """
        try:
            earned = float(amount)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Crafting reputation must be a number, got {amount!r}.") from exc
        if not math.isfinite(earned) or earned < 0:
            raise ValueError(f"Crafting reputation must be finite and non-negative, got {amount!r}.")

        clean_search = self._clean_tool_name(tool_name).lower()
        if not clean_search:
            raise ValueError("A tool name is required to record crafting reputation.")
        if not self.can_record_tool_crp():
            raise ValueError(
                f"Crafting reputation cannot be recorded for '{tool_name}': the stored value "
                f"{self.crp!r} must be reconciled first."
            )
        if earned == 0:
            # Nothing to record, and no reason to rewrite the cell.
            return self.get_tool_crp(tool_name)

        equivalent = self._equivalent_crp_keys(clean_search)
        # Refuse before mutating anything, so a value that cannot be read is
        # never replaced by one that ignores it.
        total = self._sum_crp_entries(equivalent) + earned

        target_key = equivalent[0] if equivalent else clean_search
        for duplicate in equivalent[1:]:
            del self.crp_dict[duplicate]
        self.crp_dict[target_key] = int(total) if total.is_integer() else total
        self.crp_modified = True
        return total

    def _equivalent_crp_keys(self, clean_search: str) -> List[str]:
        """Every column-W entry that names the tool `clean_search` identifies.

        One place decides which stored entries belong to a tool, so a read and a
        write can never disagree about that set. They did: get_tool_crp()
        returned the first match while add_tool_crp() summed them all, so a cell
        holding "60 (Herbalist), 50 (Herbalism)" read as 60 and became 111 when
        one point was earned (PR-20260910-R2-1). The alias table makes those two
        spellings one tool, and one tool holds one total.

        The identity rule is _clean_tool_name()'s, which both callers already
        used for lookup, so this widens nothing: it is the existing bridge
        applied consistently rather than a new one. Entry keys are left alone --
        this is a read, and OD-06 keeps free-text column W unmerged on disk until
        reputation is actually awarded for the tool.
        """
        return [
            key
            for key in self.crp_dict
            if self._clean_tool_name(key).lower() == clean_search
        ]

    def _sum_crp_entries(self, keys: List[str]) -> float:
        """Total the given column-W entries, refusing any value that is not one.

        Raises ValueError rather than skipping an unreadable entry, so no caller
        can produce a total that quietly omits reputation the character earned.
        get_tool_crp() catches it and reports 0.0, which is what a single
        unreadable entry has always read as.
        """
        total = 0.0
        for key in keys:
            value = self.crp_dict[key]
            try:
                total += float(value)
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    f"Existing crafting reputation for '{key}' is not a number: {value!r}."
                ) from exc
        return total

    def get_tool_crp(self, tool_name: str) -> float:
        """Return the crafting reputation accumulated for one tool.

        Every equivalent entry counts, because add_tool_crp() folds every
        equivalent entry into the total it writes. The read is pure: nothing is
        consolidated, renamed or persisted here, and crp_modified is untouched.
        """
        clean_search = self._clean_tool_name(tool_name).lower()
        equivalent = self._equivalent_crp_keys(clean_search)
        if equivalent:
            try:
                return self._sum_crp_entries(equivalent)
            except ValueError:
                return 0.0
        # Sheets predating per-tool tracking hold a single untagged total, which
        # records no tool. Returning it for any requested tool preserves the
        # behaviour those characters have today, but rules 6.3.3.1 (PDF p.17)
        # require the 100 points to be earned "with that tool" -- so this can
        # satisfy the Master gate for a tool the character never used.
        #
        # RULED 2026-07-30, docs/discovery/open-decisions.md OD-34: untagged CRP
        # is resolved once by hand at import, not by a code policy, so this
        # branch stays as it is and the Phase 2 importer reports any bare-number
        # cell for that one-time assignment. Do not tighten it here; a Master
        # rank is granted once for life and cannot be taken back by a later
        # correction.
        if list(self.crp_dict) == ["general"]:
            try:
                return float(self.crp_dict["general"])
            except (TypeError, ValueError):
                return 0.0
        return 0.0

    def _find_other_master_tool(self, target_name: str) -> str | None:
        """Return the name of a mastered tool other than the target, if any."""
        clean_target = self._clean_tool_name(target_name).lower()
        for source in (self.crafting, self.tool_proficiencies):
            for name, level in source.items():
                if level != "master":
                    continue
                if self._clean_tool_name(name).lower() != clean_target:
                    return name
        return None

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
                        other_master = self._find_other_master_tool(cleaned_target)
                        if other_master:
                            raise ValueError(
                                f"You can only become a Master in one artisan's tool. "
                                f"You are already a Master in '{other_master}'."
                            )
                        earned_crp = self.get_tool_crp(cleaned_target)
                        if earned_crp < self.MASTER_CRP_REQUIREMENT:
                            raise ValueError(
                                f"A master will only take you on once you have earned "
                                f"{self.MASTER_CRP_REQUIREMENT} crafting reputation points with "
                                f"'{cleaned_target}'. Current reputation: {earned_crp:g}."
                            )
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
            other_master_name = self._find_other_master_tool(name)
            if other_master_name:
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
                # Reaching Master rank replaces the whole cell with the terminal
                # literal, deliberately and independently of what it held before,
                # so the read-only pin on an unparsed cell is lifted here. That
                # this discards any per-tool total is a known data-model defect
                # recorded for Phase 5 (phase-0-handoff.md, deliberately
                # incomplete); it is not changed by this fix.
                self.crp = "Master"
                self.crp_dict = {}
                self._crp_unparsed = False
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
