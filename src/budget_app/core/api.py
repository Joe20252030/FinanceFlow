"""
本地预算分配核心接口框架，无需API调用。
- 用户输入数据由主界面传递。
- 所有预算分配逻辑在本地实现，无需外部API。
"""
import json

last_input_data = None  # 类型: dict, 结构如下：
# {
#   'income_input': [ {'name': str, 'period': str, 'amount': float}, ... ],
#   'fixed_costs': [ {'name': str, 'amount': float}, ... ],
#   'budget_preference': [ {'category': str, 'percent': int}, ... ],
#   'constraints': [ {'category': str, 'min': int, 'max': int}, ... ]
# }

def generate_budget_plan_local(input_data):
    """
    本地预算分配核心逻辑，无需API。
    输入: input_data (dict)
    输出: 预算分配结果文本（category-amount-percent，每行一个类别）
    """
    # Step 1: 计算总收入
    total_income = 0.0
    for inc in input_data.get('income_input', []):
        amt = inc.get('amount', 0.0)
        if inc.get('period', '').lower() == 'week':
            amt *= 4
        total_income += amt
    # Step 2: 计算总固定支出
    total_fixed = sum(fc.get('amount', 0.0) for fc in input_data.get('fixed_costs', []))
    # Step 3: 计算可分配预算
    available = total_income - total_fixed
    # Step 4: 读取预算偏好
    prefs = input_data.get('budget_preference', [])
    # Step 5: 按配比分配预算，记录原始分配
    total_percent = sum(p['percent'] for p in prefs)
    plan = []
    used = 0.0
    raw_alloc = {}
    for p in prefs:
        cat = p['category']
        percent = p['percent']
        amt = available * percent / total_percent if total_percent > 0 else 0.0
        raw_alloc[cat] = amt
    # Step 6: 生成 plan
    for p in prefs:
        cat = p['category']
        amt = round(raw_alloc[cat], 2)
        plan.append({
            'category': cat,
            'amount': amt,
            'percent': 0  # 由 PlanView 统一计算
        })
    # Step 7: 输出文本
    lines = [f"{item['category']}-{item['amount']}-{item['percent']}" for item in plan]
    return "\n".join(lines)

def parse_gemini_response(response_text):
    """
    Parse Gemini API/local response text to structured data for plan table.
    Expected format per line: category-amount-percent
    Returns: List[Dict] with keys: category, amount, percent
    """
    result = []
    for line in response_text.strip().splitlines():
        parts = line.strip().split("-")
        if len(parts) == 3:
            category, amount, percent = parts
            try:
                result.append({
                    "category": category.strip(),
                    "amount": float(amount.strip()),
                    "percent": float(percent.strip())
                })
            except Exception:
                continue
    return result

# 使用示例（主程序中调用）
# from budget_app.core.api import generate_budget_plan_local, parse_gemini_response
# result_text = generate_budget_plan_local(last_input_data)
# print(result_text)
# plan_data = parse_gemini_response(result_text)
