# pages/2_🧾_Order_History.py (Patched for backward compatibility)

import streamlit as st
import requests
from datetime import datetime

API_BASE_URL = "http://localhost:8000"

def get_all_orders():
    try:
        response = requests.get(f"{API_BASE_URL}/orders")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"ไม่สามารถดึงข้อมูลออเดอร์ได้: {e}")
        return []

st.set_page_config(layout="wide", page_title="ประวัติการสั่งซื้อ")
st.title("🧾 ประวัติการสั่งซื้อย้อนหลัง")

orders = get_all_orders()

if not orders:
    st.info("ยังไม่มีข้อมูลการสั่งซื้อในระบบ")
else:
    for order in orders:
        order_date = datetime.fromisoformat(order['order_date']).strftime('%d %b %Y, %H:%M:%S')
        with st.expander(f"**Order ID:** `{order['id']}` | **วันที่:** {order_date} | **ยอดรวม:** {order['total_amount']:.2f} บาท"):
            st.write(f"**สถานะ:** {order.get('status', 'N/A')}")
            st.markdown("---")
            st.write("**รายการสินค้า:**")
            
            cols = st.columns([3, 1, 1, 2])
            cols[0].write("**ชื่อสินค้า**")
            cols[1].write("**จำนวน**")
            cols[2].write("**ราคา/หน่วย**")
            cols[3].write("**ตัวเลือก**")
            
            for item in order['items']:
                item_cols = st.columns([3, 1, 1, 2])
                item_cols[0].write(f" ▸ {item.get('product_name', 'N/A')}")
                item_cols[1].text(item.get('quantity', 0))

                # --- ส่วน Logic ที่แก้ไขเพื่อรองรับข้อมูลเก่าและใหม่ ---
                price_to_display = item.get('price_per_unit')
                
                if price_to_display is None:
                    # ลองหา key เก่า (ถ้าเคยมี)
                    price_to_display = item.get('price_per_item')

                if price_to_display is None:
                    # ถ้าไม่มีจริงๆ ให้คำนวณจากยอดรวมของรายการ
                    item_total = item.get('item_total', 0)
                    quantity = item.get('quantity', 1)
                    if quantity > 0:
                        price_to_display = item_total / quantity
                    else:
                        price_to_display = 0

                item_cols[2].text(f"{price_to_display:.2f}")
                # ----------------------------------------------------
                
                selected_options = item.get('selected_options', [])
                options_str = ", ".join([opt['name'] for opt in selected_options]) if selected_options else "ไม่มี"
                item_cols[3].text(options_str)