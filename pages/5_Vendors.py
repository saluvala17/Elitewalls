"""
Vendors Management Page
"""
import streamlit as st
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from google_sheets import (
        get_all_vendors, get_vendor_by_id,
        create_vendor, update_vendor, delete_vendor
    )
except:
    from demo_data import (
        get_all_vendors, get_vendor_by_id,
        create_vendor, update_vendor, delete_vendor
    )
from utils import show_success_message, show_error_message

st.set_page_config(page_title="Vendors | Elite Wall Systems", page_icon="🏪", layout="wide")

st.title("🏪 Vendor Management")
st.markdown("Manage your suppliers, subcontractors, and equipment vendors")

if "edit_vendor_id" not in st.session_state:
    st.session_state.edit_vendor_id = None

try:
    vendors = get_all_vendors()
except Exception as e:
    st.error(f"Error: {e}")
    st.stop()

type_icons = {"supplier": "📦", "subcontractor": "👷", "equipment": "🚜"}

tab1, tab2 = st.tabs(["📋 All Vendors", "➕ Add New Vendor"])

with tab1:
    st.markdown("### Vendors & Suppliers")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        search = st.text_input("🔍 Search vendors...", placeholder="Company name or contact")
    with col2:
        type_filter = st.selectbox("Filter by Type", ["All", "supplier", "subcontractor", "equipment"])
    
    if vendors:
        filtered = vendors
        if search:
            search_lower = search.lower()
            filtered = [v for v in vendors if 
                       search_lower in str(v.get("name", "")).lower() or
                       search_lower in str(v.get("contact_name", "") or "").lower()]
        if type_filter != "All":
            filtered = [v for v in filtered if v.get("vendor_type") == type_filter]
        
        for vendor in filtered:
            vendor_type = vendor.get("vendor_type", "supplier")
            icon = type_icons.get(vendor_type, "📦")
            
            with st.expander(f"{icon} **{vendor.get('name')}** ({vendor_type.title()})"):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Contact Information**")
                    st.write(f"👤 Contact: {vendor.get('contact_name', 'N/A')}")
                    st.write(f"📱 Phone: {vendor.get('phone', 'N/A')}")
                    st.write(f"✉️ Email: {vendor.get('email', 'N/A')}")
                with col2:
                    st.markdown("**Details**")
                    st.write(f"📋 Type: {vendor_type.title()}")
                    if vendor.get("address"):
                        st.write(f"📍 Address: {vendor.get('address')}")
                    if vendor.get("notes"):
                        st.markdown("**Notes**")
                        st.write(vendor.get("notes"))
                
                st.markdown("---")
                col1, col2, col3 = st.columns([1, 1, 2])
                with col1:
                    if st.button("✏️ Edit", key=f"edit_vend_{vendor['id']}"):
                        st.session_state.edit_vendor_id = vendor["id"]
                        st.rerun()
                with col2:
                    if st.button("🗑️ Delete", key=f"del_vend_{vendor['id']}", type="secondary"):
                        delete_vendor(vendor["id"])
                        show_success_message("Vendor removed")
                        st.rerun()
        
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📦 Suppliers", len([v for v in vendors if v.get("vendor_type") == "supplier"]))
        with col2:
            st.metric("👷 Subcontractors", len([v for v in vendors if v.get("vendor_type") == "subcontractor"]))
        with col3:
            st.metric("🚜 Equipment", len([v for v in vendors if v.get("vendor_type") == "equipment"]))
    else:
        st.info("No vendors found. Add your first vendor above.")

with tab2:
    st.markdown("### Add New Vendor")
    
    with st.form("new_vendor_form"):
        name = st.text_input("Company Name *", placeholder="e.g., ABC Materials Supply")
        vendor_type = st.selectbox("Vendor Type *", ["supplier", "subcontractor", "equipment"])
        contact_name = st.text_input("Contact Name", placeholder="e.g., Jane Doe")
        col1, col2 = st.columns(2)
        with col1:
            phone = st.text_input("Phone", placeholder="e.g., 212-555-0200")
        with col2:
            email = st.text_input("Email", placeholder="e.g., orders@company.com")
        address = st.text_area("Address", placeholder="Street, City, State, ZIP")
        notes = st.text_area("Notes", placeholder="Payment terms, specialties, etc.")
        
        submitted = st.form_submit_button("✅ Add Vendor", type="primary", use_container_width=True)
        
        if submitted:
            if not name:
                show_error_message("Company name is required")
            else:
                existing = [str(v.get("name", "")).lower() for v in vendors]
                if name.lower() in existing:
                    show_error_message(f"Vendor '{name}' already exists")
                else:
                    data = {"name": name, "vendor_type": vendor_type, "contact_name": contact_name,
                           "phone": phone, "email": email, "address": address, "notes": notes}
                    try:
                        create_vendor(data)
                        show_success_message(f"Vendor '{name}' added!")
                        st.rerun()
                    except Exception as e:
                        show_error_message(f"Error: {e}")

if st.session_state.edit_vendor_id:
    vendor = get_vendor_by_id(st.session_state.edit_vendor_id)
    if vendor:
        st.markdown("---")
        st.markdown(f"### ✏️ Edit Vendor: {vendor.get('name')}")
        
        with st.form("edit_vendor_form"):
            edit_name = st.text_input("Company Name", value=vendor.get("name", ""))
            type_list = ["supplier", "subcontractor", "equipment"]
            current_type = vendor.get("vendor_type", "supplier")
            type_idx = type_list.index(current_type) if current_type in type_list else 0
            edit_type = st.selectbox("Vendor Type", type_list, index=type_idx)
            edit_contact = st.text_input("Contact Name", value=vendor.get("contact_name", "") or "")
            col1, col2 = st.columns(2)
            with col1:
                edit_phone = st.text_input("Phone", value=vendor.get("phone", "") or "")
            with col2:
                edit_email = st.text_input("Email", value=vendor.get("email", "") or "")
            edit_address = st.text_area("Address", value=vendor.get("address", "") or "")
            edit_notes = st.text_area("Notes", value=vendor.get("notes", "") or "")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("💾 Save Changes", type="primary"):
                    data = {"name": edit_name, "vendor_type": edit_type, "contact_name": edit_contact,
                           "phone": edit_phone, "email": edit_email, "address": edit_address, "notes": edit_notes}
                    try:
                        update_vendor(st.session_state.edit_vendor_id, data)
                        show_success_message("Vendor updated!")
                        st.session_state.edit_vendor_id = None
                        st.rerun()
                    except Exception as e:
                        show_error_message(f"Error: {e}")
            with col2:
                if st.form_submit_button("❌ Cancel"):
                    st.session_state.edit_vendor_id = None
                    st.rerun()
