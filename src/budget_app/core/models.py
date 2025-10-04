from pydantic import BaseModel, Field
from typing import List, Optional
from src.budget_app.utils.money import Money

class Income(BaseModel):
    name: str
    amount: Money = Field(..., description = "Monthly net income")

class FixedExpense(BaseModel):
    name: str
    amount: Money
    essential: bool = True

class VariableExpense(BaseModel):
    name: str
    min_amount: Optional[Money] = None
    max_amount: Optional[Money] = None
    priority: int = 100

class Preferences(BaseModel):
    savings_rate_min: float = 0.1
    round_to: Money = Money("1.00")

class Constraints(BaseModel):
    max_housing_ratio: float = 0.35
    emergency_fund_months: float = 3

class PlanningInput(BaseModel):
    incomes: List[Income]
    fixed: List[FixedExpense]
    variables: List[VariableExpense]
    preferences: Preferences = Preferences()
    constraints: Constraints = Constraints()

class PlanItem(BaseModel):
    category: str
    kind: str  # e.g., "fixed", "variable", "savings"
    allocated: Money

class PlanSummary(BaseModel):
    total_income: Money
    total_expenses: Money
    savings: Money
    remaining: Money

class PlanResult(BaseModel):
    items: List[PlanItem]
    summary: PlanSummary
