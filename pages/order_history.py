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
    st.divider()
    for order in orders:
        order_date = datetime.fromisoformat(order['order_date']).strftime('%d %b %Y, %H:%M:%S')
        with st.expander(f"**Order ID:** `{order['id']}` | **วันที่:** {order_date} | **ยอดรวม:** {order['total_amount']:.2f} บาท"):
            st.write(f"**สถานะ:** {order['status']}")
            st.markdown("---")
            st.write("**รายการสินค้า:**")
            cols = st.columns([3, 1, 1, 2])
            cols[0].write("**ชื่อสินค้า**")
            cols[1].write("**จำนวน**")
            cols[2].write("**ราคา/หน่วย**")
            cols[3].write("**ตัวเลือก**")
            for item in order['items']:
                item_cols = st.columns([3, 1, 1, 2])
                item_cols[0].write(f" ▸ {item['product_name']}")
                item_cols[1].text(item['quantity'])
                item_cols[2].text(f"{item['price_per_unit']:.2f}")
                options_str = ", ".join([opt['name'] for opt in item['selected_options']]) if item['selected_options'] else "ไม่มี"
                item_cols[3].text(options_str)