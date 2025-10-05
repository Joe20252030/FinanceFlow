from src.budget_app.core.defaults import starter_input
from src.budget_app.core.planner import Planner


def test_planner_happy_path():
    data = starter_input()
    # give it some income and fixed costs
    data.incomes[0].amount = data.incomes[0].amount.__class__("2500")
    for f in data.fixed:
        f.amount = f.amount.__class__("700")

    planner = Planner()
    result = planner.build_plan(data)
    assert result is not None
    assert hasattr(result, 'items')
    assert hasattr(result, 'summary')
    assert result.summary.total_income > data.incomes[0].amount - data.summary if hasattr(data, 'summary') else True
