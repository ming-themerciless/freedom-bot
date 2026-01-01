from __future__ import annotations
from .bastion import Bastion
from .resource import Resource
from helpers.utils import to_currency

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

    def pay_for_weeks(
        self,
        actor_resources: "Resource",
        weeks: int = 1,
        extra_expenses_sp: float = 0.0,   # z.B. 3.5 = 3sp 5cp
    ) -> tuple[int, tuple[int, int, int]]:
        if weeks < 0:
            raise ValueError("Weeks cannot be negative.")
        if extra_expenses_sp < 0:
            raise ValueError("Expenses cannot be negative.")
        if self.living_weeks < weeks:
            raise ValueError(f"You tried to pay for {weeks} weeks but have only {self.living_weeks} weeks open.")

        cost_per_week_gp = self.LIFESTYLE_COSTS.get(self.lifestyle_type, 7)
        total_gold_cost = cost_per_week_gp * weeks  # nur Wochenkosten in gp

        # SP-Dezimal -> GP und stückeln (3.5sp => to_currency(0.35))
        gp_exp, sp_exp, cp_exp, _ = to_currency((extra_expenses_sp or 0.0) / 10.0)

        # zusammen abziehen
        actor_resources.deduct(
            gold=total_gold_cost + gp_exp,
            silver=sp_exp,
            copper=cp_exp,
        )

        self.living_weeks -= weeks
        actor_resources.downtime = min(actor_resources.downtime + weeks * 5, 60)

        if self.living_weeks == 0 and self.bastion.bastion_flag == 1:
            self.bastion.turn_available_flag = 1

        # getrennte Rückgabe: (Wochen-GP, (Exp-GP, Exp-SP, Exp-CP))
        return total_gold_cost, (gp_exp, sp_exp, cp_exp)

    def get_summary(self) -> str:
        return f"**Lifestyle:** {self.lifestyle_type.capitalize()} (Weeks open: {self.living_weeks})"
