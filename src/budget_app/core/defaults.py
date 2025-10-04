from decimal import Decimal
from src.budget_app.core.models import PlanningInput, Income, FixedExpense, VariableExpense, Preferences, Constraints
from src.budget_app.utils.money import Money

# Default categories the app starts with
DEFAULT_VARIABLES = [
    VariableExpense(name = "Groceries", min_amount = Money("200")),
    VariableExpense(name = "Transportation", min_amount = Money("100")),
    VariableExpense(name = "Entertainment"),
]

def default_preferences() -> Preferences:
    """Return baseline user preferences (like minimum savings rate)."""
    return Preferences(
        savings_rate_min = 0.1,
        round_to = Money("1.00"),
    )

def default_constraints() -> Constraints:
    """Return default global constraints (like housing ratio)."""
    return Constraints(
        max_housing_ratio = 0.35,
        emergency_fund_months = 3,
    )

def starter_input() -> PlanningInput:
    """Generate a complete, ready-to-use PlanningInput with zeros."""
    return PlanningInput(
        incomes = [
            Income(name = "Primary Job", amount = Money("0")),
        ],
        fixed = [
            FixedExpense(name = "Rent", amount = Money("0"), essential = True),
            FixedExpense(name = "Utilities", amount = Money("0"), essential = True),
        ],
        variables = list(DEFAULT_VARIABLES),
        preferences = default_preferences(),
        constraints = default_constraints(),
    )

def merge_with_defaults(partial: dict) -> PlanningInput:
    """
    Merge user-provided data (from JSON or UI) with defaults,
    so missing sections are filled in automatically.
    """
    base = starter_input().model_dump()
    merged = {**base, **partial}
    return PlanningInput.model_validate(merged)
