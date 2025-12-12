"""
Utility functions for Elite Wall Systems
"""
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
from io import BytesIO


def format_currency(value):
    """Format number as currency"""
    if value is None:
        return "$0.00"
    try:
        return f"${float(value):,.2f}"
    except:
        return "$0.00"


def format_number(value):
    """Format number with commas"""
    if value is None:
        return "0"
    try:
        return f"{float(value):,.0f}"
    except:
        return "0"


def format_percentage(value):
    """Format as percentage"""
    if value is None:
        return "0%"
    try:
        return f"{float(value):.1f}%"
    except:
        return "0%"


def get_week_ending_date():
    """Get the most recent week ending date (Saturday)"""
    today = datetime.now().date()
    days_until_saturday = (5 - today.weekday()) % 7
    if days_until_saturday == 0 and datetime.now().hour < 12:
        return today
    return today + timedelta(days=days_until_saturday)


def get_last_n_week_endings(n=8):
    """Get list of last N week ending dates"""
    current = get_week_ending_date()
    weeks = []
    for i in range(n):
        weeks.append(current - timedelta(weeks=i))
    return weeks


def calculate_variance(actual, budget):
    """Calculate variance between actual and budget"""
    if budget is None or budget == 0:
        return None
    return actual - budget


def get_status_color(status):
    """Get color for job status"""
    colors = {
        "estimate": "🟡",
        "active": "🟢",
        "completed": "🔵",
        "closed": "⚫"
    }
    return colors.get(status, "⚪")


def get_variance_indicator(actual, budget):
    """Get indicator for variance (over/under budget)"""
    try:
        actual = float(actual or 0)
        budget = float(budget or 0)
    except:
        return ""
    
    if budget == 0:
        return ""
    variance = actual - budget
    if variance > budget * 0.1:  # More than 10% over
        return "🔴"
    elif variance > 0:  # Slightly over
        return "🟡"
    else:  # Under budget
        return "🟢"


def export_to_excel(dataframe, filename="export.xlsx"):
    """Convert dataframe to Excel bytes for download"""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        dataframe.to_excel(writer, index=False, sheet_name='Data')
    output.seek(0)
    return output


def show_success_message(message):
    """Display success message"""
    st.success(f"✅ {message}")


def show_error_message(message):
    """Display error message"""
    st.error(f"❌ {message}")


def show_warning_message(message):
    """Display warning message"""
    st.warning(f"⚠️ {message}")
