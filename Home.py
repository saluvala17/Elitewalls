"""
Elite Wall Systems - Job Costing Application
Main entry point - Google Sheets Version
"""
import streamlit as st
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Try Google Sheets, fall back to demo mode
try:
    from google_sheets import get_all_jobs, get_all_customers, get_job_cost_totals, initialize_sheets
    DEMO_MODE = False
except:
    from demo_data import get_all_jobs, get_all_customers, get_job_cost_totals, initialize_sheets
    DEMO_MODE = True
from utils import format_currency, get_status_color

# Page configuration
st.set_page_config(
    page_title="Elite Wall Systems",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E3A5F;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        border-left: 4px solid #1E3A5F;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("## 🏗️ Elite Wall Systems")
    if DEMO_MODE:
        st.success("🎮 **DEMO MODE** - Sample data loaded")
    st.markdown("---")
    st.markdown("### Navigation")
    st.markdown("""
    - 📊 **Dashboard** (Home)
    - 📋 Jobs
    - 💰 Cost Entry
    - 👥 Customers
    - 🏪 Vendors
    - 📈 Reports
    """)
    st.markdown("---")
    st.caption("v1.0 | Google Sheets Backend")
    
    # Initialize sheets button (for first-time setup)
    if st.button("🔄 Initialize Sheets"):
        with st.spinner("Setting up sheets..."):
            initialize_sheets()
            st.success("Sheets initialized!")
            st.rerun()

# Main content
st.markdown('<p class="main-header">🏗️ Elite Wall Systems</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Job Costing Dashboard</p>', unsafe_allow_html=True)

# Load data
try:
    jobs = get_all_jobs()
    customers = get_all_customers()
except Exception as e:
    st.error(f"⚠️ Error loading data: {e}")
    st.stop()

# Calculate metrics
active_jobs = [j for j in jobs if j.get("status") == "active"]
total_contract_value = sum(float(j.get("contract_amount", 0) or 0) for j in active_jobs)
total_approved_cos = sum(float(j.get("approved_change_orders", 0) or 0) for j in active_jobs)

# Calculate total costs across all active jobs
total_costs = 0
over_budget_jobs = 0
for job in active_jobs:
    totals = get_job_cost_totals(job["id"])
    job_cost = totals.get("total", 0)
    total_costs += job_cost
    
    # Check if over budget
    job_budget = sum([
        float(job.get("budget_insurance", 0) or 0),
        float(job.get("budget_labor", 0) or 0),
        float(job.get("budget_stamps", 0) or 0),
        float(job.get("budget_material", 0) or 0),
        float(job.get("budget_subs_bond", 0) or 0),
        float(job.get("budget_equipment", 0) or 0),
    ])
    if job_budget > 0 and job_cost > job_budget:
        over_budget_jobs += 1

# KPI Cards
st.markdown("### 📊 Key Metrics")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Active Jobs",
        value=len(active_jobs),
        delta=f"{len(jobs)} total"
    )

with col2:
    st.metric(
        label="Total Contract Value",
        value=format_currency(total_contract_value),
        delta=format_currency(total_approved_cos) + " in COs"
    )

with col3:
    st.metric(
        label="Total Costs (Active)",
        value=format_currency(total_costs)
    )

with col4:
    st.metric(
        label="Over Budget Jobs",
        value=over_budget_jobs,
        delta="attention needed" if over_budget_jobs > 0 else "all on track",
        delta_color="inverse" if over_budget_jobs > 0 else "normal"
    )

st.markdown("---")

# Active Jobs Table
st.markdown("### 📋 Active Jobs")

if active_jobs:
    job_data = []
    for job in active_jobs:
        customer_name = job.get("customers", {}).get("name", "N/A") if job.get("customers") else "N/A"
        totals = get_job_cost_totals(job["id"])
        total_revenue = float(job.get("contract_amount", 0) or 0) + float(job.get("approved_change_orders", 0) or 0)
        total_budget = sum([
            float(job.get("budget_insurance", 0) or 0),
            float(job.get("budget_labor", 0) or 0),
            float(job.get("budget_stamps", 0) or 0),
            float(job.get("budget_material", 0) or 0),
            float(job.get("budget_subs_bond", 0) or 0),
            float(job.get("budget_equipment", 0) or 0),
        ])
        total_cost = totals.get("total", 0)
        
        profit = total_revenue - total_cost if total_revenue > 0 else 0
        profit_pct = (profit / total_revenue * 100) if total_revenue > 0 else 0
        budget_pct = (total_cost / total_budget * 100) if total_budget > 0 else 0
        status_indicator = "🟢" if budget_pct <= 90 else ("🟡" if budget_pct <= 100 else "🔴")
        
        job_data.append({
            "Status": status_indicator,
            "Job #": job.get("job_number"),
            "Job Name": job.get("job_name"),
            "Customer": customer_name,
            "Contract": format_currency(job.get("contract_amount", 0)),
            "Total Revenue": format_currency(total_revenue),
            "Total Cost": format_currency(total_cost),
            "Budget Used": f"{budget_pct:.0f}%",
            "Profit": format_currency(profit),
            "Margin": f"{profit_pct:.1f}%"
        })
    
    st.dataframe(job_data, use_container_width=True, hide_index=True)
else:
    st.info("No active jobs found. Go to **Jobs** to create your first job.")

st.markdown("---")

# Quick Actions
st.markdown("### ⚡ Quick Actions")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("➕ New Job", use_container_width=True):
        st.switch_page("pages/2_Jobs.py")

with col2:
    if st.button("💰 Enter Costs", use_container_width=True):
        st.switch_page("pages/3_Cost_Entry.py")

with col3:
    if st.button("📈 View Reports", use_container_width=True):
        st.switch_page("pages/6_Reports.py")

# Footer
st.markdown("---")
st.caption("Elite Wall Systems Job Costing System | Powered by Google Sheets")
