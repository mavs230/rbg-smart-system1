import streamlit as st
import pandas as pd
import urllib.parse
from typing import List, Dict, Any

# Local imports
import utils
import config
from smart_quoter import calculate_quote

# --- 1. PAGE CONFIG & STYLING ---
st.set_page_config(page_title="RBG Smart System", page_icon="🚀", layout="wide")

# Initialize Firebase and get Firestore client
db = utils.get_firestore_client()

# --- 2. FUNCTIONS ---
def get_data() -> List[Dict[str, Any]]:
    """Fetches all material data from Firestore."""
    return utils.get_all_materials(db)

def update_stock(doc_id: str, new_stock: float) -> None:
    """
    Updates the current stock level for a given material in Firestore.
    """
    db.collection(config.MATERIAL_COLLECTION).document(doc_id).update({"current_stock": new_stock})

all_materials = get_data()
mat_names = [m.get('name') for m in all_materials] if all_materials else []

# --- 3. APP UI ---
st.title("🚀 RBG Smart System: Pro Edition")
tab1, tab2, tab3 = st.tabs(["📊 Inventory & Stock", "💰 Smart Quoter", "📩 Order Materials"])

# --- TAB 1: INVENTORY & STOCK TRACKING ---
with tab1:
    st.header("Workshop Stock Levels")
    if all_materials:
        # Create a clean table for stock
        stock_data = []
        for m in all_materials:
            # We no longer include "ID" in the display dict to keep it clean
            stock_data.append({
                "Material": m.get('name'),
                "In Stock": m.get('current_stock', 0),
                "Best Supplier": m.get('best_supplier')
            })
        
        df_stock = pd.DataFrame(stock_data)
        st.table(df_stock)

        # Stock Update Tool
        st.markdown("### Update Stock Levels")
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            target_mat = st.selectbox("Select material to update:", df_stock["Material"])
        with col_s2:
            new_val = st.number_input("New Stock Quantity:", min_value=0.0, step=1.0, key="new_stock_input")
            if st.button("Update Inventory"):
                selected_material_obj = next((m for m in all_materials if m.get('name') == target_mat), None)
                if selected_material_obj:
                    target_id = utils.generate_doc_id(selected_material_obj.get('name'))
                    update_stock(target_id, new_val)
                    st.success(f"Stock for {target_mat} updated to {new_val}!")
                else:
                    st.error(f"Material '{target_mat}' not found in database.")
                st.rerun()

# --- TAB 2: SMART QUOTER ---
with tab2:
    if all_materials:
        st.header("Project Cost Calculator")
        # (Keeping the quoter logic from previous version...)
        col_q1, col_q2 = st.columns(2)
        with col_q1:
            q_material = st.selectbox("Material:", mat_names)
            q_qty = st.number_input("Amount needed:", min_value=0.1, value=1.0)
        with col_q2:
            q_labor = st.number_input("Estimated Labor Hours:", min_value=0.0, value=1.0, step=0.5)
            q_complexity = st.slider("Job Complexity:", 1.0, 2.5, 1.0, 0.1)

        # Use the unified calculation logic
        res = calculate_quote(q_material, quantity=q_qty, labor_hours=q_labor, complexity=q_complexity)
        
        if "error" in res:
            st.error(res["error"])
        else:
            st.metric("Suggested Quote", f"R{res['Final Quote (Inc. Markup)']:,.2f}")
            st.caption(f"Includes R{res['Total Labor Cost']:,} labor and R{res['Total Material Cost']:,} materials.")

# --- TAB 3: ORDER MATERIALS (The Email Feature) ---
with tab3:
    st.header("📩 Supplier Order Automator")
    if mat_names:
        order_mat = st.selectbox("What do you need to buy?", mat_names)
        item = next((x for x in all_materials if x.get('name') == order_mat), None)

        if item:
            supplier = item.get('best_supplier')
            price = item.get('price')
            supplier_email = item.get('supplier_email', config.DEFAULT_EMAIL_DOMAIN.format(supplier_name=supplier.lower().replace(' ', ''))) # Use stored email or default

            st.info(f"The cheapest supplier is **{supplier}** at **R{price:,.2f}** per unit.")

            order_qty = st.number_input("Order Quantity:", min_value=1, value=1)

            # EMAIL LOGIC
            subject = f"ORDER REQUEST: {order_mat} - RBG Smart System"
            body = f"Hi {supplier} Team,\n\nI would like to place an order for:\n\n- Item: {order_mat}\n- Quantity: {order_qty}\n- Quoted Price: R{price:,.2f}\n\nPlease confirm availability and send through the invoice.\n\nRegards,\nRowan\nRBG Smart System"

            # Encode for URL
            mailto_link = f"mailto:{supplier_email}?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(body)}"

            st.markdown(f"""
                <a href="{mailto_link}" target="_blank">
                    <button style="background-color: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer;">
                        📧 Create Order Email for {supplier}
                    </button>
                </a>
                """, unsafe_allow_html=True)

            st.caption("Note: This will open your default email app (Outlook/Gmail) with the text ready.")
        else:
            st.warning(f"Material '{order_mat}' not found for ordering.")

st.sidebar.markdown("---")
st.sidebar.info("System: V2.0 (Stock + Ordering)")

if all_materials:
    st.sidebar.success("✅ Database Connected")
else:
    st.sidebar.warning("⚠️ Database Empty or Connecting...")
