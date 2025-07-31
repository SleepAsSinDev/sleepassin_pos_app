import streamlit as st
import requests

API_BASE_URL = "http://192.168.1.50:80"

def get_products():
    try:
        response = requests.get(f"{API_BASE_URL}/products")
        response.raise_for_status()
        return response.json()
    except: return None

def create_product(name, price, category):
    try:
        response = requests.post(f"{API_BASE_URL}/products", json={"name": name, "price": price, "category": category})
        response.raise_for_status()
        st.success(f"เพิ่มสินค้า '{name}' สำเร็จ!")
        return True
    except Exception as e: return False

def delete_product(product_id):
    try:
        response = requests.delete(f"{API_BASE_URL}/products/{product_id}")
        response.raise_for_status()
        st.success("ลบสินค้าสำเร็จ!")
        return True
    except: return False

def upload_image(product_id, image_file):
    try:
        response = requests.post(f"{API_BASE_URL}/products/{product_id}/upload-image", files={'file': image_file})
        response.raise_for_status()
        st.success("อัปโหลดรูปภาพสำเร็จ!")
        return True
    except: return False

def update_product_options(product_id, options):
    try:
        response = requests.put(f"{API_BASE_URL}/products/{product_id}", json={"options": options})
        response.raise_for_status()
        st.success("บันทึก Options สำเร็จ!")
        return True
    except: return False

st.set_page_config(layout="wide", page_title="จัดการสินค้า")
st.title("📦 ระบบจัดการสินค้า (Admin Panel)")

with st.form("new_product_form", clear_on_submit=True):
    st.subheader("เพิ่มสินค้าใหม่ในเมนู")
    col1, col2 = st.columns(2)
    new_name = col1.text_input("ชื่อสินค้า")
    new_price = col1.number_input("ราคา (บาท)", min_value=0.0, format="%.2f")
    new_category = col2.text_input("หมวดหมู่")
    if st.form_submit_button("➕ เพิ่มสินค้า"):
        if new_name and new_category:
            create_product(new_name, new_price, new_category)

st.divider()
st.subheader("รายการสินค้าทั้งหมดในระบบ")
products = get_products()

if products:
    for product in products:
        product_id = product['id']
        with st.container(border=True):
            col_info, col_manage = st.columns([3, 1])
            with col_info:
                st.subheader(f"{product['name']} ({product['category']}) - {product['price']:.2f} ฿")
                if product.get('image_url'): st.image(API_BASE_URL + product['image_url'], width=150)
                st.write("**Options ปัจจุบัน:**")
                if product.get('options'):
                    for opt_group in product['options']:
                        choices_str = ", ".join([f"{c['name']} (+{c['price']:.2f}฿)" for c in opt_group['choices']])
                        st.text(f"  - {opt_group['name']}: {choices_str}")
                else: st.caption("ไม่มี")
            with col_manage:
                if st.button("🗑️ ลบสินค้านี้", key=f"delete_{product_id}", use_container_width=True):
                    if delete_product(product_id): st.rerun()
                with st.popover("📷 อัปโหลดรูป", use_container_width=True):
                    uploaded_file = st.file_uploader("เลือกรูปภาพ", type=["png", "jpg"], key=f"upload_{product_id}")
                    if uploaded_file and upload_image(product_id, uploaded_file): st.rerun()

            with st.expander("จัดการ Options"):
                if f"options_{product_id}" not in st.session_state:
                    st.session_state[f"options_{product_id}"] = product.get('options', [])
                options_in_state = st.session_state[f"options_{product_id}"]
                for i, opt_group in enumerate(options_in_state):
                    group_cols = st.columns([3, 1])
                    group_cols[0].write(f"**กลุ่ม: {opt_group['name']}**")
                    if group_cols[1].button("❌ ลบกลุ่มนี้", key=f"del_group_{product_id}_{i}"):
                        options_in_state.pop(i); st.rerun()
                    for j, choice in enumerate(opt_group['choices']):
                        choice_cols = st.columns([1, 2, 2, 1])
                        choice_cols[1].write(f"  - ตัวเลือก: {choice['name']}")
                        choice_cols[2].write(f"  - ราคาบวกเพิ่ม: {choice['price']:.2f}")
                        if choice_cols[3].button("ลบ", key=f"del_choice_{product_id}_{i}_{j}"):
                            opt_group['choices'].pop(j); st.rerun()
                st.markdown("---")
                st.write("**เพิ่มกลุ่ม Option ใหม่**")
                group_form_cols = st.columns([2, 1])
                new_group_name = group_form_cols[0].text_input("ชื่อกลุ่ม", key=f"new_group_{product_id}")
                if group_form_cols[1].button("➕ เพิ่มกลุ่ม", key=f"add_group_{product_id}"):
                    if new_group_name:
                        options_in_state.append({"name": new_group_name, "choices": []}); st.rerun()
                for i, opt_group in enumerate(options_in_state):
                    with st.container(border=True):
                        st.write(f"**เพิ่มตัวเลือกในกลุ่ม '{opt_group['name']}'**")
                        choice_form_cols = st.columns([2, 1, 1])
                        new_choice_name = choice_form_cols[0].text_input("ชื่อตัวเลือก", key=f"new_choice_name_{product_id}_{i}")
                        new_choice_price = choice_form_cols[1].number_input("ราคาบวกเพิ่ม", min_value=0.0, format="%.2f", key=f"new_choice_price_{product_id}_{i}")
                        if choice_form_cols[2].button("➕ เพิ่มตัวเลือก", key=f"add_choice_{product_id}_{i}"):
                            if new_choice_name:
                                opt_group['choices'].append({"name": new_choice_name, "price": new_choice_price}); st.rerun()
                st.markdown("---")
                if st.button("💾 บันทึกการเปลี่ยนแปลง Options ทั้งหมด", key=f"save_{product_id}", type="primary"):
                    if update_product_options(product_id, options_in_state):
                        del st.session_state[f"options_{product_id}"]; st.rerun()