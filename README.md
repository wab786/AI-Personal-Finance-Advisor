# 💰 AI Personal Finance Advisor

An AI-powered personal finance management application built with Python, Streamlit, SQLite, and Ollama.

The application helps users track expenses, manage budgets, set savings goals, view financial reports, and receive AI-generated insights based on their spending patterns.

---

## 📌 Project Overview

Managing personal expenses manually can make it difficult to understand spending habits and savings.

The **AI Personal Finance Advisor** provides a simple dashboard where users can record their expenses, monitor their budget, track savings goals, and use a local AI model to analyze their financial data and provide practical suggestions.

The application uses **Ollama with Llama 3.2** to generate financial insights locally without requiring a paid cloud AI API.

---

## ✨ Features

### 🔐 User Authentication
- Username and password login
- Dynamic username and password management
- Password stored as a SHA-256 hash
- Logout functionality

### 🏠 Dashboard
- Monthly income overview
- Total expenses
- Available savings
- Savings goal
- Spending breakdown
- Financial health indicator

### ➕ Expense Management
- Add expenses
- Select expense categories
- Enter amount and date
- Add expense descriptions
- Store expenses in SQLite
- Delete transactions

### 💰 Budget Management
- Set monthly budget
- Track total spending
- Calculate remaining budget
- Display budget usage
- Category-wise budget tracking
- Budget warning when spending is high

### 📊 Financial Reports
- Total expense calculation
- Transaction count
- Spending by category
- Daily spending report
- Visual charts

### 🎯 Savings Goals
- Create a savings goal
- Set target amount
- Track current savings
- Calculate remaining amount
- Display progress toward the goal

### 🤖 AI Financial Advisor
- Analyzes recorded expenses
- Calculates spending patterns
- Identifies financial status
- Generates AI-powered financial suggestions
- Provides spending and savings recommendations
- Runs locally using Ollama and Llama 3.2

### ⚙️ Settings
- Change username
- Change password
- Update personal profile
- Update monthly income
- Manage account information

---

## 🛠️ Technologies Used

| Technology | Purpose |
|------------|---------|
| Python | Application logic and backend |
| Streamlit | User interface |
| SQLite | Database |
| Ollama | Local AI model execution |
| Llama 3.2 | AI financial analysis |
| Pandas | Data processing/analysis |
| Git & GitHub | Version control and project hosting |

---

## 🏗️ Project Architecture

```text
                    ┌──────────────────────┐
                    │       User           │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │      Streamlit       │
                    │      Frontend        │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │       Python         │
                    │   Application Logic  │
                    └───────┬────────┬─────┘
                            │        │
                 ┌──────────┘        └──────────┐
                 ▼                               ▼
        ┌──────────────────┐            ┌──────────────────┐
        │     SQLite       │            │      Ollama      │
        │    Database      │            │    Llama 3.2     │
        └──────────────────┘            └──────────────────┘
                                                │
                                                ▼
                                      ┌──────────────────┐
                                      │   AI Financial   │
                                      │     Advice       │
                                      └──────────────────┘
