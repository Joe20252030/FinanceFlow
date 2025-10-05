from pydantic import BaseModel, Field
from typing import List, Optional
from src.budget_app.utils.money import Money


# Use a common Base that allows arbitrary types (Money) to be used in models.
class Base(BaseModel):
    model_config = {
        "arbitrary_types_allowed": True,
    }


class Income(Base):
    name: str
    amount: Money = Field(..., description="Monthly net income")


class FixedExpense(Base):
    name: str
    amount: Money
    essential: bool = True


class VariableExpense(Base):
    name: str
    min_amount: Optional[Money] = None
    max_amount: Optional[Money] = None
    priority: int = 100


class Preferences(Base):
    savings_rate_min: float = 0.1
    round_to: Money = Money("1.00")


class Constraints(Base):
    max_housing_ratio: float = 0.35
    emergency_fund_months: float = 3


class PlanningInput(Base):
    incomes: List[Income]
    fixed: List[FixedExpense]
    variables: List[VariableExpense]
    preferences: Preferences = Preferences()
    constraints: Constraints = Constraints()


class PlanItem(Base):
    category: str
    kind: str  # e.g., "fixed", "variable", "savings"
    allocated: Money


class PlanSummary(Base):
    total_income: Money
    total_expenses: Money
    savings: Money
    remaining: Money


class PlanResult(Base):
    items: List[PlanItem]
    summary: PlanSummary
