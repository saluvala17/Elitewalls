"""
Jobs Management Page
"""
import streamlit as st
import pandas as pd
from datetime import date
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from google_sheets import (
        get_all_jobs, get_all_customers, get_job_by_id,
        create_job, update_job, delete_job, get_job_cost_totals
    )
except:
    from demo_data import (
        get_all_jobs, get_all_customers, get_job_by_id,
        create_job, update_job, delete_job, get_job_cost_totals
    )
from utils import format_currency, show_success_message, show_error_message

st.set_page_config(page_title="Jobs | Elite Wall Systems", page_icon="📋", layout="wide")

st.title("📋 Job Management")

# Initialize session state
if "edit_job_id" not in st.session_state:
    st.session_state.edit_job_id = None

# Load data
try:
    jobs = get_all_jobs()
    customers = get_all_customers()
except Exception as e:
    st.error(f"Error: {e}")
    st.stop()

customer_options_list = ["Select Customer..."] + [c["name"] for c in customers]

# Tabs
tab1, tab2 = st.tabs(["📋 All Jobs", "➕ New Job"])

# TAB 1: All Jobs List
with tab1:
    st.markdown("### Active & Completed Jobs")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        search = st.text_input("🔍 Search jobs...", placeholder="Job number or name")
    with col2:
        status_filter = st.selectbox("Filter by Status", ["All", "active", "estimate", "completed", "closed"])
    
    filtered_jobs = jobs
    if search:
        search_lower = search.lower()
        filtered_jobs = [j for j in filtered_jobs if 
                        search_lower in str(j.get("job_number", "")).lower() or
                        search_lower in str(j.get("job_name", "")).lower()]
    if status_filter != "All":
        filtered_jobs = [j for j in filtered_jobs if j.get("status") == status_filter]
    
    if filtered_jobs:
        for job in filtered_jobs:
            customer_name = job.get("customers", {}).get("name", "N/A") if job.get("customers") else "N/A"
            totals = get_job_cost_totals(job["id"])
            total_revenue = float(job.get("contract_amount", 0) or 0) + float(job.get("approved_change_orders", 0) or 0)
            total_cost = totals.get("total", 0)
            
            status_icons = {"active": "🟢", "estimate": "🟡", "completed": "🔵", "closed": "⚫"}
            status_icon = status_icons.get(job.get("status"), "⚪")
            
            with st.expander(f"{status_icon} **{job.get('job_number')}** - {job.get('job_name')} | {customer_name}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("**Contract Information**")
                    st.write(f"Contract: {format_currency(job.get('contract_amount', 0))}")
                    st.write(f"Pending COs: {format_currency(job.get('pending_change_orders', 0))}")
                    st.write(f"Approved COs: {format_currency(job.get('approved_change_orders', 0))}")
                    st.write(f"**Total Revenue: {format_currency(total_revenue)}**")
                
                with col2:
                    st.markdown("**Budget**")
                    st.write(f"Insurance: {format_currency(job.get('budget_insurance', 0))}")
                    st.write(f"Labor: {format_currency(job.get('budget_labor', 0))}")
                    st.write(f"Materials: {format_currency(job.get('budget_material', 0))}")
                    st.write(f"Subs/Bond: {format_currency(job.get('budget_subs_bond', 0))}")
                    st.write(f"Equipment: {format_currency(job.get('budget_equipment', 0))}")
                
                with col3:
                    st.markdown("**Actual Costs**")
                    st.write(f"Insurance: {format_currency(totals.get('insurance', 0))}")
                    st.write(f"Labor: {format_currency(totals.get('labor', 0))}")
                    st.write(f"Materials: {format_currency(totals.get('material', 0))}")
                    st.write(f"Subs/Bond: {format_currency(totals.get('subs_bond', 0))}")
                    st.write(f"Equipment: {format_currency(totals.get('equipment', 0))}")
                    st.write(f"**Total Cost: {format_currency(total_cost)}**")
                
                st.markdown("---")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    if st.button("✏️ Edit", key=f"edit_{job['id']}"):
                        st.session_state.edit_job_id = job["id"]
                        st.rerun()
                with col2:
                    if st.button("💰 Enter Costs", key=f"costs_{job['id']}"):
                        st.session_state.selected_job_id = job["id"]
                        st.switch_page("pages/3_Cost_Entry.py")
                with col4:
                    if st.button("🗑️ Delete", key=f"delete_{job['id']}", type="secondary"):
                        delete_job(job["id"])
                        show_success_message("Job deleted")
                        st.rerun()
    else:
        st.info("No jobs found matching your criteria")

# TAB 2: New Job Form
with tab2:
    st.markdown("### Create New Job")
    
    with st.form("new_job_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            job_number = st.text_input("Job Number *", placeholder="e.g., 550")
            job_name = st.text_input("Job Name *", placeholder="e.g., Linden Grove")
            selected_customer = st.selectbox("Customer (GC)", customer_options_list)
            customer_id = ""
            if selected_customer != "Select Customer...":
                for c in customers:
                    if c["name"] == selected_customer:
                        customer_id = c["id"]
                        break
            status = st.selectbox("Status", ["estimate", "active", "completed", "closed"])
        
        with col2:
            contract_amount = st.number_input("Contract Amount ($)", min_value=0.0, step=1000.0)
            pending_cos = st.number_input("Pending Change Orders ($)", min_value=0.0, step=100.0)
            approved_cos = st.number_input("Approved Change Orders ($)", min_value=0.0, step=100.0)
            start_date = st.date_input("Start Date", value=date.today())
        
        st.markdown("---")
        st.markdown("### Budget")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            budget_insurance = st.number_input("Insurance Budget ($)", min_value=0.0, step=100.0)
            budget_labor = st.number_input("Labor Budget ($)", min_value=0.0, step=100.0)
        with col2:
            budget_stamps = st.number_input("Stamps Budget ($)", min_value=0.0, step=100.0)
            budget_material = st.number_input("Materials Budget ($)", min_value=0.0, step=100.0)
        with col3:
            budget_subs = st.number_input("Subs/Bond Budget ($)", min_value=0.0, step=100.0)
            budget_equipment = st.number_input("Equipment Budget ($)", min_value=0.0, step=100.0)
        
        budget_man_days = st.number_input("Man Days Budget", min_value=0, step=10)
        notes = st.text_area("Notes", placeholder="Any additional notes...")
        
        submitted = st.form_submit_button("✅ Create Job", type="primary", use_container_width=True)
        
        if submitted:
            if not job_number or not job_name:
                show_error_message("Job Number and Job Name are required")
            else:
                existing_numbers = [str(j.get("job_number")) for j in jobs]
                if job_number in existing_numbers:
                    show_error_message(f"Job number {job_number} already exists")
                else:
                    job_data = {
                        "job_number": job_number,
                        "job_name": job_name,
                        "customer_id": customer_id,
                        "contract_amount": contract_amount,
                        "pending_change_orders": pending_cos,
                        "approved_change_orders": approved_cos,
                        "status": status,
                        "start_date": str(start_date),
                        "budget_insurance": budget_insurance,
                        "budget_labor": budget_labor,
                        "budget_stamps": budget_stamps,
                        "budget_material": budget_material,
                        "budget_subs_bond": budget_subs,
                        "budget_equipment": budget_equipment,
                        "budget_man_days": budget_man_days,
                        "notes": notes
                    }
                    
                    try:
                        create_job(job_data)
                        show_success_message(f"Job {job_number} created!")
                        st.rerun()
                    except Exception as e:
                        show_error_message(f"Error: {e}")

# Edit Job Modal
if st.session_state.edit_job_id:
    job = get_job_by_id(st.session_state.edit_job_id)
    
    if job:
        st.markdown("---")
        st.markdown(f"### ✏️ Edit Job: {job.get('job_number')} - {job.get('job_name')}")
        
        with st.form("edit_job_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                edit_job_name = st.text_input("Job Name", value=job.get("job_name", ""))
                current_customer_idx = 0
                if job.get("customer_id"):
                    for idx, c in enumerate(customers):
                        if str(c["id"]) == str(job.get("customer_id")):
                            current_customer_idx = idx + 1
                            break
                edit_customer = st.selectbox("Customer", customer_options_list, index=current_customer_idx)
                status_list = ["estimate", "active", "completed", "closed"]
                current_status = job.get("status", "active")
                status_idx = status_list.index(current_status) if current_status in status_list else 1
                edit_status = st.selectbox("Status", status_list, index=status_idx)
            
            with col2:
                edit_contract = st.number_input("Contract Amount ($)", value=float(job.get("contract_amount", 0) or 0))
                edit_pending = st.number_input("Pending COs ($)", value=float(job.get("pending_change_orders", 0) or 0))
                edit_approved = st.number_input("Approved COs ($)", value=float(job.get("approved_change_orders", 0) or 0))
            
            st.markdown("**Budget**")
            col1, col2, col3 = st.columns(3)
            with col1:
                edit_budget_ins = st.number_input("Insurance", value=float(job.get("budget_insurance", 0) or 0))
                edit_budget_labor = st.number_input("Labor", value=float(job.get("budget_labor", 0) or 0))
            with col2:
                edit_budget_stamps = st.number_input("Stamps", value=float(job.get("budget_stamps", 0) or 0))
                edit_budget_mat = st.number_input("Materials", value=float(job.get("budget_material", 0) or 0))
            with col3:
                edit_budget_subs = st.number_input("Subs/Bond", value=float(job.get("budget_subs_bond", 0) or 0))
                edit_budget_equip = st.number_input("Equipment", value=float(job.get("budget_equipment", 0) or 0))
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("💾 Save Changes", type="primary"):
                    edit_customer_id = ""
                    if edit_customer != "Select Customer...":
                        for c in customers:
                            if c["name"] == edit_customer:
                                edit_customer_id = c["id"]
                                break
                    
                    update_data = {
                        "job_name": edit_job_name,
                        "customer_id": edit_customer_id,
                        "status": edit_status,
                        "contract_amount": edit_contract,
                        "pending_change_orders": edit_pending,
                        "approved_change_orders": edit_approved,
                        "budget_insurance": edit_budget_ins,
                        "budget_labor": edit_budget_labor,
                        "budget_stamps": edit_budget_stamps,
                        "budget_material": edit_budget_mat,
                        "budget_subs_bond": edit_budget_subs,
                        "budget_equipment": edit_budget_equip
                    }
                    
                    try:
                        update_job(st.session_state.edit_job_id, update_data)
                        show_success_message("Job updated!")
                        st.session_state.edit_job_id = None
                        st.rerun()
                    except Exception as e:
                        show_error_message(f"Error: {e}")
            
            with col2:
                if st.form_submit_button("❌ Cancel"):
                    st.session_state.edit_job_id = None
                    st.rerun()
