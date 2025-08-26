from __future__ import annotations
from .bastion import Bastion
from .resource import Resource

class Lifestyle:
    LIFESTYLE_COSTS = {
        "wretched": 0,
        "modest": 7,
        "comfortable": 14,
        "wealthy": 28,
        "aristocratic": 70
    }

    def __init__(self, lifestyle_type="modest"):
        self.lifestyle_type = (lifestyle_type or "modest").lower()
        self.bastion = Bastion(lifestyle_type=self.lifestyle_type)
        self.living_weeks = 0

    def pay_for_weeks(self, actor_resources: Resource, weeks=1, extra_expenses_sp=0):
        if self.living_weeks < weeks:
            raise ValueError(f"You tried to pay for {weeks} weeks but have only {self.living_weeks} weeks open.")
        cost_per_week_gp = self.LIFESTYLE_COSTS.get(self.lifestyle_type, 7)
        total_gold_cost = cost_per_week_gp * weeks
        total_silver_cost = extra_expenses_sp * weeks
        actor_resources.deduct(gold=total_gold_cost, silver=total_silver_cost)
        self.living_weeks -= weeks
        if self.living_weeks == 0 and self.bastion.bastion_flag == 1:
            self.bastion.turn_available_flag = 1
        return total_gold_cost, total_silver_cost

    def get_summary(self) -> str:
        return f"**Lifestyle:** {self.lifestyle_type.capitalize()} (Weeks open: {self.living_weeks})"
