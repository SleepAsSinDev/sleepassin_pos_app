# pages/3_📦_Product_Management.py

import streamlit as st
import requests
import pandas as pd

# -----------------------------------------------------------------------------
# ⚙️ การตั้งค่าและฟังก์ชัน API
# -----------------------------------------------------------------------------

API_BASE_URL = "http://192.168.1.145:8000" # แก้ไข IP ของคุณ

# --- ฟังก์ชันสำหรับ Products ---
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

# --- ส่วนที่ 1: ฟอร์มสำหรับเพิ่มสินค้าใหม่ ---
with st.form("new_product_form", clear_on_submit=True):
    st.subheader("เพิ่มสินค้าใหม่ในเมนู")
    
    col1, col2 = st.columns(2)
    with col1:
        new_name = st.text_input("ชื่อสินค้า", placeholder="เช่น คาปูชิโน่เย็น")
        new_price = st.number_input("ราคา (บาท)", min_value=0.0, format="%.2f")
    with col2:
        new_category = st.text_input("หมวดหมู่", placeholder="เช่น เครื่องดื่มเย็น")

    submitted = st.form_submit_button("➕ เพิ่มสินค้า")
    if submitted:
        if not new_name or not new_category:
            st.warning("กรุณากรอกชื่อและหมวดหมู่ของสินค้า")
        else:
            if create_product(new_name, new_price, new_category):
                # ไม่ต้องทำอะไรเพิ่ม เพราะ form จะเคลียร์ค่าให้เอง
                pass

st.divider()

# --- ส่วนที่ 2: แสดงและจัดการสินค้าที่มีอยู่ ---
st.subheader("รายการสินค้าทั้งหมดในระบบ")

products = get_products()

if products is None:
    st.error("ไม่สามารถเชื่อมต่อกับเซิร์ฟเวอร์เพื่อดึงข้อมูลสินค้าได้")
elif not products:
    st.info("ยังไม่มีสินค้าในระบบ กรุณาเพิ่มสินค้าใหม่จากฟอร์มด้านบน")
else:
    # สร้าง DataFrame จากข้อมูลสินค้าเพื่อแสดงผลในตาราง
    df = pd.DataFrame(products)
    # จัดลำดับคอลัมน์ใหม่เพื่อความสวยงาม
    df = df[['name', 'category', 'price', 'id', 'image_url']]
    
    # ใช้ st.data_editor เพื่อสร้างตารางที่สามารถโต้ตอบได้
    st.info("คุณสามารถจัดการสินค้าแต่ละรายการได้ที่คอลัมน์ 'actions' ด้านขวาสุด")
    
    # เพิ่มคอลัมน์ 'actions' เข้าไปใน DataFrame
    df['actions'] = [None] * len(df)
    
    # แสดงตาราง
    edited_df = st.data_editor(
        df,
        column_config={
            # ตั้งค่าให้คอลัมน์ id และ image_url ไม่แสดงผล
            "id": None,
            "image_url": None,
            # ตั้งค่าหัวข้อคอลัมน์ให้เป็นภาษาไทย
            "name": st.column_config.TextColumn("ชื่อสินค้า", required=True),
            "category": st.column_config.TextColumn("หมวดหมู่", required=True),
            "price": st.column_config.NumberColumn("ราคา", required=True, format="%.2f ฿"),
            "actions": st.column_config.TextColumn("จัดการ", disabled=True) # คอลัมน์ว่างๆ สำหรับวางปุ่ม
        },
        disabled=["name", "category", "price"], # ทำให้ข้อมูลหลักแก้ไขในตารางโดยตรงไม่ได้
        hide_index=True,
        use_container_width=True
    )

    # สร้างคอลัมน์สำหรับจัดการ (นอกตารางเพื่อให้วางปุ่มได้)
    st.write("--- จัดการรายสินค้า ---")
    for index, row in df.iterrows():
        with st.container(border=True):
            col_name, col_upload, col_delete = st.columns([2, 2, 1])
            
            with col_name:
                st.write(f"**{row['name']}**")
                if row['image_url']:
                    st.image(API_BASE_URL + row['image_url'], width=100)
                else:
                    st.caption("ยังไม่มีรูปภาพ")

            with col_upload:
                uploaded_file = st.file_uploader(
                    "อัปโหลดรูปภาพใหม่", 
                    type=["png", "jpg", "jpeg"],
                    key=f"upload_{row['id']}"
                )
                if uploaded_file is not None:
                    if upload_image(row['id'], uploaded_file):
                        st.rerun() # โหลดหน้าใหม่เพื่อแสดงรูปที่อัปเดต

            with col_delete:
                if st.button("🗑️ ลบสินค้านี้", key=f"delete_{row['id']}", type="primary"):
                    delete_product(row['id'])
                    st.rerun() # โหลดหน้าใหม่เพื่ออัปเดตรายการ