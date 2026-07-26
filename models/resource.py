from __future__ import annotations
from helpers.utils import to_currency, roll_dice
from models.money import Money
from typing import List, Tuple
import discord

class Resource:
    def __init__(self, downtime=0, platinum=0, gold=0, silver=0, copper=0, moradinium=0):
        self.downtime = downtime
        self.platinum = platinum
        self.gold = gold
        self.silver = silver
        self.copper = copper
        self.moradinium = moradinium

    def load_from_sheet_data(self, get_val):
        from helpers.utils import safe_int, safe_number
        self.downtime = safe_number(get_val('downtime'), default=0.0)
        self.platinum = safe_int(get_val('platinum'), default=0)
        self.gold = safe_int(get_val('gold'), default=0)
        self.silver = safe_int(get_val('silver'), default=0)
        self.copper = safe_int(get_val('copper'), default=0)
        self.moradinium = safe_int(get_val('moradinium'), default=0)

    def get_sheet_data(self) -> dict[str, any]:
        return {
            'downtime': self.downtime,
            'platinum': self.platinum,
            'gold': self.gold,
            'silver': self.silver,
            'copper': self.copper,
            'moradinium': self.moradinium
        }

    def validate_downtime(self, downtime: int):
        if downtime < 5 or downtime % 5 != 0:
            raise ValueError("Downtime must be spent in increments of five days.")
        if downtime > self.downtime:
            raise ValueError(f"Not enough downtime available: {self.downtime} days.")

    def get_summary(self, include_money=True, include_moradinium=True, include_downtime=False) -> str:
        parts = []
        if include_money:
            money = []
            if self.platinum > 0: money.append(f"{self.platinum}pp")
            if self.gold > 0:     money.append(f"{self.gold}gp")
            if self.silver > 0:   money.append(f"{self.silver}sp")
            if self.copper > 0:   money.append(f"{self.copper}cp")
            if money:
                parts.append("**Money:** " + ", ".join(money))
        if include_moradinium:
            parts.append(f"**Moradinium:** {self.moradinium}")
        if include_downtime:
            parts.append(f"**Downtime:** {self.downtime} days")
        return "\n".join(parts) if parts else "*No relevant resources.*"

    def format_coins(self) -> str:
        parts = []
        if self.platinum:   parts.append(f"{self.platinum}pp")
        if self.gold:       parts.append(f"{self.gold}gp")
        if self.silver:     parts.append(f"{self.silver}sp")
        if self.copper:     parts.append(f"{self.copper}cp")
        if self.moradinium: parts.append(f"{self.moradinium} Moradinium")
        return ", ".join(parts) or "nothing"

    def deduct(self, platinum=0, gold=0, silver=0, copper=0, moradinium=0):
        if any(amount < 0 for amount in (platinum, gold, silver, copper)):
            raise ValueError("Currency deductions cannot be negative.")
        if moradinium > self.moradinium:
            raise ValueError("Not enough Moradinium to pay.")
        wallet = {"pp": self.platinum, "gp": self.gold, "sp": self.silver, "cp": self.copper}
        required = {"pp": platinum, "gp": gold, "sp": silver, "cp": copper}
        rates = {"pp": 10, "gp": 10, "sp": 10}
        order = ["cp", "sp", "gp", "pp"]

        def ensure_funds(curr, amount):
            if wallet[curr] >= amount:
                return True
            if curr == "pp":
                return False
            idx = order.index(curr)
            bigger = order[idx + 1]
            needed = amount - wallet[curr]
            rate = rates[bigger]
            needed_bigger = (needed // rate) + (1 if needed % rate else 0)
            if ensure_funds(bigger, needed_bigger):
                wallet[bigger] -= needed_bigger
                wallet[curr] += needed_bigger * rate
                return True
            return False

        for curr in order:
            if required[curr] > wallet[curr]:
                if not ensure_funds(curr, required[curr]):
                    raise ValueError(f"Not enough currency to deduct {required[curr]} {curr}.")
            wallet[curr] -= required[curr]

        self.copper = wallet["cp"]
        self.silver = wallet["sp"]
        self.gold = wallet["gp"]
        self.platinum = wallet["pp"]
        self.moradinium -= moradinium

    def add(self, platinum=0, gold=0, silver=0, copper=0, moradinium=0):
        if self.platinum + platinum < 0: raise ValueError("Resulting platinum cannot be negative.")
        if self.gold + gold < 0: raise ValueError("Resulting gold cannot be negative.")
        if self.silver + silver < 0: raise ValueError("Resulting silver cannot be negative.")
        if self.copper + copper < 0: raise ValueError("Resulting copper cannot be negative.")
        if self.moradinium + moradinium < 0: raise ValueError("Resulting Moradinium cannot be negative.")

        self.platinum += platinum
        self.gold += gold
        self.silver += silver
        self.copper += copper
        self.moradinium += moradinium

    def mine_moradinium(self, bot: discord.Client, downtime: int, actor_name=""):
        self.validate_downtime(downtime)
        mining_weeks = downtime // 5
        roll_results: List[Tuple[int,int,int]] = []
        total_moradinium = 0
        for _ in range(mining_weeks):
            rolls, total = roll_dice(bot, modifier=0, roll_mode="normal", actor_name=actor_name)
            earned = (total+7) // 4 + (1 if rolls[0]==20 else 0)
            total_moradinium += earned
            roll_results.append((rolls[0], total, earned))
        self.moradinium += total_moradinium
        self.downtime -= downtime
        return roll_results

    def earn_money(self, bot: discord.Client, downtime: int, modifier: int=0, roll_mode: str="normal", actor_name: str=""):
        self.validate_downtime(downtime)
        earning_weeks = downtime // 5
        roll_results: List[Tuple[int,int,int]] = []
        total_earned = Money()
        for _ in range(earning_weeks):
            rolls, total = roll_dice(bot, modifier=modifier, roll_mode=roll_mode, actor_name=actor_name)
            base_gold = min(2 ** (max(total - 6, 0) // 5) * 7, 112)
            earned = Money.from_gold(base_gold) if rolls[0] != 20 else Money(base_gold * 150)
            total_earned += earned
            roll_results.append((rolls[0], total, earned.copper / 100))
        gold, silver, copper = total_earned.gold_denominations()
        self.add(gold=gold, silver=silver, copper=copper)
        self.downtime -= downtime
        return roll_results

    def sale(self, bot: discord.Client, item: str, persuasion_modifier: int=0, roll_mode: str="normal", 
                    crafting_cost: float=0, quantity: int=1, material: int=0, actor_name: str="", point_of_sale: str="general store"):
        from helpers.utils import to_currency
        rolls, total_persuasion = roll_dice(bot, modifier=persuasion_modifier, roll_mode=roll_mode, actor_name=actor_name)
        earnings_percent = (min(total_persuasion + 40 + (20 if point_of_sale=="your own shop" else 0), 80) + (10 if rolls[0]==20 else 0)) / 100
        earnings = crafting_cost * earnings_percent
        sale_price_per_item = material + crafting_cost + earnings
        total_sale_price = sale_price_per_item * quantity

        earnings_gold, earnings_silver, earnings_copper, earnings_amount = to_currency(earnings)
        item_gold, item_silver, item_copper, item_amount = to_currency(sale_price_per_item)
        total_gold, total_silver, total_copper, total_amount = to_currency(total_sale_price)

        self.add(gold=total_gold,silver=total_silver, copper=total_copper)
        
        msg = (f"Item(s): {item}\n"
               f"Roll: {rolls[0]} + {persuasion_modifier} = {total_persuasion}\n"
               f"Earnings rate: {earnings_percent * 100:.0f}%\n"
               f"Profit per item: {earnings_amount}\n"
               f"Sale price per item: {item_amount}\n")
        if quantity > 1:
            msg += f"Total sale price for {quantity} items: {total_amount}"
        else:
            msg += f"Total sale price: {total_amount}"
        return msg
