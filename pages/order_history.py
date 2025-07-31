# pages/2_🧾_Order_History.py

import streamlit as st
import requests
from datetime import datetime

# -----------------------------------------------------------------------------
# ⚙️ การตั้งค่าและฟังก์ชัน (สามารถคัดลอกมาจากหน้าหลักได้)
# -----------------------------------------------------------------------------

# !!! สำคัญ: แก้ไข IP Address ของ Raspberry Pi ของคุณตรงนี้ !!!
API_BASE_URL = "http://192.168.137.22:8000"

def get_all_orders():
    """ดึงข้อมูลออเดอร์ทั้งหมดจาก Backend"""
    try:
        response = requests.get(f"{API_BASE_URL}/orders")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"ไม่สามารถดึงข้อมูลออเดอร์ได้: {e}")
        return []

# -----------------------------------------------------------------------------
# 🖼️ ส่วนแสดงผล (UI Layout)
# -----------------------------------------------------------------------------

st.set_page_config(layout="wide", page_title="ประวัติการสั่งซื้อ")
st.title("🧾 ประวัติการสั่งซื้อย้อนหลัง")
st.write("ตรวจสอบใบเสร็จและรายการสั่งซื้อทั้งหมดที่ผ่านมา")

# ดึงข้อมูลเมื่อเปิดหน้า
orders = get_all_orders()

if not orders:
    st.info("ยังไม่มีข้อมูลการสั่งซื้อในระบบ")
else:
    # สามารถเพิ่ม Filter ตามวันหรือช่วงเวลาได้ที่นี่ในอนาคต
    st.divider()
    
    # วนลูปแสดงผลออเดอร์แต่ละรายการ
    for order in orders:
        order_id = order['id']
        # แปลง string ของวันที่กลับเป็น object datetime เพื่อจัดรูปแบบ
        order_date = datetime.fromisoformat(order['order_date']).strftime('%d %b %Y, %H:%M:%S')
        total_amount = order['total_amount']
        
        # ใช้ st.expander เพื่อสร้างส่วนที่พับเก็บได้สำหรับแต่ละออเดอร์
        with st.expander(f"**Order ID:** `{order_id}` | **วันที่:** {order_date} | **ยอดรวม:** {total_amount:.2f} บาท"):
            
            st.write(f"**สถานะ:** {order['status']}")
            st.markdown("---")
            
            # แสดงรายการสินค้าในออเดอร์นั้นๆ
            st.write("**รายการสินค้า:**")
            
            # สร้าง Header สำหรับตารางรายการสินค้า
            cols = st.columns([3, 1, 1])
            cols[0].write("**ชื่อสินค้า**")
            cols[1].write("**จำนวน**")
            cols[2].write("**ราคา**")
            
            # วนลูปแสดงสินค้า
            for item in order['items']:
                item_cols = st.columns([3, 1, 1])
                item_cols[0].write(f" ▸ {item['product_name']}")
                item_cols[1].text(item['quantity'])
                item_cols[2].text(f"{item['price_per_item']:.2f}")