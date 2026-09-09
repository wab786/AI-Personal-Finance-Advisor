import ollama


def get_financial_advice(expenses, income):

    prompt = f"""
You are an AI personal finance assistant.

Monthly income: ₹{income:,.0f}

Expense data:
{expenses}

Analyze the user's spending.

Give your response in these sections:

### 1. Spending Summary
Briefly summarize the user's income and expenses.

### 2. Highest Spending Category
Identify the category with the highest spending.

### 3. Spending Analysis
Explain what the spending pattern shows.

### 4. Practical Suggestions
Give 3 simple and realistic ways to manage expenses.

### 5. Savings Suggestion
Suggest a simple way to increase savings.

Use the actual numbers provided.
Keep the explanation simple and clear.
Do not recommend specific financial products or investments.
"""

    try:
        response = ollama.chat(
            model="llama3.2",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response["message"]["content"]

    except Exception as e:
        return (
            "Sorry, I could not generate financial advice right now. "
            "Please make sure Ollama is running and try again."
        )

    return response["message"]["content"]