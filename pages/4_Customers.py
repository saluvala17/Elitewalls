"""
Customers (General Contractors) Management Page
"""
import streamlit as st
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from google_sheets import (
        get_all_customers, get_customer_by_id,
        create_customer, update_customer, delete_customer
    )
except:
    from demo_data import (
        get_all_customers, get_customer_by_id,
        create_customer, update_customer, delete_customer
    )
from utils import show_success_message, show_error_message

st.set_page_config(page_title="Customers | Elite Wall Systems", page_icon="👥", layout="wide")

st.title("👥 Customer Management")
st.markdown("Manage your General Contractors (GCs)")

if "edit_customer_id" not in st.session_state:
    st.session_state.edit_customer_id = None

try:
    customers = get_all_customers()
except Exception as e:
    st.error(f"Error: {e}")
    st.stop()

tab1, tab2 = st.tabs(["📋 All Customers", "➕ Add New Customer"])

with tab1:
    st.markdown("### General Contractors")
    
    if customers:
        search = st.text_input("🔍 Search customers...", placeholder="Company name or contact")
        
        filtered = customers
        if search:
            search_lower = search.lower()
            filtered = [c for c in customers if 
                       search_lower in str(c.get("name", "")).lower() or
                       search_lower in str(c.get("contact_name", "") or "").lower()]
        
        for customer in filtered:
            with st.expander(f"🏢 **{customer.get('name')}**"):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Contact Information**")
                    st.write(f"📧 Contact: {customer.get('contact_name', 'N/A')}")
                    st.write(f"📱 Phone: {customer.get('phone', 'N/A')}")
                    st.write(f"✉️ Email: {customer.get('email', 'N/A')}")
                with col2:
                    st.markdown("**Address**")
                    st.write(customer.get("address", "No address on file") or "No address on file")
                    if customer.get("notes"):
                        st.markdown("**Notes**")
                        st.write(customer.get("notes"))
                
                st.markdown("---")
                col1, col2, col3 = st.columns([1, 1, 2])
                with col1:
                    if st.button("✏️ Edit", key=f"edit_cust_{customer['id']}"):
                        st.session_state.edit_customer_id = customer["id"]
                        st.rerun()
                with col2:
                    if st.button("🗑️ Delete", key=f"del_cust_{customer['id']}", type="secondary"):
                        delete_customer(customer["id"])
                        show_success_message("Customer removed")
                        st.rerun()
        
        st.markdown("---")
        st.markdown("### Quick View")
        df = pd.DataFrame(customers)
        if not df.empty:
            cols = ["name", "contact_name", "phone", "email"]
            available = [c for c in cols if c in df.columns]
            display_df = df[available].copy()
            display_df.columns = ["Company", "Contact", "Phone", "Email"][:len(available)]
            st.dataframe(display_df, use_container_width=True, hide_index=True)
    else:
        st.info("No customers found. Add your first customer above.")

with tab2:
    st.markdown("### Add New Customer (GC)")
    
    with st.form("new_customer_form"):
        name = st.text_input("Company Name *", placeholder="e.g., Promethean Construction")
        contact_name = st.text_input("Contact Name", placeholder="e.g., John Smith")
        col1, col2 = st.columns(2)
        with col1:
            phone = st.text_input("Phone", placeholder="e.g., 212-555-0100")
        with col2:
            email = st.text_input("Email", placeholder="e.g., john@company.com")
        address = st.text_area("Address", placeholder="Street, City, State, ZIP")
        notes = st.text_area("Notes", placeholder="Any additional notes...")
        
        submitted = st.form_submit_button("✅ Add Customer", type="primary", use_container_width=True)
        
        if submitted:
            if not name:
                show_error_message("Company name is required")
            else:
                existing = [str(c.get("name", "")).lower() for c in customers]
                if name.lower() in existing:
                    show_error_message(f"Customer '{name}' already exists")
                else:
                    data = {"name": name, "contact_name": contact_name, "phone": phone,
                           "email": email, "address": address, "notes": notes}
                    try:
                        create_customer(data)
                        show_success_message(f"Customer '{name}' added!")
                        st.rerun()
                    except Exception as e:
                        show_error_message(f"Error: {e}")

if st.session_state.edit_customer_id:
    customer = get_customer_by_id(st.session_state.edit_customer_id)
    if customer:
        st.markdown("---")
        st.markdown(f"### ✏️ Edit Customer: {customer.get('name')}")
        
        with st.form("edit_customer_form"):
            edit_name = st.text_input("Company Name", value=customer.get("name", ""))
            edit_contact = st.text_input("Contact Name", value=customer.get("contact_name", "") or "")
            col1, col2 = st.columns(2)
            with col1:
                edit_phone = st.text_input("Phone", value=customer.get("phone", "") or "")
            with col2:
                edit_email = st.text_input("Email", value=customer.get("email", "") or "")
            edit_address = st.text_area("Address", value=customer.get("address", "") or "")
            edit_notes = st.text_area("Notes", value=customer.get("notes", "") or "")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("💾 Save Changes", type="primary"):
                    data = {"name": edit_name, "contact_name": edit_contact, "phone": edit_phone,
                           "email": edit_email, "address": edit_address, "notes": edit_notes}
                    try:
                        update_customer(st.session_state.edit_customer_id, data)
                        show_success_message("Customer updated!")
                        st.session_state.edit_customer_id = None
                        st.rerun()
                    except Exception as e:
                        show_error_message(f"Error: {e}")
            with col2:
                if st.form_submit_button("❌ Cancel"):
                    st.session_state.edit_customer_id = None
                    st.rerun()
