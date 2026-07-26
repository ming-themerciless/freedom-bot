from __future__ import annotations
import re
from typing import Dict, List

class Item:
    def __init__(self, name="", description="", benefits="", link="", rarity="common"):
        self.name = name
        self.description = description
        self.benefits = benefits
        self.link = link
        self.rarity = rarity

    def get_summary(self) -> str:
        return (f"**Item:** {self.name}\n"
                f"**Description:** {self.description}\n"
                f"**Benefits:** {self.benefits}\n"
                f"**Link:** {self.link}")

    @staticmethod
    def parse_notable_items(raw_str: str) -> List[Item]:
        """
        Parses a string of notable items into a list of Item objects.
        """
        categories = {
            "legendary": [],
            "very rare": [],
            "rare": [],
            "uncommon": [],
            "common": []
        }
        
        if not raw_str or raw_str.strip() in ("", "-", "None"):
            return []

        lines = [line.strip() for line in raw_str.split("\n") if line.strip()]
        
        for line in lines:
            matched_prefix = None
            for cat in categories.keys():
                prefix = cat.title() + ":"
                if line.lower().startswith(cat + ":") or line.startswith(prefix):
                    matched_prefix = cat
                    line = line[len(prefix):].strip()
                    break
            
            items = [it.strip() for it in line.split(",") if it.strip()]
            
            for item in items:
                if matched_prefix:
                    categories[matched_prefix].append(item)
                else:
                    match = re.search(r"\((legendary|very rare|rare|uncommon|common)\)$", item, re.IGNORECASE)
                    if match:
                        rarity_suffix = match.group(1).lower()
                        clean_name = item[:match.start()].strip()
                        categories[rarity_suffix].append(clean_name)
                    else:
                        categories["common"].append(item)
                        
        item_list = []
        for rarity, names in categories.items():
            for name in names:
                item_list.append(Item(name=name, rarity=rarity))
                
        return item_list

    @staticmethod
    def serialize_notable_items(item_list: List[Item]) -> str:
        """
        Serializes a list of Item objects into a sorted multiline string.
        """
        categories = {
            "legendary": [],
            "very rare": [],
            "rare": [],
            "uncommon": [],
            "common": []
        }
        for item in item_list:
            r = item.rarity.lower() if item.rarity else "common"
            if r in categories:
                categories[r].append(item.name)
            else:
                categories["common"].append(item.name)
                
        order = ["legendary", "very rare", "rare", "uncommon", "common"]
        lines = []
        for cat in order:
            names = categories[cat]
            if names:
                lines.append(f"{cat.title()}: {', '.join(names)}")
                
        return "\n".join(lines) if lines else "-"
