import streamlit as st
import sqlite3
import hashlib
from datetime import date
from ai_advisor import get_financial_advice


# =========================================================
# DATABASE
# =========================================================

DB_NAME = "finance.db"


def create_connection():
    return sqlite3.connect(DB_NAME)


def hash_password(password):
    return hashlib.sha256(
        password.encode("utf-8")
    ).hexdigest()


def create_table():

    connection = create_connection()

    # -----------------------------------------------------
    # Expenses
    # -----------------------------------------------------

    connection.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            amount REAL,
            date TEXT,
            description TEXT
        )
    """)

    # -----------------------------------------------------
    # Goals
    # -----------------------------------------------------

    connection.execute("""
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY,
            goal_name TEXT,
            target_savings REAL
        )
    """)

    # Support old database
    try:
        connection.execute(
            "ALTER TABLE goals ADD COLUMN goal_name TEXT"
        )
    except sqlite3.OperationalError:
        pass

    # -----------------------------------------------------
    # Profile
    # -----------------------------------------------------

    connection.execute("""
        CREATE TABLE IF NOT EXISTS profile (
            id INTEGER PRIMARY KEY,
            name TEXT,
            email TEXT,
            income REAL
        )
    """)

    # -----------------------------------------------------
    # Users
    # -----------------------------------------------------

    connection.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)

    # -----------------------------------------------------
    # Default user
    # -----------------------------------------------------

    user = connection.execute(
        """
        SELECT id
        FROM users
        WHERE id = 1
        """
    ).fetchone()

    if not user:

        connection.execute(
            """
            INSERT INTO users
            (
                id,
                username,
                password_hash
            )
            VALUES (?, ?, ?)
            """,
            (
                1,
                "admin",
                hash_password("1234")
            )
        )

    connection.commit()
    connection.close()


# =========================================================
# AUTHENTICATION
# =========================================================

def get_user_credentials():

    connection = create_connection()

    user = connection.execute(
        """
        SELECT username, password_hash
        FROM users
        WHERE id = 1
        """
    ).fetchone()

    connection.close()

    return user


def verify_login(username, password):

    user = get_user_credentials()

    if not user:
        return False

    saved_username, saved_password_hash = user

    return (
        username == saved_username
        and
        hash_password(password) == saved_password_hash
    )


def change_credentials(
    new_username,
    new_password
):

    connection = create_connection()

    connection.execute(
        """
        UPDATE users
        SET username = ?,
            password_hash = ?
        WHERE id = 1
        """,
        (
            new_username,
            hash_password(new_password)
        )
    )

    connection.commit()
    connection.close()


# =========================================================
# PROFILE
# =========================================================

def load_profile():

    connection = create_connection()

    profile = connection.execute(
        """
        SELECT name, email, income
        FROM profile
        WHERE id = 1
        """
    ).fetchone()

    connection.close()

    if profile:

        st.session_state["name"] = profile[0]
        st.session_state["email"] = profile[1]
        st.session_state["income"] = profile[2]


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="AI Personal Finance Advisor",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# LOGIN PAGE
# =========================================================

def login_page():

    st.title("💰 AI Personal Finance Advisor")

    st.subheader(
        "Smart expense tracking and AI-powered insights"
    )

    st.info(
        "💡 Small steps every day build big financial "
        "freedom tomorrow."
    )

    st.divider()

    left, center, right = st.columns(
        [1, 1.2, 1]
    )

    with center:

        st.header("🔐 Welcome Back")

        st.write(
            "Sign in to access your personal "
            "finance dashboard."
        )

        username = st.text_input(
            "Username",
            placeholder="Enter username"
        )

        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter password"
        )

        if st.button(
            "🚀 Login",
            type="primary",
            use_container_width=True
        ):

            if verify_login(
                username.strip(),
                password
            ):

                st.session_state.logged_in = True

                st.session_state.username = (
                    username.strip()
                )

                st.success(
                    "Login successful! 🎉"
                )

                st.rerun()

            else:

                st.error(
                    "Invalid username or password."
                )

        st.caption(
            "First-time login: admin / 1234"
        )


# =========================================================
# MAIN DASHBOARD
# =========================================================

def dashboard():

    # =====================================================
    # SIDEBAR
    # =====================================================

    st.sidebar.title("💰 AI Finance")

    st.sidebar.write(
        "Your personal finance assistant"
    )

    st.sidebar.divider()

    menu = st.sidebar.radio(
        "Navigation",
        [
            "🏠 Dashboard",
            "➕ Add Expense",
            "💰 Budget",
            "🔄 Transactions",
            "📊 Reports",
            "🎯 Goals",
            "🤖 AI Advisor",
            "⚙️ Settings"
        ]
    )

    st.sidebar.divider()

    if st.sidebar.button(
        "🚪 Logout",
        use_container_width=True
    ):

        st.session_state.logged_in = False

        st.session_state.pop(
            "username",
            None
        )

        st.rerun()


    # =====================================================
    # DASHBOARD
    # =====================================================

    if menu == "🏠 Dashboard":

        st.title("🏠 Financial Dashboard")

        st.info(
            "💡 Small steps every day build big financial "
            "freedom tomorrow."
        )

        income = float(
            st.session_state.get(
                "income",
                30000.0
            )
        )

        connection = create_connection()

        total_expenses = connection.execute(
            """
            SELECT COALESCE(SUM(amount), 0)
            FROM expenses
            """
        ).fetchone()[0]

        category_data = connection.execute(
            """
            SELECT category, SUM(amount)
            FROM expenses
            GROUP BY category
            """
        ).fetchall()

        saved_goal = connection.execute(
            """
            SELECT goal_name, target_savings
            FROM goals
            WHERE id = 1
            """
        ).fetchone()

        connection.close()

        total_expenses = float(
            total_expenses or 0
        )

        savings = (
            income -
            total_expenses
        )

        if saved_goal:

            goal_name = (
                saved_goal[0]
                or "Savings Goal"
            )

            goal_amount = float(
                saved_goal[1]
            )

        else:

            goal_name = "Savings Goal"
            goal_amount = 50000.0


        # -------------------------------------------------
        # FINANCIAL METRICS
        # -------------------------------------------------

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            st.metric(
                "💼 Income",
                f"₹{income:,.0f}"
            )

        with col2:

            st.metric(
                "💸 Expenses",
                f"₹{total_expenses:,.0f}"
            )

        with col3:

            st.metric(
                "💰 Savings",
                f"₹{savings:,.0f}"
            )

        with col4:

            st.metric(
                f"🎯 {goal_name}",
                f"₹{goal_amount:,.0f}"
            )


        st.divider()


        # -------------------------------------------------
        # SPENDING BREAKDOWN
        # -------------------------------------------------

        left, right = st.columns(2)

        with left:

            st.subheader(
                "📊 Spending Breakdown"
            )

            if category_data:

                chart_data = {
                    category: amount
                    for category, amount
                    in category_data
                }

                st.bar_chart(
                    chart_data
                )

            else:

                st.info(
                    "No expenses yet. Add your first "
                    "expense to see your spending chart."
                )


        # -------------------------------------------------
        # FINANCIAL HEALTH
        # -------------------------------------------------

        with right:

            st.subheader(
                "💡 Financial Health"
            )

            if income > 0:

                savings_percentage = (
                    savings /
                    income
                ) * 100

                if savings_percentage >= 30:

                    st.success(
                        f"🟢 Excellent! You are saving "
                        f"{savings_percentage:.1f}% "
                        "of your income."
                    )

                elif savings_percentage >= 10:

                    st.info(
                        f"🟡 You are saving "
                        f"{savings_percentage:.1f}% "
                        "of your income. "
                        "There is room to improve."
                    )

                else:

                    st.warning(
                        f"🔴 Your savings are only "
                        f"{savings_percentage:.1f}% "
                        "of your income. "
                        "Review your spending."
                    )

            st.subheader(
                "📌 Quick Summary"
            )

            st.write(
                f"💼 Income: ₹{income:,.0f}"
            )

            st.write(
                f"💸 Expenses: ₹{total_expenses:,.0f}"
            )

            st.write(
                f"💰 Available savings: "
                f"₹{savings:,.0f}"
            )


    # =====================================================
    # ADD EXPENSE
    # =====================================================

    elif menu == "➕ Add Expense":

        st.title("➕ Add Expense")

        st.write(
            "Record your expenses to keep your "
            "financial data updated."
        )

        left, right = st.columns(2)

        with left:

            category = st.selectbox(
                "Category",
                [
                    "Food",
                    "Transport",
                    "Shopping",
                    "Entertainment",
                    "Bills",
                    "Other"
                ]
            )

            amount = st.number_input(
                "Amount (₹)",
                min_value=0.0,
                step=100.0
            )

        with right:

            expense_date = st.date_input(
                "Date",
                value=date.today()
            )

            description = st.text_input(
                "Description",
                placeholder="Example: Grocery shopping"
            )

        if st.button(
            "💾 Save Expense",
            type="primary"
        ):

            if amount <= 0:

                st.error(
                    "Expense amount must be greater than ₹0."
                )

            else:

                connection = create_connection()

                connection.execute(
                    """
                    INSERT INTO expenses
                    (
                        category,
                        amount,
                        date,
                        description
                    )
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        category,
                        amount,
                        str(expense_date),
                        description
                    )
                )

                connection.commit()
                connection.close()

                st.success(
                    "Expense added successfully! 🎉"
                )


    # =====================================================
    # BUDGET
    # =====================================================

    elif menu == "💰 Budget":

        st.title("💰 Monthly Budget")

        budget = st.number_input(
            "Monthly Budget",
            min_value=0.0,
            value=30000.0,
            step=1000.0
        )

        connection = create_connection()

        total_expenses = connection.execute(
            """
            SELECT COALESCE(SUM(amount), 0)
            FROM expenses
            """
        ).fetchone()[0]

        connection.close()

        total_expenses = float(
            total_expenses or 0
        )

        remaining = (
            budget -
            total_expenses
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "💰 Budget",
                f"₹{budget:,.0f}"
            )

        with col2:

            st.metric(
                "💸 Spent",
                f"₹{total_expenses:,.0f}"
            )

        with col3:

            st.metric(
                "💵 Remaining",
                f"₹{remaining:,.0f}"
            )

        st.divider()

        if budget > 0:

            usage = min(
                max(
                    total_expenses / budget,
                    0
                ),
                1.0
            )

            percentage = (
                total_expenses /
                budget
            ) * 100

            st.subheader(
                "📊 Budget Usage"
            )

            st.progress(
                usage
            )

            st.write(
                f"You have used **{percentage:.1f}%** "
                "of your budget."
            )

            if total_expenses > budget:

                st.error(
                    "⚠️ You have exceeded your "
                    "monthly budget."
                )

            elif percentage >= 80:

                st.warning(
                    "⚠️ You are close to your "
                    "budget limit."
                )

            else:

                st.success(
                    "🟢 You are within your budget."
                )

        st.divider()

        st.subheader(
            "📋 Category Budgets"
        )

        budgets = {}

        col1, col2 = st.columns(2)

        with col1:

            budgets["Food"] = st.number_input(
                "🍔 Food",
                min_value=0.0,
                value=5000.0,
                step=500.0,
                key="budget_food"
            )

            budgets["Transport"] = st.number_input(
                "🚌 Transport",
                min_value=0.0,
                value=3000.0,
                step=500.0,
                key="budget_transport"
            )

        with col2:

            budgets["Shopping"] = st.number_input(
                "🛍️ Shopping",
                min_value=0.0,
                value=5000.0,
                step=500.0,
                key="budget_shopping"
            )

            budgets["Other"] = st.number_input(
                "📦 Other",
                min_value=0.0,
                value=2000.0,
                step=500.0,
                key="budget_other"
            )

        connection = create_connection()

        for category, category_budget in budgets.items():

            spent = connection.execute(
                """
                SELECT COALESCE(SUM(amount), 0)
                FROM expenses
                WHERE category = ?
                """,
                (category,)
            ).fetchone()[0]

            st.write(
                f"**{category}:** "
                f"₹{spent:,.0f} / "
                f"₹{category_budget:,.0f}"
            )

            if category_budget > 0:

                st.progress(
                    min(
                        max(
                            spent /
                            category_budget,
                            0
                        ),
                        1.0
                    )
                )

        connection.close()


    # =====================================================
    # TRANSACTIONS
    # =====================================================

    elif menu == "🔄 Transactions":

        st.title("🔄 Transactions")

        connection = create_connection()

        expenses = connection.execute(
            """
            SELECT
                id,
                category,
                amount,
                date,
                description
            FROM expenses
            ORDER BY date DESC, id DESC
            """
        ).fetchall()

        connection.close()

        if expenses:

            for (
                expense_id,
                category,
                amount,
                expense_date,
                description
            ) in expenses:

                col1, col2, col3, col4, col5 = (
                    st.columns(
                        [1.4, 1, 1.2, 2, 0.6]
                    )
                )

                with col1:

                    st.write(
                        f"**{category}**"
                    )

                with col2:

                    st.write(
                        f"₹{amount:,.0f}"
                    )

                with col3:

                    st.write(
                        str(expense_date)
                    )

                with col4:

                    st.write(
                        description or "—"
                    )

                with col5:

                    if st.button(
                        "🗑️",
                        key=f"delete_{expense_id}"
                    ):

                        connection = create_connection()

                        connection.execute(
                            """
                            DELETE FROM expenses
                            WHERE id = ?
                            """,
                            (expense_id,)
                        )

                        connection.commit()
                        connection.close()

                        st.rerun()

                st.divider()

        else:

            st.info(
                "No transactions found."
            )


    # =====================================================
    # REPORTS
    # =====================================================

    elif menu == "📊 Reports":

        st.title("📊 Financial Reports")

        connection = create_connection()

        total_expenses = connection.execute(
            """
            SELECT COALESCE(SUM(amount), 0)
            FROM expenses
            """
        ).fetchone()[0]

        transaction_count = connection.execute(
            """
            SELECT COUNT(*)
            FROM expenses
            """
        ).fetchone()[0]

        category_data = connection.execute(
            """
            SELECT category, SUM(amount)
            FROM expenses
            GROUP BY category
            """
        ).fetchall()

        daily_data = connection.execute(
            """
            SELECT date, SUM(amount)
            FROM expenses
            GROUP BY date
            ORDER BY date
            """
        ).fetchall()

        connection.close()

        total_expenses = float(
            total_expenses or 0
        )

        col1, col2 = st.columns(2)

        with col1:

            st.metric(
                "💸 Total Expenses",
                f"₹{total_expenses:,.0f}"
            )

        with col2:

            st.metric(
                "🔄 Transactions",
                transaction_count
            )

        st.divider()

        st.subheader(
            "📊 Spending by Category"
        )

        if category_data:

            chart_data = {
                category: amount
                for category, amount
                in category_data
            }

            st.bar_chart(
                chart_data
            )

        else:

            st.info(
                "Add expenses to generate reports."
            )

        st.divider()

        st.subheader(
            "📅 Daily Spending"
        )

        if daily_data:

            chart_data = {
                expense_date: amount
                for expense_date, amount
                in daily_data
            }

            st.line_chart(
                chart_data
            )

        else:

            st.info(
                "No daily spending data available."
            )


    # =====================================================
    # SAVINGS GOALS
    # =====================================================

    elif menu == "🎯 Goals":

        st.title("🎯 Savings Goals")

        st.write(
            "Set a target and track your savings progress."
        )

        connection = create_connection()

        saved_goal = connection.execute(
            """
            SELECT goal_name, target_savings
            FROM goals
            WHERE id = 1
            """
        ).fetchone()

        connection.close()

        if saved_goal:

            saved_goal_name = (
                saved_goal[0] or ""
            )

            default_target = float(
                saved_goal[1]
            )

        else:

            saved_goal_name = ""
            default_target = 50000.0

        goal_name = st.text_input(
            "Goal Name",
            value=saved_goal_name,
            placeholder="Example: New Laptop"
        )

        target_amount = st.number_input(
            "Target Amount (₹)",
            min_value=0.0,
            value=default_target,
            step=1000.0
        )

        if st.button(
            "💾 Save Goal",
            type="primary"
        ):

            connection = create_connection()

            connection.execute(
                """
                INSERT OR REPLACE INTO goals
                (
                    id,
                    goal_name,
                    target_savings
                )
                VALUES (1, ?, ?)
                """,
                (
                    goal_name,
                    target_amount
                )
            )

            connection.commit()
            connection.close()

            st.success(
                "Savings goal saved successfully! 🎯"
            )

        connection = create_connection()

        total_expenses = connection.execute(
            """
            SELECT COALESCE(SUM(amount), 0)
            FROM expenses
            """
        ).fetchone()[0]

        connection.close()

        income = float(
            st.session_state.get(
                "income",
                30000.0
            )
        )

        current_savings = (
            income -
            total_expenses
        )

        st.divider()

        st.subheader(
            f"📊 {goal_name or 'Savings Goal'} Progress"
        )

        if target_amount > 0:

            raw_percentage = (
                current_savings /
                target_amount
            ) * 100

            percentage = max(
                0.0,
                min(
                    raw_percentage,
                    100.0
                )
            )

            progress = max(
                0.0,
                min(
                    current_savings /
                    target_amount,
                    1.0
                )
            )

            st.progress(
                progress
            )

            st.write(
                f"**{percentage:.1f}% completed**"
            )

            col1, col2, col3 = st.columns(3)

            with col1:

                st.metric(
                    "🎯 Target",
                    f"₹{target_amount:,.0f}"
                )

            with col2:

                st.metric(
                    "💵 Current Savings",
                    f"₹{current_savings:,.0f}"
                )

            with col3:

                remaining = max(
                    target_amount -
                    current_savings,
                    0
                )

                st.metric(
                    "📌 Remaining",
                    f"₹{remaining:,.0f}"
                )

        else:

            st.info(
                "Enter a target amount "
                "to see progress."
            )


    # =====================================================
    # AI ADVISOR
    # =====================================================

    elif menu == "🤖 AI Advisor":

        st.title(
            "🤖 AI Financial Advisor"
        )

        st.write(
            "Your local AI analyzes your spending "
            "and provides simple suggestions."
        )

        st.info(
            "The AI runs locally using Ollama. "
            "No paid API is required."
        )

        if st.button(
            "✨ Analyze My Finances",
            type="primary"
        ):

            connection = create_connection()

            expenses = connection.execute(
                """
                SELECT
                    category,
                    amount,
                    date,
                    description
                FROM expenses
                ORDER BY date DESC
                """
            ).fetchall()

            connection.close()

            income = float(
                st.session_state.get(
                    "income",
                    30000.0
                )
            )

            if expenses:

                category_totals = {}

                for (
                    category,
                    amount,
                    expense_date,
                    description
                ) in expenses:

                    if category not in category_totals:

                        category_totals[category] = 0

                    category_totals[category] += amount

                total_expenses = sum(
                    category_totals.values()
                )

                savings = (
                    income -
                    total_expenses
                )

                if income > 0:

                    savings_percentage = (
                        savings /
                        income
                    ) * 100

                else:

                    savings_percentage = 0

                if savings < 0:

                    financial_status = (
                        "🔴 Overspending"
                    )

                elif savings_percentage < 20:

                    financial_status = (
                        "🟡 Needs Attention"
                    )

                else:

                    financial_status = (
                        "🟢 Healthy Spending"
                    )

                expense_text = f"""
Monthly Income: ₹{income:.0f}
Total Expenses: ₹{total_expenses:.0f}
Remaining Savings: ₹{savings:.0f}
Savings Percentage: {savings_percentage:.1f}%

Category-wise Expenses:
"""

                expense_text += "\n".join(
                    [
                        f"{category}: ₹{amount:.0f}"
                        for category, amount
                        in category_totals.items()
                    ]
                )

                with st.spinner(
                    "🤖 AI is analyzing your finances..."
                ):

                    advice = get_financial_advice(
                        expense_text,
                        income
                    )

                st.subheader(
                    "📌 Financial Status"
                )

                st.metric(
                    "Current Status",
                    financial_status
                )

                st.subheader(
                    "📊 Spending Breakdown"
                )

                st.bar_chart(
                    category_totals
                )

                st.subheader(
                    "💡 Your AI Financial Advice"
                )

                st.markdown(
                    advice
                )

            else:

                st.info(
                    "Add some expenses first so "
                    "the AI can analyze your spending."
                )


    # =====================================================
    # SETTINGS
    # =====================================================

    elif menu == "⚙️ Settings":

        st.title("⚙️ Settings")

        st.write(
            "Manage your account, profile and login credentials."
        )


        # -------------------------------------------------
        # ACCOUNT
        # -------------------------------------------------

        st.subheader(
            "🔐 Account & Security"
        )

        credentials = get_user_credentials()

        current_username = (
            credentials[0]
            if credentials
            else st.session_state.get(
                "username",
                "admin"
            )
        )

        st.write(
            f"Current username: **{current_username}**"
        )

        st.divider()

        st.subheader(
            "🔑 Change Username & Password"
        )

        new_username = st.text_input(
            "New Username",
            value=current_username,
            key="new_username"
        )

        new_password = st.text_input(
            "New Password",
            type="password",
            placeholder="Enter a new password",
            key="new_password"
        )

        confirm_password = st.text_input(
            "Confirm New Password",
            type="password",
            placeholder="Re-enter your new password",
            key="confirm_password"
        )

        if st.button(
            "🔒 Update Login Credentials",
            type="primary"
        ):

            new_username = new_username.strip()

            if not new_username:

                st.error(
                    "Username cannot be empty."
                )

            elif not new_password:

                st.error(
                    "Password cannot be empty."
                )

            elif len(new_password) < 4:

                st.error(
                    "Password must contain at least 4 characters."
                )

            elif new_password != confirm_password:

                st.error(
                    "Passwords do not match."
                )

            else:

                try:

                    change_credentials(
                        new_username,
                        new_password
                    )

                    st.session_state.username = (
                        new_username
                    )

                    st.success(
                        "Login credentials updated successfully! 🔐"
                    )

                except sqlite3.IntegrityError:

                    st.error(
                        "That username is already in use."
                    )


        st.divider()


        # -------------------------------------------------
        # PROFILE
        # -------------------------------------------------

        st.subheader(
            "👤 Personal Profile"
        )

        saved_name = st.session_state.get(
            "name",
            ""
        )

        saved_email = st.session_state.get(
            "email",
            ""
        )

        saved_income = float(
            st.session_state.get(
                "income",
                30000.0
            )
        )

        name = st.text_input(
            "Full Name",
            value=saved_name,
            placeholder="Enter your name"
        )

        email = st.text_input(
            "Email",
            value=saved_email,
            placeholder="Enter your email"
        )

        monthly_income = st.number_input(
            "Monthly Income (₹)",
            min_value=0.0,
            value=saved_income,
            step=1000.0
        )

        if st.button(
            "💾 Save Profile",
            type="primary"
        ):

            st.session_state["name"] = name
            st.session_state["email"] = email
            st.session_state["income"] = monthly_income

            connection = create_connection()

            connection.execute(
                """
                INSERT OR REPLACE INTO profile
                (
                    id,
                    name,
                    email,
                    income
                )
                VALUES (1, ?, ?, ?)
                """,
                (
                    name,
                    email,
                    monthly_income
                )
            )

            connection.commit()
            connection.close()

            st.success(
                "Profile updated successfully! 🎉"
            )


        st.divider()


        # -------------------------------------------------
        # SECURITY INFORMATION
        # -------------------------------------------------

        st.subheader(
            "🛡️ Security"
        )

        st.info(
            "Your password is stored in the database "
            "as a SHA-256 hash instead of plain text."
        )

        st.caption(
            "Authentication is handled locally using SQLite."
        )


# =========================================================
# APPLICATION START
# =========================================================

create_table()

load_profile()

if "logged_in" not in st.session_state:

    st.session_state.logged_in = False


if st.session_state.logged_in:

    dashboard()

else:

    login_page()