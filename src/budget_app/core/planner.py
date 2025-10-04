from __future__ import annotations
from typing import List, Dict, Optional, Tuple
from src.budget_app.core.models import PlanningInput, PlanItem, PlanSummary, PlanResult, VariableExpense
from src.budget_app.utils.money import Money

class Planner:
    """
    Budget allocation engine (pure & deterministic).

    Pipeline:
      1) Totals & sanity
      2) Allocate FIXED first
      3) Allocate SAVINGS (based on total income * savings_rate_min)
      4) Apply variable FLOORS (min_amount) by priority
      5) Distribute remainder to VARIABLES up to their CAPS (max_amount), by priority
      6) Build PlanResult (items + summary)

    Notes:
      - All arithmetic uses Money.
      - Rounding is centralized via user preference round_to.
      - Deterministic ordering: (priority, name).
      - This version does not emit warnings (your models don't include them).
    """

    # ---------- public API ----------

    def build_plan(self, data: PlanningInput) -> PlanResult:
        # 1) Totals
        total_income = self._sum(i.amount for i in data.incomes)
        fixed_total = self._sum(f.amount for f in data.fixed)

        total_income = self._round(total_income, data)
        fixed_total = self._round(fixed_total, data)

        # 2) Fixed first
        items: List[PlanItem] = []
        remaining = total_income
        for f in data.fixed:
            amt = self._round(f.amount, data)
            if amt > Money("0"):
                items.append(self._item(f.name, "fixed", amt))
            remaining -= amt
        remaining = self._floor_zero(self._round(remaining, data))

        # 3) Savings (target = total_income * savings_rate_min)
        savings_target = self._round(
            total_income * Money.from_decimal(data.preferences.savings_rate_min), data) if data.preferences.savings_rate_min > 0 else Money("0")

        savings_alloc = Money("0")
        if savings_target > Money("0"):
            if remaining >= savings_target:
                savings_alloc = savings_target
            else:
                # allocate whatever remains (can't meet target)
                savings_alloc = self._floor_zero(remaining)
            if savings_alloc > Money("0"):
                items.append(self._item("Savings", "savings", self._round(savings_alloc, data)))
                remaining = self._floor_zero(self._round(remaining - savings_alloc, data))

        # 4) Variable floors (min_amount), in priority order
        variables = sorted(data.variables, key = lambda v: (v.priority, v.name.lower()))
        allocated_by_cat: Dict[str, Money] = {}

        for v in variables:
            if remaining <= Money("0"):
                break
            floor_amt = v.min_amount or Money("0")
            if floor_amt > Money("0"):
                alloc = self._bounded_allocation(floor_amt, v.max_amount, allocated_by_cat.get(v.name, Money("0")), remaining, data)
                if alloc > Money("0"):
                    self._add_var(items, allocated_by_cat, v.name, alloc, data)
                    remaining = self._floor_zero(self._round(remaining - alloc, data))

        # 5) Distribute remainder up to variable caps, still by priority
        for v in variables:
            if remaining <= Money("0"):
                break
            cap = v.max_amount
            current = allocated_by_cat.get(v.name, Money("0"))
            room = self._room_left(cap, current)
            if room <= Money("0"):
                continue
            add = self._round(min(room, remaining), data)
            if add > Money("0"):
                self._add_var(items, allocated_by_cat, v.name, add, data)
                remaining = self._floor_zero(self._round(remaining - add, data))

        # 6) Summary
        variable_total = self._sum(i.allocated for i in items if i.kind == "variable")
        savings_total = self._sum(i.allocated for i in items if i.kind == "savings")
        total_expenses = self._round(fixed_total + variable_total, data)
        remaining = self._floor_zero(self._round(total_income - total_expenses - savings_total, data))

        summary = PlanSummary(
            total_income = total_income,
            total_expenses = total_expenses,
            savings = self._round(savings_total, data),
            remaining = remaining,
        )

        return PlanResult(items = items, summary = summary)

    # ---------- helpers ----------

    def _item(self, category: str, kind: str, amount: Money) -> PlanItem:
        return PlanItem(category = category, kind = kind, allocated = amount)

    def _sum(self, it) -> Money:
        return sum(it, Money("0"))

    def _round(self, m: Money, data: PlanningInput) -> Money:
        step = data.preferences.round_to
        if step <= Money("0"):
            return m
        return m.quantize_to_step(step)

    def _floor_zero(self, m: Money) -> Money:
        return m if m > Money("0") else Money("0")

    def _room_left(self, cap: Optional[Money], current: Money) -> Money:
        if cap is None:
            # No cap → effectively infinite room; let caller min(...) with remaining
            return Money("999999999999.99")
        room = cap - current
        return room if room > Money("0") else Money("0")

    def _bounded_allocation(self, desired: Money, cap: Optional[Money], current: Money, remaining: Money, data: PlanningInput,) -> Money:
        """
        Allocate up to 'desired', but never exceed remaining or 'cap - current'.
        """
        room = self._room_left(cap, current)
        add = min(desired, room, remaining)
        return self._round(self._floor_zero(add), data)

    def _add_var(self, items: List[PlanItem], acc: Dict[str, Money], name: str, amount: Money, data: PlanningInput,) -> None:
        amount = self._round(amount, data)
        if amount <= Money("0"):
            return
        items.append(self._item(name, "variable", amount))
        acc[name] = acc.get(name, Money("0")) + amount
