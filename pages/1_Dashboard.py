"""
Dashboard Page - Visual overview of job costing
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from google_sheets import get_all_jobs, get_job_cost_totals, get_all_weekly_costs
except:
    from demo_data import get_all_jobs, get_job_cost_totals, get_all_weekly_costs
from utils import format_currency

st.set_page_config(page_title="Dashboard | Elite Wall Systems", page_icon="📊", layout="wide")

st.title("📊 Dashboard")
st.markdown("Visual overview of all jobs and costs")

# Load data
try:
    jobs = get_all_jobs()
    weekly_costs = get_all_weekly_costs()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

if not jobs:
    st.info("No jobs found. Create your first job to see the dashboard.")
    st.stop()

# Process job data
job_metrics = []
for job in jobs:
    totals = get_job_cost_totals(job["id"])
    total_budget = sum([
        float(job.get("budget_insurance", 0) or 0),
        float(job.get("budget_labor", 0) or 0),
        float(job.get("budget_stamps", 0) or 0),
        float(job.get("budget_material", 0) or 0),
        float(job.get("budget_subs_bond", 0) or 0),
        float(job.get("budget_equipment", 0) or 0),
    ])
    total_revenue = float(job.get("contract_amount", 0) or 0) + float(job.get("approved_change_orders", 0) or 0)
    total_cost = totals.get("total", 0)
    
    job_metrics.append({
        "job_number": job.get("job_number"),
        "job_name": job.get("job_name"),
        "status": job.get("status"),
        "customer": job.get("customers", {}).get("name", "N/A") if job.get("customers") else "N/A",
        "contract": float(job.get("contract_amount", 0) or 0),
        "revenue": total_revenue,
        "budget": total_budget,
        "cost": total_cost,
        "profit": total_revenue - total_cost,
        "profit_margin": ((total_revenue - total_cost) / total_revenue * 100) if total_revenue > 0 else 0,
        "budget_used": (total_cost / total_budget * 100) if total_budget > 0 else 0
    })

df_jobs = pd.DataFrame(job_metrics)

# Summary Metrics
st.markdown("### Summary")
col1, col2, col3, col4 = st.columns(4)

active_jobs = df_jobs[df_jobs["status"] == "active"] if not df_jobs.empty else pd.DataFrame()

with col1:
    st.metric("Total Jobs", len(df_jobs))
with col2:
    st.metric("Active Jobs", len(active_jobs))
with col3:
    st.metric("Total Revenue", format_currency(df_jobs["revenue"].sum() if not df_jobs.empty else 0))
with col4:
    st.metric("Total Costs", format_currency(df_jobs["cost"].sum() if not df_jobs.empty else 0))

st.markdown("---")

# Charts
col1, col2 = st.columns(2)

with col1:
    st.markdown("### Jobs by Status")
    if not df_jobs.empty:
        status_counts = df_jobs["status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]
        fig_status = px.pie(status_counts, values="Count", names="Status",
                           color_discrete_sequence=px.colors.qualitative.Set2)
        fig_status.update_layout(margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig_status, use_container_width=True)

with col2:
    st.markdown("### Budget vs Actual by Job")
    if not active_jobs.empty:
        fig_budget = go.Figure()
        fig_budget.add_trace(go.Bar(name="Budget", x=active_jobs["job_number"], 
                                    y=active_jobs["budget"], marker_color="#1E3A5F"))
        fig_budget.add_trace(go.Bar(name="Actual", x=active_jobs["job_number"], 
                                    y=active_jobs["cost"], marker_color="#E74C3C"))
        fig_budget.update_layout(barmode="group", margin=dict(t=0, b=0))
        st.plotly_chart(fig_budget, use_container_width=True)
    else:
        st.info("No active jobs to display")

st.markdown("---")

# Profit Margin Chart
st.markdown("### Profit Margins by Job")
if not df_jobs.empty and len(df_jobs[df_jobs["revenue"] > 0]) > 0:
    profit_df = df_jobs[df_jobs["revenue"] > 0].copy()
    profit_df = profit_df.sort_values("profit_margin", ascending=True)
    
    colors = ["#E74C3C" if x < 0 else "#27AE60" for x in profit_df["profit_margin"]]
    
    fig_profit = go.Figure(go.Bar(
        x=profit_df["profit_margin"],
        y=profit_df["job_number"] + " - " + profit_df["job_name"].str[:15],
        orientation="h",
        marker_color=colors,
        text=[f"{x:.1f}%" for x in profit_df["profit_margin"]],
        textposition="outside"
    ))
    fig_profit.update_layout(
        xaxis_title="Profit Margin %",
        margin=dict(l=0, r=50, t=0, b=0),
        height=max(300, len(profit_df) * 40)
    )
    st.plotly_chart(fig_profit, use_container_width=True)

st.markdown("---")

# Jobs Table
st.markdown("### All Jobs Summary")
if not df_jobs.empty:
    display_df = df_jobs[["job_number", "job_name", "customer", "status", "revenue", "cost", "profit", "profit_margin"]].copy()
    display_df.columns = ["Job #", "Name", "Customer", "Status", "Revenue", "Cost", "Profit", "Margin %"]
    display_df["Revenue"] = display_df["Revenue"].apply(format_currency)
    display_df["Cost"] = display_df["Cost"].apply(format_currency)
    display_df["Profit"] = display_df["Profit"].apply(format_currency)
    display_df["Margin %"] = display_df["Margin %"].apply(lambda x: f"{x:.1f}%")
    st.dataframe(display_df, use_container_width=True, hide_index=True)
