from ai_advisor import get_financial_advice


expenses = """
Food: ₹5,000
Transport: ₹10,000
Shopping: ₹3,000
Entertainment: ₹2,000
"""

income = 50_000


advice = get_financial_advice(
    expenses,
    income
)

print("\n===== AI FINANCIAL ADVICE =====\n")
print(advice)