"""
Google Sheets Database Module
Handles all read/write operations to Google Sheets
"""
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import json
import os

# Google Sheets scope
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

# Sheet names (tabs in your Google Sheet)
SHEET_JOBS = "Jobs"
SHEET_CUSTOMERS = "Customers"
SHEET_VENDORS = "Vendors"
SHEET_WEEKLY_COSTS = "WeeklyCosts"


@st.cache_resource
def get_google_sheets_client():
    """
    Create and cache Google Sheets client connection.
    Uses service account credentials from secrets or file.
    """
    try:
        # Try Streamlit secrets first (for deployment)
        if "gcp_service_account" in st.secrets:
            creds_dict = dict(st.secrets["gcp_service_account"])
            creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        else:
            # Fall back to local credentials file
            creds_path = os.path.join(os.path.dirname(__file__), '..', 'credentials.json')
            if os.path.exists(creds_path):
                creds = Credentials.from_service_account_file(creds_path, scopes=SCOPES)
            else:
                st.error("⚠️ Google credentials not found. See README for setup instructions.")
                st.stop()
        
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        st.error(f"⚠️ Failed to connect to Google Sheets: {e}")
        st.stop()


def get_spreadsheet():
    """Get the main spreadsheet"""
    client = get_google_sheets_client()
    
    # Try to get spreadsheet ID from secrets or environment
    try:
        spreadsheet_id = st.secrets.get("SPREADSHEET_ID", os.getenv("SPREADSHEET_ID"))
    except:
        spreadsheet_id = os.getenv("SPREADSHEET_ID")
    
    if not spreadsheet_id:
        st.error("⚠️ SPREADSHEET_ID not configured. Add it to .streamlit/secrets.toml or .env")
        st.stop()
    
    return client.open_by_key(spreadsheet_id)


def get_worksheet(sheet_name):
    """Get a specific worksheet (tab) by name"""
    spreadsheet = get_spreadsheet()
    try:
        return spreadsheet.worksheet(sheet_name)
    except gspread.WorksheetNotFound:
        # Create the worksheet if it doesn't exist
        return create_worksheet(spreadsheet, sheet_name)


def create_worksheet(spreadsheet, sheet_name):
    """Create a new worksheet with appropriate headers"""
    headers = {
        SHEET_JOBS: [
            "id", "job_number", "job_name", "customer_id", "contract_amount",
            "pending_change_orders", "approved_change_orders", "status",
            "start_date", "end_date", "budget_insurance", "budget_labor",
            "budget_stamps", "budget_material", "budget_subs_bond",
            "budget_equipment", "budget_man_days", "notes", "created_at", "updated_at"
        ],
        SHEET_CUSTOMERS: [
            "id", "name", "contact_name", "phone", "email", "address",
            "notes", "is_active", "created_at"
        ],
        SHEET_VENDORS: [
            "id", "name", "vendor_type", "contact_name", "phone", "email",
            "address", "notes", "is_active", "created_at"
        ],
        SHEET_WEEKLY_COSTS: [
            "id", "job_id", "week_ending", "insurance_actual", "labor_actual",
            "stamps_actual", "material_actual", "subs_bond_actual",
            "equipment_actual", "man_days_actual", "notes", "created_at"
        ]
    }
    
    worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=25)
    if sheet_name in headers:
        worksheet.append_row(headers[sheet_name])
    return worksheet


def generate_id():
    """Generate a unique ID"""
    return datetime.now().strftime("%Y%m%d%H%M%S%f")


def sheet_to_dataframe(worksheet):
    """Convert worksheet to pandas DataFrame"""
    data = worksheet.get_all_records()
    return pd.DataFrame(data) if data else pd.DataFrame()


def dataframe_to_sheet(worksheet, df):
    """Write entire DataFrame to worksheet (replaces all data)"""
    worksheet.clear()
    if not df.empty:
        worksheet.update([df.columns.values.tolist()] + df.values.tolist())


# ============================================
# CUSTOMER OPERATIONS
# ============================================
def get_all_customers():
    """Get all active customers"""
    ws = get_worksheet(SHEET_CUSTOMERS)
    df = sheet_to_dataframe(ws)
    if df.empty:
        return []
    # Filter active customers
    if 'is_active' in df.columns:
        df = df[df['is_active'] != False]
        df = df[df['is_active'] != 'False']
        df = df[df['is_active'] != 'FALSE']
    return df.to_dict('records')


def get_customer_by_id(customer_id):
    """Get single customer by ID"""
    customers = get_all_customers()
    for c in customers:
        if str(c.get('id')) == str(customer_id):
            return c
    return None


def create_customer(data):
    """Create new customer"""
    ws = get_worksheet(SHEET_CUSTOMERS)
    data['id'] = generate_id()
    data['is_active'] = True
    data['created_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Get headers and create row in correct order
    headers = ws.row_values(1)
    row = [data.get(h, '') for h in headers]
    ws.append_row(row)
    return data


def update_customer(customer_id, data):
    """Update existing customer"""
    ws = get_worksheet(SHEET_CUSTOMERS)
    df = sheet_to_dataframe(ws)
    
    # Find and update the row
    mask = df['id'].astype(str) == str(customer_id)
    if mask.any():
        for key, value in data.items():
            if key in df.columns:
                df.loc[mask, key] = value
        dataframe_to_sheet(ws, df)
    return data


def delete_customer(customer_id):
    """Soft delete customer (set inactive)"""
    return update_customer(customer_id, {'is_active': False})


# ============================================
# VENDOR OPERATIONS
# ============================================
def get_all_vendors():
    """Get all active vendors"""
    ws = get_worksheet(SHEET_VENDORS)
    df = sheet_to_dataframe(ws)
    if df.empty:
        return []
    if 'is_active' in df.columns:
        df = df[df['is_active'] != False]
        df = df[df['is_active'] != 'False']
        df = df[df['is_active'] != 'FALSE']
    return df.to_dict('records')


def get_vendor_by_id(vendor_id):
    """Get single vendor by ID"""
    vendors = get_all_vendors()
    for v in vendors:
        if str(v.get('id')) == str(vendor_id):
            return v
    return None


def create_vendor(data):
    """Create new vendor"""
    ws = get_worksheet(SHEET_VENDORS)
    data['id'] = generate_id()
    data['is_active'] = True
    data['created_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    headers = ws.row_values(1)
    row = [data.get(h, '') for h in headers]
    ws.append_row(row)
    return data


def update_vendor(vendor_id, data):
    """Update existing vendor"""
    ws = get_worksheet(SHEET_VENDORS)
    df = sheet_to_dataframe(ws)
    
    mask = df['id'].astype(str) == str(vendor_id)
    if mask.any():
        for key, value in data.items():
            if key in df.columns:
                df.loc[mask, key] = value
        dataframe_to_sheet(ws, df)
    return data


def delete_vendor(vendor_id):
    """Soft delete vendor"""
    return update_vendor(vendor_id, {'is_active': False})


# ============================================
# JOB OPERATIONS
# ============================================
def get_all_jobs():
    """Get all jobs with customer info"""
    ws = get_worksheet(SHEET_JOBS)
    df = sheet_to_dataframe(ws)
    if df.empty:
        return []
    
    # Get customers for lookup
    customers = {str(c['id']): c for c in get_all_customers()}
    
    jobs = df.to_dict('records')
    for job in jobs:
        customer_id = str(job.get('customer_id', ''))
        if customer_id in customers:
            job['customers'] = {'name': customers[customer_id].get('name', '')}
        else:
            job['customers'] = None
        
        # Convert numeric fields
        for field in ['contract_amount', 'pending_change_orders', 'approved_change_orders',
                     'budget_insurance', 'budget_labor', 'budget_stamps', 'budget_material',
                     'budget_subs_bond', 'budget_equipment', 'budget_man_days']:
            try:
                job[field] = float(job.get(field, 0) or 0)
            except:
                job[field] = 0
    
    return jobs


def get_active_jobs():
    """Get only active jobs"""
    jobs = get_all_jobs()
    return [j for j in jobs if j.get('status') == 'active']


def get_job_by_id(job_id):
    """Get single job by ID"""
    jobs = get_all_jobs()
    for j in jobs:
        if str(j.get('id')) == str(job_id):
            return j
    return None


def create_job(data):
    """Create new job"""
    ws = get_worksheet(SHEET_JOBS)
    data['id'] = generate_id()
    data['created_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data['updated_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    headers = ws.row_values(1)
    row = [data.get(h, '') for h in headers]
    ws.append_row(row)
    return data


def update_job(job_id, data):
    """Update existing job"""
    ws = get_worksheet(SHEET_JOBS)
    df = sheet_to_dataframe(ws)
    
    data['updated_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    mask = df['id'].astype(str) == str(job_id)
    if mask.any():
        for key, value in data.items():
            if key in df.columns:
                df.loc[mask, key] = value
        dataframe_to_sheet(ws, df)
    return data


def delete_job(job_id):
    """Delete job"""
    ws = get_worksheet(SHEET_JOBS)
    df = sheet_to_dataframe(ws)
    df = df[df['id'].astype(str) != str(job_id)]
    dataframe_to_sheet(ws, df)
    
    # Also delete related weekly costs
    ws_costs = get_worksheet(SHEET_WEEKLY_COSTS)
    df_costs = sheet_to_dataframe(ws_costs)
    if not df_costs.empty:
        df_costs = df_costs[df_costs['job_id'].astype(str) != str(job_id)]
        dataframe_to_sheet(ws_costs, df_costs)


# ============================================
# WEEKLY COST OPERATIONS
# ============================================
def get_weekly_costs_by_job(job_id):
    """Get all weekly cost entries for a job"""
    ws = get_worksheet(SHEET_WEEKLY_COSTS)
    df = sheet_to_dataframe(ws)
    if df.empty:
        return []
    
    df = df[df['job_id'].astype(str) == str(job_id)]
    
    # Convert numeric fields
    for col in ['insurance_actual', 'labor_actual', 'stamps_actual', 'material_actual',
                'subs_bond_actual', 'equipment_actual', 'man_days_actual']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # Sort by week_ending descending
    if not df.empty and 'week_ending' in df.columns:
        df = df.sort_values('week_ending', ascending=False)
    
    return df.to_dict('records')


def get_weekly_cost_entry(job_id, week_ending):
    """Get specific weekly cost entry"""
    costs = get_weekly_costs_by_job(job_id)
    for c in costs:
        if str(c.get('week_ending')) == str(week_ending):
            return c
    return None


def upsert_weekly_cost(data):
    """Insert or update weekly cost entry"""
    ws = get_worksheet(SHEET_WEEKLY_COSTS)
    df = sheet_to_dataframe(ws)
    
    job_id = str(data.get('job_id', ''))
    week_ending = str(data.get('week_ending', ''))
    
    if df.empty:
        # First entry - just append
        data['id'] = generate_id()
        data['created_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        headers = ws.row_values(1)
        row = [data.get(h, '') for h in headers]
        ws.append_row(row)
    else:
        # Check if entry exists
        mask = (df['job_id'].astype(str) == job_id) & (df['week_ending'].astype(str) == week_ending)
        
        if mask.any():
            # Update existing
            for key, value in data.items():
                if key in df.columns and key != 'id':
                    df.loc[mask, key] = value
            dataframe_to_sheet(ws, df)
        else:
            # Insert new
            data['id'] = generate_id()
            data['created_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            headers = ws.row_values(1)
            row = [data.get(h, '') for h in headers]
            ws.append_row(row)
    
    return data


def get_job_cost_totals(job_id):
    """Get total costs for a specific job"""
    costs = get_weekly_costs_by_job(job_id)
    
    if not costs:
        return {
            "insurance": 0, "labor": 0, "stamps": 0,
            "material": 0, "subs_bond": 0, "equipment": 0,
            "man_days": 0, "total": 0
        }
    
    totals = {
        "insurance": sum(float(c.get("insurance_actual", 0) or 0) for c in costs),
        "labor": sum(float(c.get("labor_actual", 0) or 0) for c in costs),
        "stamps": sum(float(c.get("stamps_actual", 0) or 0) for c in costs),
        "material": sum(float(c.get("material_actual", 0) or 0) for c in costs),
        "subs_bond": sum(float(c.get("subs_bond_actual", 0) or 0) for c in costs),
        "equipment": sum(float(c.get("equipment_actual", 0) or 0) for c in costs),
        "man_days": sum(int(float(c.get("man_days_actual", 0) or 0)) for c in costs),
    }
    totals["total"] = totals["insurance"] + totals["labor"] + totals["stamps"] + \
                      totals["material"] + totals["subs_bond"] + totals["equipment"]
    return totals


def get_all_weekly_costs():
    """Get all weekly costs with job info"""
    ws = get_worksheet(SHEET_WEEKLY_COSTS)
    df = sheet_to_dataframe(ws)
    if df.empty:
        return []
    
    # Get jobs for lookup
    jobs = {str(j['id']): j for j in get_all_jobs()}
    
    costs = df.to_dict('records')
    for cost in costs:
        job_id = str(cost.get('job_id', ''))
        if job_id in jobs:
            cost['jobs'] = {
                'job_number': jobs[job_id].get('job_number', ''),
                'job_name': jobs[job_id].get('job_name', '')
            }
        else:
            cost['jobs'] = None
        
        # Convert numeric fields
        for field in ['insurance_actual', 'labor_actual', 'stamps_actual', 'material_actual',
                     'subs_bond_actual', 'equipment_actual', 'man_days_actual']:
            try:
                cost[field] = float(cost.get(field, 0) or 0)
            except:
                cost[field] = 0
    
    return costs


# ============================================
# INITIALIZATION HELPER
# ============================================
def initialize_sheets():
    """Initialize all worksheets with headers"""
    for sheet_name in [SHEET_CUSTOMERS, SHEET_VENDORS, SHEET_JOBS, SHEET_WEEKLY_COSTS]:
        get_worksheet(sheet_name)
    return True
