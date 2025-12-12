"""
Demo Database Module
Uses in-memory data for testing UI without Google Sheets
"""
import streamlit as st
from datetime import datetime, timedelta
import random

# ============================================
# DEMO DATA STORAGE (in session state)
# ============================================

def init_demo_data():
    """Initialize demo data in session state"""
    if "demo_initialized" not in st.session_state:
        st.session_state.demo_initialized = True
        
        # Sample Customers (GCs)
        st.session_state.customers = [
            {"id": "1", "name": "Promethean Construction", "contact_name": "Mike Johnson", 
             "phone": "212-555-0101", "email": "mike@promethean.com", "address": "123 Main St, NYC", 
             "notes": "Preferred GC, always pays on time", "is_active": True, "created_at": "2024-01-15"},
            {"id": "2", "name": "Skanska USA", "contact_name": "Sarah Chen", 
             "phone": "212-555-0102", "email": "schen@skanska.com", "address": "456 Park Ave, NYC", 
             "notes": "Large commercial projects", "is_active": True, "created_at": "2024-02-01"},
            {"id": "3", "name": "Turner Construction", "contact_name": "Bob Williams", 
             "phone": "212-555-0103", "email": "bwilliams@turner.com", "address": "789 Broadway, NYC", 
             "notes": "", "is_active": True, "created_at": "2024-03-10"},
        ]
        
        # Sample Vendors
        st.session_state.vendors = [
            {"id": "1", "name": "ABC Materials Supply", "vendor_type": "supplier",
             "contact_name": "Tom Smith", "phone": "718-555-0201", "email": "orders@abcmaterials.com",
             "address": "100 Industrial Blvd, Brooklyn", "notes": "Net 30 terms", "is_active": True},
            {"id": "2", "name": "Metro Scaffolding", "vendor_type": "equipment",
             "contact_name": "Joe Martinez", "phone": "718-555-0202", "email": "joe@metroscaff.com",
             "address": "200 Warehouse St, Queens", "notes": "Weekly rental rates available", "is_active": True},
            {"id": "3", "name": "Elite Masonry Subs", "vendor_type": "subcontractor",
             "contact_name": "Frank DeLuca", "phone": "718-555-0203", "email": "frank@elitemasonry.com",
             "address": "300 Stone Ave, Bronx", "notes": "Union shop", "is_active": True},
        ]
        
        # Sample Jobs
        st.session_state.jobs = [
            {
                "id": "1", "job_number": "550", "job_name": "Linden Grove Apartments",
                "customer_id": "1", "contract_amount": 485000, "pending_change_orders": 15000,
                "approved_change_orders": 8500, "status": "active", "start_date": "2024-06-01",
                "budget_insurance": 12000, "budget_labor": 180000, "budget_stamps": 25000,
                "budget_material": 145000, "budget_subs_bond": 65000, "budget_equipment": 28000,
                "budget_man_days": 450, "notes": "Phase 1 exterior walls"
            },
            {
                "id": "2", "job_number": "548", "job_name": "Harbor View Tower",
                "customer_id": "2", "contract_amount": 720000, "pending_change_orders": 0,
                "approved_change_orders": 32000, "status": "active", "start_date": "2024-04-15",
                "budget_insurance": 18000, "budget_labor": 275000, "budget_stamps": 38000,
                "budget_material": 210000, "budget_subs_bond": 95000, "budget_equipment": 42000,
                "budget_man_days": 680, "notes": "High-rise, floors 15-30"
            },
            {
                "id": "3", "job_number": "545", "job_name": "Riverside Office Complex",
                "customer_id": "3", "contract_amount": 325000, "pending_change_orders": 5000,
                "approved_change_orders": 12000, "status": "completed", "start_date": "2024-01-10",
                "budget_insurance": 8000, "budget_labor": 125000, "budget_stamps": 17000,
                "budget_material": 98000, "budget_subs_bond": 45000, "budget_equipment": 18000,
                "budget_man_days": 310, "notes": "Completed ahead of schedule"
            },
            {
                "id": "4", "job_number": "552", "job_name": "Greenpoint Retail Center",
                "customer_id": "1", "contract_amount": 195000, "pending_change_orders": 8000,
                "approved_change_orders": 0, "status": "estimate", "start_date": "",
                "budget_insurance": 5000, "budget_labor": 72000, "budget_stamps": 10000,
                "budget_material": 58000, "budget_subs_bond": 28000, "budget_equipment": 12000,
                "budget_man_days": 180, "notes": "Awaiting permit approval"
            },
        ]
        
        # Sample Weekly Costs
        st.session_state.weekly_costs = []
        
        # Generate realistic weekly costs for active/completed jobs
        for job in st.session_state.jobs:
            if job["status"] in ["active", "completed"]:
                num_weeks = 12 if job["status"] == "active" else 18
                base_date = datetime(2024, 10, 5)  # Recent Saturdays
                
                for i in range(num_weeks):
                    week_ending = base_date - timedelta(weeks=i)
                    
                    # Randomize costs a bit
                    multiplier = random.uniform(0.8, 1.2)
                    weekly_labor = (float(job["budget_labor"]) / 20) * multiplier
                    weekly_material = (float(job["budget_material"]) / 20) * random.uniform(0.5, 1.5)
                    
                    st.session_state.weekly_costs.append({
                        "id": f"{job['id']}_{i}",
                        "job_id": job["id"],
                        "week_ending": week_ending.strftime("%Y-%m-%d"),
                        "insurance_actual": round((float(job["budget_insurance"]) / 20) * multiplier, 2),
                        "labor_actual": round(weekly_labor, 2),
                        "stamps_actual": round((float(job["budget_stamps"]) / 20) * multiplier, 2),
                        "material_actual": round(weekly_material, 2),
                        "subs_bond_actual": round((float(job["budget_subs_bond"]) / 20) * random.uniform(0, 1.5), 2),
                        "equipment_actual": round((float(job["budget_equipment"]) / 20) * multiplier, 2),
                        "man_days_actual": random.randint(15, 35),
                        "notes": "",
                        "created_at": week_ending.strftime("%Y-%m-%d")
                    })


def generate_id():
    """Generate unique ID"""
    return datetime.now().strftime("%Y%m%d%H%M%S%f")


# ============================================
# CUSTOMER OPERATIONS
# ============================================
def get_all_customers():
    init_demo_data()
    return [c for c in st.session_state.customers if c.get("is_active", True)]

def get_customer_by_id(customer_id):
    init_demo_data()
    for c in st.session_state.customers:
        if str(c["id"]) == str(customer_id):
            return c
    return None

def create_customer(data):
    init_demo_data()
    data["id"] = generate_id()
    data["is_active"] = True
    data["created_at"] = datetime.now().strftime("%Y-%m-%d")
    st.session_state.customers.append(data)
    return data

def update_customer(customer_id, data):
    init_demo_data()
    for i, c in enumerate(st.session_state.customers):
        if str(c["id"]) == str(customer_id):
            st.session_state.customers[i].update(data)
            return data
    return None

def delete_customer(customer_id):
    init_demo_data()
    for c in st.session_state.customers:
        if str(c["id"]) == str(customer_id):
            c["is_active"] = False
    return True


# ============================================
# VENDOR OPERATIONS
# ============================================
def get_all_vendors():
    init_demo_data()
    return [v for v in st.session_state.vendors if v.get("is_active", True)]

def get_vendor_by_id(vendor_id):
    init_demo_data()
    for v in st.session_state.vendors:
        if str(v["id"]) == str(vendor_id):
            return v
    return None

def create_vendor(data):
    init_demo_data()
    data["id"] = generate_id()
    data["is_active"] = True
    data["created_at"] = datetime.now().strftime("%Y-%m-%d")
    st.session_state.vendors.append(data)
    return data

def update_vendor(vendor_id, data):
    init_demo_data()
    for i, v in enumerate(st.session_state.vendors):
        if str(v["id"]) == str(vendor_id):
            st.session_state.vendors[i].update(data)
            return data
    return None

def delete_vendor(vendor_id):
    init_demo_data()
    for v in st.session_state.vendors:
        if str(v["id"]) == str(vendor_id):
            v["is_active"] = False
    return True


# ============================================
# JOB OPERATIONS
# ============================================
def get_all_jobs():
    init_demo_data()
    jobs = st.session_state.jobs.copy()
    customers = {c["id"]: c for c in st.session_state.customers}
    
    for job in jobs:
        customer_id = str(job.get("customer_id", ""))
        if customer_id in customers:
            job["customers"] = {"name": customers[customer_id]["name"]}
        else:
            job["customers"] = None
    
    return jobs

def get_active_jobs():
    return [j for j in get_all_jobs() if j.get("status") == "active"]

def get_job_by_id(job_id):
    for j in get_all_jobs():
        if str(j["id"]) == str(job_id):
            return j
    return None

def create_job(data):
    init_demo_data()
    data["id"] = generate_id()
    data["created_at"] = datetime.now().strftime("%Y-%m-%d")
    st.session_state.jobs.append(data)
    return data

def update_job(job_id, data):
    init_demo_data()
    for i, j in enumerate(st.session_state.jobs):
        if str(j["id"]) == str(job_id):
            st.session_state.jobs[i].update(data)
            return data
    return None

def delete_job(job_id):
    init_demo_data()
    st.session_state.jobs = [j for j in st.session_state.jobs if str(j["id"]) != str(job_id)]
    st.session_state.weekly_costs = [c for c in st.session_state.weekly_costs if str(c["job_id"]) != str(job_id)]
    return True


# ============================================
# WEEKLY COST OPERATIONS
# ============================================
def get_weekly_costs_by_job(job_id):
    init_demo_data()
    costs = [c for c in st.session_state.weekly_costs if str(c["job_id"]) == str(job_id)]
    return sorted(costs, key=lambda x: x["week_ending"], reverse=True)

def get_weekly_cost_entry(job_id, week_ending):
    init_demo_data()
    for c in st.session_state.weekly_costs:
        if str(c["job_id"]) == str(job_id) and str(c["week_ending"]) == str(week_ending):
            return c
    return None

def upsert_weekly_cost(data):
    init_demo_data()
    job_id = str(data["job_id"])
    week_ending = str(data["week_ending"])
    
    # Check if exists
    for i, c in enumerate(st.session_state.weekly_costs):
        if str(c["job_id"]) == job_id and str(c["week_ending"]) == week_ending:
            st.session_state.weekly_costs[i].update(data)
            return data
    
    # Create new
    data["id"] = generate_id()
    data["created_at"] = datetime.now().strftime("%Y-%m-%d")
    st.session_state.weekly_costs.append(data)
    return data

def get_job_cost_totals(job_id):
    costs = get_weekly_costs_by_job(job_id)
    
    if not costs:
        return {"insurance": 0, "labor": 0, "stamps": 0, "material": 0, 
                "subs_bond": 0, "equipment": 0, "man_days": 0, "total": 0}
    
    totals = {
        "insurance": sum(float(c.get("insurance_actual", 0) or 0) for c in costs),
        "labor": sum(float(c.get("labor_actual", 0) or 0) for c in costs),
        "stamps": sum(float(c.get("stamps_actual", 0) or 0) for c in costs),
        "material": sum(float(c.get("material_actual", 0) or 0) for c in costs),
        "subs_bond": sum(float(c.get("subs_bond_actual", 0) or 0) for c in costs),
        "equipment": sum(float(c.get("equipment_actual", 0) or 0) for c in costs),
        "man_days": sum(int(float(c.get("man_days_actual", 0) or 0)) for c in costs),
    }
    totals["total"] = sum([totals["insurance"], totals["labor"], totals["stamps"], 
                          totals["material"], totals["subs_bond"], totals["equipment"]])
    return totals

def get_all_weekly_costs():
    init_demo_data()
    costs = st.session_state.weekly_costs.copy()
    jobs = {j["id"]: j for j in st.session_state.jobs}
    
    for cost in costs:
        job_id = str(cost.get("job_id", ""))
        if job_id in jobs:
            cost["jobs"] = {"job_number": jobs[job_id]["job_number"], "job_name": jobs[job_id]["job_name"]}
        else:
            cost["jobs"] = None
    
    return costs

def initialize_sheets():
    """Dummy function for demo mode"""
    init_demo_data()
    return True
