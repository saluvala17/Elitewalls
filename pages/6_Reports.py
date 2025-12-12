"""
Reports Page - Generate and export job costing reports
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from google_sheets import get_all_jobs, get_all_customers, get_job_cost_totals, get_all_weekly_costs
except:
    from demo_data import get_all_jobs, get_all_customers, get_job_cost_totals, get_all_weekly_costs
from utils import format_currency, export_to_excel

st.set_page_config(page_title="Reports | Elite Wall Systems", page_icon="📈", layout="wide")

st.title("📈 Reports")
st.markdown("Generate and export job costing reports")

try:
    jobs = get_all_jobs()
    customers = get_all_customers()
    all_weekly_costs = get_all_weekly_costs()
except Exception as e:
    st.error(f"Error: {e}")
    st.stop()

if not jobs:
    st.info("No jobs found. Create jobs to generate reports.")
    st.stop()

report_type = st.selectbox("Select Report", [
    "Job Cost Summary",
    "Job Profitability Analysis", 
    "Budget vs Actual Comparison",
    "Customer Summary",
    "Export All Data"
])

st.markdown("---")

# Job Cost Summary
if report_type == "Job Cost Summary":
    st.markdown("### Job Cost Summary Report")
    
    job_options = ["All Jobs"] + [f"{j['job_number']} - {j['job_name']}" for j in jobs]
    selected = st.selectbox("Select Job", job_options)
    
    report_jobs = jobs if selected == "All Jobs" else [j for j in jobs if f"{j['job_number']} - {j['job_name']}" == selected]
    
    report_data = []
    for job in report_jobs:
        totals = get_job_cost_totals(job["id"])
        customer = job.get("customers", {}).get("name", "N/A") if job.get("customers") else "N/A"
        total_revenue = float(job.get("contract_amount", 0) or 0) + float(job.get("approved_change_orders", 0) or 0)
        total_cost = totals.get("total", 0)
        profit = total_revenue - total_cost
        
        report_data.append({
            "Job #": job.get("job_number"),
            "Job Name": job.get("job_name"),
            "Customer": customer,
            "Status": str(job.get("status", "")).title(),
            "Contract": float(job.get("contract_amount", 0) or 0),
            "Change Orders": float(job.get("approved_change_orders", 0) or 0),
            "Total Revenue": total_revenue,
            "Insurance": totals.get("insurance", 0),
            "Labor": totals.get("labor", 0),
            "Stamps": totals.get("stamps", 0),
            "Materials": totals.get("material", 0),
            "Subs/Bond": totals.get("subs_bond", 0),
            "Equipment": totals.get("equipment", 0),
            "Total Cost": total_cost,
            "Profit": profit,
            "Margin %": (profit / total_revenue * 100) if total_revenue > 0 else 0,
            "Man Days": totals.get("man_days", 0)
        })
    
    df = pd.DataFrame(report_data)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Revenue", format_currency(df["Total Revenue"].sum()))
    with col2:
        st.metric("Total Costs", format_currency(df["Total Cost"].sum()))
    with col3:
        st.metric("Total Profit", format_currency(df["Profit"].sum()))
    with col4:
        avg_margin = (df["Profit"].sum() / df["Total Revenue"].sum() * 100) if df["Total Revenue"].sum() > 0 else 0
        st.metric("Avg Margin", f"{avg_margin:.1f}%")
    
    st.markdown("---")
    display_df = df.copy()
    for col in ["Contract", "Change Orders", "Total Revenue", "Insurance", "Labor", "Stamps", 
                "Materials", "Subs/Bond", "Equipment", "Total Cost", "Profit"]:
        display_df[col] = display_df[col].apply(format_currency)
    display_df["Margin %"] = display_df["Margin %"].apply(lambda x: f"{x:.1f}%")
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    excel_data = export_to_excel(df)
    st.download_button("📥 Download Excel", data=excel_data,
        file_name=f"job_cost_summary_{datetime.now().strftime('%Y%m%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# Profitability Analysis
elif report_type == "Job Profitability Analysis":
    st.markdown("### Job Profitability Analysis")
    
    profit_data = []
    for job in jobs:
        totals = get_job_cost_totals(job["id"])
        total_revenue = float(job.get("contract_amount", 0) or 0) + float(job.get("approved_change_orders", 0) or 0)
        total_cost = totals.get("total", 0)
        profit = total_revenue - total_cost
        margin = (profit / total_revenue * 100) if total_revenue > 0 else 0
        
        profit_data.append({
            "job": f"{job['job_number']} - {str(job['job_name'])[:15]}",
            "revenue": total_revenue, "cost": total_cost,
            "profit": profit, "margin": margin,
            "status": job.get("status", "")
        })
    
    profit_df = pd.DataFrame(profit_data)
    
    status_filter = st.multiselect("Filter by Status", ["active", "completed", "estimate", "closed"], default=["active", "completed"])
    filtered_df = profit_df[profit_df["status"].isin(status_filter)] if status_filter else profit_df
    
    if not filtered_df.empty:
        st.markdown("#### Profit Margin by Job")
        sorted_df = filtered_df.sort_values("margin", ascending=True)
        colors = ["#E74C3C" if x < 0 else "#27AE60" if x > 15 else "#F39C12" for x in sorted_df["margin"]]
        
        fig = go.Figure(go.Bar(
            x=sorted_df["margin"], y=sorted_df["job"], orientation="h",
            marker_color=colors, text=[f"{x:.1f}%" for x in sorted_df["margin"]], textposition="outside"
        ))
        fig.update_layout(xaxis_title="Profit Margin %", height=max(400, len(sorted_df) * 35), margin=dict(l=10, r=50))
        st.plotly_chart(fig, use_container_width=True)

# Budget vs Actual
elif report_type == "Budget vs Actual Comparison":
    st.markdown("### Budget vs Actual Comparison")
    
    job_options = {j["id"]: f"{j['job_number']} - {j['job_name']}" for j in jobs}
    selected_job_id = st.selectbox("Select Job", list(job_options.keys()), format_func=lambda x: job_options[x])
    
    job = next(j for j in jobs if j["id"] == selected_job_id)
    totals = get_job_cost_totals(selected_job_id)
    
    categories = ["Insurance", "Labor", "Stamps", "Materials", "Subs/Bond", "Equipment"]
    budget_values = [
        float(job.get("budget_insurance", 0) or 0),
        float(job.get("budget_labor", 0) or 0),
        float(job.get("budget_stamps", 0) or 0),
        float(job.get("budget_material", 0) or 0),
        float(job.get("budget_subs_bond", 0) or 0),
        float(job.get("budget_equipment", 0) or 0)
    ]
    actual_values = [
        totals.get("insurance", 0),
        totals.get("labor", 0),
        totals.get("stamps", 0),
        totals.get("material", 0),
        totals.get("subs_bond", 0),
        totals.get("equipment", 0)
    ]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Budget", x=categories, y=budget_values, marker_color="#1E3A5F"))
    fig.add_trace(go.Bar(name="Actual", x=categories, y=actual_values, marker_color="#E74C3C"))
    fig.update_layout(barmode="group", title="Budget vs Actual by Category")
    st.plotly_chart(fig, use_container_width=True)
    
    comparison_df = pd.DataFrame({
        "Category": categories + ["TOTAL"],
        "Budget": budget_values + [sum(budget_values)],
        "Actual": actual_values + [sum(actual_values)]
    })
    comparison_df["Variance"] = comparison_df["Actual"] - comparison_df["Budget"]
    comparison_df["% Used"] = comparison_df.apply(lambda r: f"{(r['Actual']/r['Budget']*100):.1f}%" if r['Budget'] > 0 else "N/A", axis=1)
    
    display_df = comparison_df.copy()
    for col in ["Budget", "Actual", "Variance"]:
        display_df[col] = display_df[col].apply(format_currency)
    st.dataframe(display_df, use_container_width=True, hide_index=True)

# Customer Summary
elif report_type == "Customer Summary":
    st.markdown("### Customer Summary Report")
    
    customer_data = []
    for customer in customers:
        customer_jobs = [j for j in jobs if str(j.get("customer_id", "")) == str(customer["id"])]
        total_revenue = sum(float(j.get("contract_amount", 0) or 0) + float(j.get("approved_change_orders", 0) or 0) for j in customer_jobs)
        total_cost = sum(get_job_cost_totals(j["id"]).get("total", 0) for j in customer_jobs)
        
        customer_data.append({
            "Customer": customer.get("name"),
            "Jobs": len(customer_jobs),
            "Active Jobs": len([j for j in customer_jobs if j.get("status") == "active"]),
            "Total Revenue": total_revenue,
            "Total Cost": total_cost,
            "Profit": total_revenue - total_cost,
            "Margin %": ((total_revenue - total_cost) / total_revenue * 100) if total_revenue > 0 else 0
        })
    
    cust_df = pd.DataFrame(customer_data).sort_values("Total Revenue", ascending=False)
    
    display_df = cust_df.copy()
    for col in ["Total Revenue", "Total Cost", "Profit"]:
        display_df[col] = display_df[col].apply(format_currency)
    display_df["Margin %"] = display_df["Margin %"].apply(lambda x: f"{x:.1f}%")
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    if not cust_df.empty:
        fig = px.bar(cust_df, x="Customer", y="Total Revenue", color="Margin %", color_continuous_scale="RdYlGn")
        fig.update_layout(title="Revenue by Customer")
        st.plotly_chart(fig, use_container_width=True)

# Export All Data
elif report_type == "Export All Data":
    st.markdown("### Export All Data")
    st.markdown("Download complete data export for backup or analysis.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Jobs Data")
        jobs_df = pd.DataFrame(jobs)
        if not jobs_df.empty and "customers" in jobs_df.columns:
            jobs_df["customer_name"] = jobs_df["customers"].apply(lambda x: x.get("name", "") if isinstance(x, dict) else "")
            jobs_df = jobs_df.drop(columns=["customers"], errors="ignore")
        if not jobs_df.empty:
            excel_jobs = export_to_excel(jobs_df)
            st.download_button("📥 Download Jobs", data=excel_jobs,
                file_name=f"jobs_export_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    
    with col2:
        st.markdown("#### Weekly Costs Data")
        if all_weekly_costs:
            costs_df = pd.DataFrame(all_weekly_costs)
            if "jobs" in costs_df.columns:
                costs_df["job_info"] = costs_df["jobs"].apply(lambda x: f"{x.get('job_number', '')} - {x.get('job_name', '')}" if isinstance(x, dict) else "")
                costs_df = costs_df.drop(columns=["jobs"], errors="ignore")
            excel_costs = export_to_excel(costs_df)
            st.download_button("📥 Download Weekly Costs", data=excel_costs,
                file_name=f"weekly_costs_export_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        else:
            st.info("No weekly cost data to export")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Customers Data")
        if customers:
            cust_df = pd.DataFrame(customers)
            excel_cust = export_to_excel(cust_df)
            st.download_button("📥 Download Customers", data=excel_cust,
                file_name=f"customers_export_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
