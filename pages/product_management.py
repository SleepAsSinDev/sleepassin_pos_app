# pages/3_📦_Product_Management.py (Corrected Indentation)

import streamlit as st
import requests
import pandas as pd

# -----------------------------------------------------------------------------
# ⚙️ การตั้งค่าและฟังก์ชัน API
# -----------------------------------------------------------------------------

API_BASE_URL = "http://localhost:8000"

def get_products():
    try:
        response = requests.get(f"{API_BASE_URL}/products")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return None

def create_product(name: str, price: float, category: str):
    product_data = {"name": name, "price": price, "category": category}
    try:
        response = requests.post(f"{API_BASE_URL}/products", json=product_data)
        response.raise_for_status()
        st.success(f"เพิ่มสินค้า '{name}' สำเร็จ!")
        return True
    except requests.exceptions.RequestException as e:
        st.error(f"เกิดข้อผิดพลาด: {e.response.json().get('detail')}")
        return False

def delete_product(product_id: str):
    try:
        response = requests.delete(f"{API_BASE_URL}/products/{product_id}")
        response.raise_for_status()
        st.success("ลบสินค้าสำเร็จ!")
        return True
    except requests.exceptions.RequestException as e:
        st.error(f"เกิดข้อผิดพลาดในการลบ: {e.response.json().get('detail')}")
        return False

def upload_image(product_id: str, image_file):
    try:
        files = {'file': (image_file.name, image_file, image_file.type)}
        response = requests.post(f"{API_BASE_URL}/products/{product_id}/upload-image", files=files)
        response.raise_for_status()
        st.success("อัปโหลดรูปภาพสำเร็จ!")
        return True
    except requests.exceptions.RequestException as e:
        st.error(f"เกิดข้อผิดพลาดในการอัปโหลดรูป: {e.response.json().get('detail')}")
        return False

# -----------------------------------------------------------------------------
# 🖼️ ส่วนแสดงผล (UI Layout)
# -----------------------------------------------------------------------------

st.set_page_config(layout="wide", page_title="จัดการสินค้า")
st.title("📦 ระบบจัดการสินค้า (Admin Panel)")

# --- บล็อกที่ 1: ฟอร์มสำหรับเพิ่มสินค้าใหม่ ---
with st.form("new_product_form", clear_on_submit=True):
    st.subheader("เพิ่มสินค้าใหม่ในเมนู")
    
    col1, col2 = st.columns(2)
    with col1:
        new_name = st.text_input("ชื่อสินค้า", placeholder="เช่น คาปูชิโน่เย็น")
        new_price = st.number_input("ราคา (บาท)", min_value=0.0, format="%.2f")
    with col2:
        new_category = st.text_input("หมวดหมู่", placeholder="เช่น เครื่องดื่มเย็น")

    # ใช้ st.form_submit_button ซึ่งเป็นปุ่มเดียวที่อนุญาตใน form
    submitted = st.form_submit_button("➕ เพิ่มสินค้า")
    if submitted:
        if not new_name or not new_category:
            st.warning("กรุณากรอกชื่อและหมวดหมู่ของสินค้า")
        else:
            if create_product(new_name, new_price, new_category):
                st.rerun() # โหลดหน้าใหม่เพื่อให้เห็นรายการที่อัปเดตทันที
# --- สิ้นสุดบล็อกของฟอร์ม ---


st.divider()

# --- บล็อกที่ 2: แสดงและจัดการสินค้าที่มีอยู่ (อยู่นอก form) ---
st.subheader("รายการสินค้าทั้งหมดในระบบ")

products = get_products()

if products is None:
    st.error("ไม่สามารถเชื่อมต่อกับเซิร์ฟเวอร์เพื่อดึงข้อมูลสินค้าได้")
elif not products:
    st.info("ยังไม่มีสินค้าในระบบ กรุณาเพิ่มสินค้าใหม่จากฟอร์มด้านบน")
else:
    # สร้างการ์ดสำหรับจัดการสินค้าแต่ละรายการ
    for product in products:
        with st.container(border=True):
            col_info, col_upload, col_delete = st.columns([2, 2, 1])
            
            with col_info:
                st.write(f"**{product['name']}**")
                st.caption(f"หมวดหมู่: {product['category']} | ราคา: {product['price']:.2f} ฿")
                if product['image_url']:
                    st.image(API_BASE_URL + product['image_url'], width=100)
                else:
                    st.caption("ยังไม่มีรูปภาพ")

            with col_upload:
                uploaded_file = st.file_uploader(
                    "อัปโหลดรูปภาพใหม่", 
                    type=["png", "jpg", "jpeg"],
                    key=f"upload_{product['id']}"
                )
                if uploaded_file is not None:
                    if upload_image(product['id'], uploaded_file):
                        st.rerun()

            with col_delete:
                # ใช้ st.button() ที่อยู่นอก form ได้ตามปกติ
                if st.button("🗑️ ลบสินค้านี้", key=f"delete_{product['id']}", type="primary", use_container_width=True):
                    delete_product(product['id'])
                    st.rerun()