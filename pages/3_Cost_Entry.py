"""
Weekly Cost Entry Page
"""
import streamlit as st
import pandas as pd
from datetime import date, timedelta
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from google_sheets import (
        get_all_jobs, get_active_jobs, get_job_by_id, get_job_cost_totals,
        get_weekly_costs_by_job, get_weekly_cost_entry, upsert_weekly_cost
    )
except:
    from demo_data import (
        get_all_jobs, get_active_jobs, get_job_by_id, get_job_cost_totals,
        get_weekly_costs_by_job, get_weekly_cost_entry, upsert_weekly_cost
    )
from utils import (
    format_currency, get_week_ending_date, get_last_n_week_endings,
    show_success_message, show_error_message, get_variance_indicator
)

st.set_page_config(page_title="Cost Entry | Elite Wall Systems", page_icon="💰", layout="wide")

st.title("💰 Weekly Cost Entry")
st.markdown("Enter actual costs for each job by week")

# Load jobs
try:
    all_jobs = get_all_jobs()
    active_jobs = get_active_jobs()
except Exception as e:
    st.error(f"Error: {e}")
    st.stop()

if not all_jobs:
    st.warning("No jobs found. Please create a job first.")
    if st.button("➕ Create New Job"):
        st.switch_page("pages/2_Jobs.py")
    st.stop()

st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    job_options = {j["id"]: f"{j['job_number']} - {j['job_name']}" for j in all_jobs}
    default_job = st.session_state.get("selected_job_id")
    if default_job:
        del st.session_state.selected_job_id
    
    job_ids = list(job_options.keys())
    default_idx = job_ids.index(default_job) if default_job and default_job in job_ids else 0
    selected_job_id = st.selectbox("Select Job", job_ids, format_func=lambda x: job_options[x], index=default_idx)

with col2:
    week_options = get_last_n_week_endings(12)
    selected_week = st.selectbox("Week Ending", week_options, format_func=lambda x: x.strftime("%m/%d/%Y (%A)"))

if selected_job_id:
    job = get_job_by_id(selected_job_id)
    totals = get_job_cost_totals(selected_job_id)
    existing_entry = get_weekly_cost_entry(selected_job_id, str(selected_week))
    
    if job:
        st.markdown("---")
        customer_name = job.get("customers", {}).get("name", "N/A") if job.get("customers") else "N/A"
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"**Customer:** {customer_name}")
            st.markdown(f"**Status:** {job.get('status', 'N/A').upper()}")
        with col2:
            contract = float(job.get("contract_amount", 0) or 0)
            approved = float(job.get("approved_change_orders", 0) or 0)
            st.markdown(f"**Contract:** {format_currency(contract)}")
            st.markdown(f"**Total Revenue:** {format_currency(contract + approved)}")
        with col3:
            st.markdown(f"**Total Cost to Date:** {format_currency(totals.get('total', 0))}")
            st.markdown(f"**Man Days to Date:** {totals.get('man_days', 0)}")
        
        st.markdown("---")
        st.markdown(f"### Enter Costs for Week Ending {selected_week.strftime('%m/%d/%Y')}")
        
        if existing_entry:
            st.info("📝 Existing entry found. Values shown below can be updated.")
        
        with st.form("cost_entry_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Cost Categories")
                
                st.markdown("**Insurance (WC)**")
                insurance = st.number_input("Insurance Actual ($)", min_value=0.0,
                    value=float(existing_entry.get("insurance_actual", 0) if existing_entry else 0), step=100.0)
                budget_ins = float(job.get("budget_insurance", 0) or 0)
                st.caption(f"Budget: {format_currency(budget_ins)} | To Date: {format_currency(totals.get('insurance', 0))}")
                
                st.markdown("**Labor (incl. PR Taxes)**")
                labor = st.number_input("Labor Actual ($)", min_value=0.0,
                    value=float(existing_entry.get("labor_actual", 0) if existing_entry else 0), step=100.0)
                budget_labor = float(job.get("budget_labor", 0) or 0)
                st.caption(f"Budget: {format_currency(budget_labor)} | To Date: {format_currency(totals.get('labor', 0))}")
                
                st.markdown("**Stamps (Union)**")
                stamps = st.number_input("Stamps Actual ($)", min_value=0.0,
                    value=float(existing_entry.get("stamps_actual", 0) if existing_entry else 0), step=100.0)
                budget_stamps = float(job.get("budget_stamps", 0) or 0)
                st.caption(f"Budget: {format_currency(budget_stamps)} | To Date: {format_currency(totals.get('stamps', 0))}")
            
            with col2:
                st.markdown("####  ")
                
                st.markdown("**Materials**")
                material = st.number_input("Material Actual ($)", min_value=0.0,
                    value=float(existing_entry.get("material_actual", 0) if existing_entry else 0), step=100.0)
                budget_mat = float(job.get("budget_material", 0) or 0)
                st.caption(f"Budget: {format_currency(budget_mat)} | To Date: {format_currency(totals.get('material', 0))}")
                
                st.markdown("**Subcontractors & Bond**")
                subs = st.number_input("Subs/Bond Actual ($)", min_value=0.0,
                    value=float(existing_entry.get("subs_bond_actual", 0) if existing_entry else 0), step=100.0)
                budget_subs = float(job.get("budget_subs_bond", 0) or 0)
                st.caption(f"Budget: {format_currency(budget_subs)} | To Date: {format_currency(totals.get('subs_bond', 0))}")
                
                st.markdown("**Equipment**")
                equipment = st.number_input("Equipment Actual ($)", min_value=0.0,
                    value=float(existing_entry.get("equipment_actual", 0) if existing_entry else 0), step=100.0)
                budget_equip = float(job.get("budget_equipment", 0) or 0)
                st.caption(f"Budget: {format_currency(budget_equip)} | To Date: {format_currency(totals.get('equipment', 0))}")
            
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                man_days = st.number_input("Man Days This Week", min_value=0,
                    value=int(existing_entry.get("man_days_actual", 0) if existing_entry else 0), step=1)
                budget_md = int(job.get("budget_man_days", 0) or 0)
                st.caption(f"Budget: {budget_md} | To Date: {totals.get('man_days', 0)}")
            with col2:
                notes = st.text_area("Notes", value=existing_entry.get("notes", "") if existing_entry else "")
            
            weekly_total = insurance + labor + stamps + material + subs + equipment
            st.markdown(f"### Week Total: {format_currency(weekly_total)}")
            
            submitted = st.form_submit_button("💾 Save Week Entry", type="primary", use_container_width=True)
            
            if submitted:
                cost_data = {
                    "job_id": selected_job_id,
                    "week_ending": str(selected_week),
                    "insurance_actual": insurance,
                    "labor_actual": labor,
                    "stamps_actual": stamps,
                    "material_actual": material,
                    "subs_bond_actual": subs,
                    "equipment_actual": equipment,
                    "man_days_actual": man_days,
                    "notes": notes
                }
                
                try:
                    upsert_weekly_cost(cost_data)
                    show_success_message(f"Week ending {selected_week.strftime('%m/%d/%Y')} saved!")
                    st.rerun()
                except Exception as e:
                    show_error_message(f"Error: {e}")
        
        # Cost History
        st.markdown("---")
        st.markdown("### 📊 Cost History for This Job")
        
        history = get_weekly_costs_by_job(selected_job_id)
        if history:
            history_df = pd.DataFrame(history)
            display_cols = ["week_ending", "insurance_actual", "labor_actual", "stamps_actual", 
                          "material_actual", "subs_bond_actual", "equipment_actual", "man_days_actual"]
            available_cols = [c for c in display_cols if c in history_df.columns]
            display_df = history_df[available_cols].copy()
            
            col_names = {
                "week_ending": "Week Ending", "insurance_actual": "Insurance", "labor_actual": "Labor",
                "stamps_actual": "Stamps", "material_actual": "Materials", "subs_bond_actual": "Subs/Bond",
                "equipment_actual": "Equipment", "man_days_actual": "Man Days"
            }
            display_df = display_df.rename(columns=col_names)
            
            # Add weekly total
            cost_cols = ["Insurance", "Labor", "Stamps", "Materials", "Subs/Bond", "Equipment"]
            available_cost_cols = [c for c in cost_cols if c in display_df.columns]
            display_df["Weekly Total"] = display_df[available_cost_cols].sum(axis=1)
            
            for col in available_cost_cols + ["Weekly Total"]:
                display_df[col] = display_df[col].apply(lambda x: format_currency(x))
            
            st.dataframe(display_df, use_container_width=True, hide_index=True)
        else:
            st.info("No cost entries yet for this job.")
        
        # Budget vs Actual Summary
        st.markdown("---")
        st.markdown("### 📈 Budget vs Actual Summary")
        
        summary_data = {
            "Category": ["Insurance", "Labor", "Stamps", "Materials", "Subs/Bond", "Equipment", "TOTAL"],
            "Budget": [
                float(job.get("budget_insurance", 0) or 0),
                float(job.get("budget_labor", 0) or 0),
                float(job.get("budget_stamps", 0) or 0),
                float(job.get("budget_material", 0) or 0),
                float(job.get("budget_subs_bond", 0) or 0),
                float(job.get("budget_equipment", 0) or 0),
                sum([float(job.get(f"budget_{k}", 0) or 0) for k in ["insurance", "labor", "stamps", "material", "subs_bond", "equipment"]])
            ],
            "Actual": [
                totals.get("insurance", 0), totals.get("labor", 0), totals.get("stamps", 0),
                totals.get("material", 0), totals.get("subs_bond", 0), totals.get("equipment", 0),
                totals.get("total", 0)
            ]
        }
        
        summary_df = pd.DataFrame(summary_data)
        summary_df["Variance"] = summary_df["Actual"] - summary_df["Budget"]
        summary_df["% Used"] = summary_df.apply(
            lambda row: f"{(row['Actual'] / row['Budget'] * 100):.1f}%" if row['Budget'] > 0 else "N/A", axis=1)
        summary_df["Status"] = summary_df.apply(
            lambda row: get_variance_indicator(row['Actual'], row['Budget']), axis=1)
        
        for col in ["Budget", "Actual", "Variance"]:
            summary_df[col] = summary_df[col].apply(format_currency)
        
        st.dataframe(summary_df, use_container_width=True, hide_index=True)
