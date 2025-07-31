import streamlit as st
import requests
import uuid
from typing import List, Dict, Any

API_BASE_URL = "http://localhost:8000"

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

if 'cart' not in st.session_state:
    st.session_state.cart = {}

def add_to_cart(product: Dict[str, Any], selected_options: List[Dict[str, Any]]):
    line_item_id = str(uuid.uuid4())
    options_price = sum(opt.get('price', 0) for opt in selected_options)
    st.session_state.cart[line_item_id] = {
        "product_id": product['id'], "name": product['name'], "base_price": product['price'],
        "quantity": 1, "selected_options": selected_options, "options_price": options_price
    }
    st.rerun()

def remove_from_cart(line_item_id: str):
    if line_item_id in st.session_state.cart:
        del st.session_state.cart[line_item_id]
        st.rerun()

def update_quantity(line_item_id: str, quantity: int):
    if line_item_id in st.session_state.cart:
        if quantity > 0:
            st.session_state.cart[line_item_id]['quantity'] = quantity
        else:
            del st.session_state.cart[line_item_id]
        st.rerun()

st.set_page_config(layout="wide", page_title="Point of Sale")
st.title("☕ Point of Sale (POS)")

products = get_products()

if products:
    all_categories = sorted(list(set(p['category'] for p in products)))
    categories_with_all = ["แสดงทั้งหมด"] + all_categories
else:
    categories_with_all = ["แสดงทั้งหมด"]

col_menu, col_cart = st.columns([2, 1.2])

with col_menu:
    st.header("เมนูสินค้า")
    selected_category = st.selectbox("เลือกหมวดหมู่:", options=categories_with_all)
    filtered_products = [p for p in products if selected_category == "แสดงทั้งหมด" or p['category'] == selected_category]
    
    if not filtered_products:
        st.info("ไม่พบสินค้าในหมวดหมู่นี้")
    else:
        for product in filtered_products:
            with st.expander(f"{product['name']} - {product['price']:.2f} ฿", expanded=False):
                col_img, col_details = st.columns([1, 2])
                with col_img:
                    if product.get("image_url"):
                        st.image(f"{API_BASE_URL}{product['image_url']}", use_container_width=True)
                with col_details:
                    st.subheader(product['name'])
                    selected_options = []
                    if product.get('options'):
                        for option_group in product['options']:
                            st.write(f"**{option_group['name']}**")
                            choices_data = {f"{c['name']} (+{c['price']:.2f}฿)": c for c in option_group['choices']}
                            if "ท็อปปิ้ง" in option_group['name']:
                                chosen_names = st.multiselect(f"เลือก {option_group['name']}", options=list(choices_data.keys()), key=f"options_{product['id']}_{option_group['name']}")
                                for name in chosen_names:
                                    selected_options.append(choices_data[name])
                            else:
                                chosen_name = st.radio(f"เลือก {option_group['name']}", options=list(choices_data.keys()), key=f"options_{product['id']}_{option_group['name']}", horizontal=True)
                                if chosen_name:
                                    selected_options.append(choices_data[chosen_name])
                    if st.button("✔️ ยืนยันและเพิ่มลงตะกร้า", key=f"add_{product['id']}", type="primary"):
                        add_to_cart(product, selected_options)

with col_cart:
    st.header("🛒 รายการสั่งซื้อปัจจุบัน")
    if not st.session_state.cart:
        st.info("ตะกร้าสินค้าว่างเปล่า")
    else:
        total_amount = 0.0
        header_cols = st.columns([4, 2, 2, 1])
        header_cols[0].write("**สินค้า**")
        header_cols[1].write("**จำนวน**")
        header_cols[2].write("**ราคารวม**")
        for line_item_id, details in list(st.session_state.cart.items()):
            item_cols = st.columns([4, 2, 2, 1])
            with item_cols[0]:
                st.write(details['name'])
                if details['selected_options']:
                    options_str = ", ".join([opt['name'] for opt in details['selected_options']])
                    st.caption(f"└ {options_str}")
            new_quantity = item_cols[1].number_input("Qty", min_value=0, value=details['quantity'], key=f"qty_{line_item_id}", label_visibility="collapsed")
            if new_quantity != details['quantity']:
                update_quantity(line_item_id, new_quantity)
            unit_price = details['base_price'] + details['options_price']
            item_total = unit_price * details['quantity']
            item_cols[2].write(f"{item_total:.2f}")
            if item_cols[3].button("🗑️", key=f"del_{line_item_id}"):
                remove_from_cart(line_item_id)
            total_amount += item_total
        st.divider()
        st.subheader(f"ยอดรวม: {total_amount:.2f} บาท")
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("✅ ยืนยันการสั่งซื้อ", use_container_width=True, type="primary"):
                order_items_to_send = [{"product_id": d["product_id"], "quantity": d["quantity"], "selected_options": d["selected_options"]} for d in st.session_state.cart.values()]
                if post_order(order_items_to_send):
                    st.session_state.cart = {}
                    st.balloons()
                    st.rerun()
        with col_btn2:
            if st.button("❌ ล้างตะกร้า", use_container_width=True):
                st.session_state.cart = {}
                st.rerun()