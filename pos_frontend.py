# 1_🛒_Point_of_Sale.py (Updated with Grid Card Layout)

import streamlit as st
import requests
# ไม่ต้องการ Pandas ในหน้านี้แล้ว สามารถลบออกได้
# import pandas as pd 
from typing import List, Dict, Any

# -----------------------------------------------------------------------------
# ⚙️ การตั้งค่าและฟังก์ชัน API (เหมือนเดิม)
# -----------------------------------------------------------------------------
API_BASE_URL = "http://192.168.1.145:8000"

def get_products() -> List[Dict[str, Any]]:
    try:
        response = requests.get(f"{API_BASE_URL}/products")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"ไม่สามารถเชื่อมต่อกับ API ได้: {e}")
        return []

def post_order(order_items: List[Dict[str, Any]]) -> bool:
    order_data_to_send = {"items": order_items}
    try:
        response = requests.post(f"{API_BASE_URL}/orders", json=order_data_to_send)
        response.raise_for_status()
        st.success(f"บันทึกออเดอร์สำเร็จ! หมายเลขออเดอร์: {response.json().get('id')}")
        return True
    except requests.exceptions.RequestException as e:
        st.error(f"ไม่สามารถบันทึกออเดอร์ได้: {e.response.json().get('detail')}")
        return False

# -----------------------------------------------------------------------------
# 🛒 การจัดการสถานะของแอป (ตะกร้าสินค้า) (เหมือนเดิม)
# -----------------------------------------------------------------------------
if 'cart' not in st.session_state:
    st.session_state.cart = {}

def add_to_cart(product_id: str, name: str, price: float):
    if product_id in st.session_state.cart:
        st.session_state.cart[product_id]['quantity'] += 1
    else:
        st.session_state.cart[product_id] = {"name": name, "price": price, "quantity": 1}
    st.rerun()

def remove_from_cart(product_id: str):
    if product_id in st.session_state.cart:
        del st.session_state.cart[product_id]
        st.rerun()

def update_quantity(product_id: str, quantity: int):
    if product_id in st.session_state.cart:
        if quantity > 0:
            st.session_state.cart[product_id]['quantity'] = quantity
        else:
            del st.session_state.cart[product_id]
        st.rerun()

# -----------------------------------------------------------------------------
# 🖼️ ส่วนแสดงผล (UI Layout)
# -----------------------------------------------------------------------------

st.set_page_config(layout="wide", page_title="Point of Sale")
st.title("☕ Point of Sale (POS)")

products = get_products()

if products:
    all_categories = sorted(list(set(p['category'] for p in products)))
    categories_with_all = ["แสดงทั้งหมด"] + all_categories
else:
    categories_with_all = ["แสดงทั้งหมด"]

col_menu, col_cart = st.columns([2, 1.2])

# --- คอลัมน์ซ้าย: แสดงเมนูสินค้า (ปรับปรุงเป็น Grid Card Layout) ---
with col_menu:
    st.header("เมนูสินค้า")

    selected_category = st.selectbox(
        "เลือกหมวดหมู่:",
        options=categories_with_all,
        key="category_filter"
    )

    if selected_category == "แสดงทั้งหมด":
        filtered_products = products
    else:
        filtered_products = [p for p in products if p['category'] == selected_category]
    
    if not filtered_products:
        st.info("ไม่พบสินค้าในระบบ" if selected_category == "แสดงทั้งหมด" else "ไม่พบสินค้าในหมวดหมู่นี้")
    else:
        # --- ส่วนที่เปลี่ยนแปลง: สร้าง Grid Layout ---
        num_columns = 3  # แสดงแถวละ 3 รายการ (ปรับเปลี่ยนได้ตามต้องการ)
        cols = st.columns(num_columns)
        
        # วนลูปเพื่อแสดงสินค้าลงในแต่ละคอลัมน์ของ Grid
        for i, product in enumerate(filtered_products):
            col_index = i % num_columns
            with cols[col_index]:
                with st.container(border=True, height=350): # กำหนดความสูงของการ์ดให้เท่ากัน
                    # แสดงรูปภาพให้เต็มความกว้างของ container
                    if product.get("image_url"):
                        st.image(
                            f"{API_BASE_URL}{product['image_url']}",
                            use_container_width=True
                        )
                    
                    st.subheader(f"{product['name']}")
                    st.write(f"**ราคา: {product['price']:.2f} ฿**")

                    # ปุ่มเพิ่มลงตะกร้า
                    if st.button("➕ เพิ่มลงตะกร้า", key=f"add_{product['id']}", use_container_width=True):
                        add_to_cart(
                            product_id=product['id'],
                            name=product['name'],
                            price=product['price']
                        )

# --- คอลัมน์ขวา: แสดงตะกร้าสินค้าและยอดรวม (เหมือนเดิม) ---
with col_cart:
    st.header("🛒 รายการสั่งซื้อปัจจุบัน")
    
    if not st.session_state.cart:
        st.info("ตะกร้าสินค้าว่างเปล่า")
    else:
        # ... (ส่วนนี้เหมือนเดิมทั้งหมด) ...
        total_amount = 0.0
        header_cols = st.columns([3, 2, 2, 1])
        header_cols[0].write("**สินค้า**")
        header_cols[1].write("**จำนวน**")
        header_cols[2].write("**ราคารวม**")
        
        for product_id, item_details in list(st.session_state.cart.items()):
            item_cols = st.columns([3, 2, 2, 1])
            item_cols[0].write(item_details['name'])
            new_quantity = item_cols[1].number_input(
                "Qty", min_value=0, value=item_details['quantity'], 
                key=f"qty_{product_id}", label_visibility="collapsed"
            )
            if new_quantity != item_details['quantity']:
                update_quantity(product_id, new_quantity)
            item_total = item_details['price'] * item_details['quantity']
            item_cols[2].write(f"{item_total:.2f}")
            if item_cols[3].button("🗑️", key=f"del_{product_id}"):
                remove_from_cart(product_id)
            total_amount += item_total

        st.divider()
        st.subheader(f"ยอดรวม: {total_amount:.2f} บาท")
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("✅ ยืนยันการสั่งซื้อ", use_container_width=True, type="primary"):
                order_items_to_send = [
                    {"product_id": pid, "quantity": details["quantity"]}
                    for pid, details in st.session_state.cart.items()
                ]
                if post_order(order_items_to_send):
                    st.session_state.cart = {}
                    st.balloons()
                    st.rerun()
        with col_btn2:
            if st.button("❌ ล้างตะกร้า", use_container_width=True):
                st.session_state.cart = {}
                st.rerun()