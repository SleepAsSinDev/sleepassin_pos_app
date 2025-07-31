# pages/4_📊_Dashboard.py (Patched for backward compatibility)

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

API_BASE_URL = "http://localhost:8000"

@st.cache_data(ttl=300)
def get_all_orders():
    try:
        response = requests.get(f"{API_BASE_URL}/orders"); response.raise_for_status(); return response.json()
    except requests.exceptions.RequestException: st.error("ไม่สามารถดึงข้อมูลออเดอร์ได้"); return []

@st.cache_data(ttl=3600)
def get_all_products():
    try:
        response = requests.get(f"{API_BASE_URL}/products"); response.raise_for_status(); return response.json()
    except requests.exceptions.RequestException: st.error("ไม่สามารถดึงข้อมูลสินค้าได้"); return []

st.set_page_config(layout="wide", page_title="Dashboard")
st.title("📊 Dashboard สรุปยอดขาย")

orders = get_all_orders()
products = get_all_products()

if not orders:
    st.info("ยังไม่มีข้อมูลการสั่งซื้อเพื่อนำมาวิเคราะห์")
else:
    orders_df = pd.DataFrame(orders)
    orders_df['order_date'] = pd.to_datetime(orders_df['order_date'])
    
    st.sidebar.header("ตัวกรองข้อมูล")
    today = datetime.now().date()
    start_date = st.sidebar.date_input('วันที่เริ่มต้น', today - timedelta(days=7))
    end_date = st.sidebar.date_input('วันที่สิ้นสุด', today)

    mask = (orders_df['order_date'].dt.date >= start_date) & (orders_df['order_date'].dt.date <= end_date)
    filtered_orders_df = orders_df.loc[mask]

    if filtered_orders_df.empty:
        st.warning("ไม่พบข้อมูลในช่วงวันที่ที่เลือก")
    else:
        total_revenue = filtered_orders_df['total_amount'].sum()
        total_orders = len(filtered_orders_df)
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0

        kpi1, kpi2, kpi3 = st.columns(3)
        kpi1.metric(label="ยอดขายทั้งหมด (บาท)", value=f"{total_revenue:,.2f}")
        kpi2.metric(label="จำนวนออเดอร์ทั้งหมด", value=f"{total_orders:,}")
        kpi3.metric(label="ยอดขายเฉลี่ยต่อออเดอร์ (บาท)", value=f"{avg_order_value:,.2f}")

        st.divider()
        
        daily_sales = filtered_orders_df.set_index('order_date').resample('D')['total_amount'].sum().reset_index()
        daily_sales.rename(columns={'order_date': 'วันที่', 'total_amount': 'ยอดขาย'}, inplace=True)

        # --- ส่วน Logic ที่แก้ไขเพื่อรองรับข้อมูลเก่า ---
        all_items_df = filtered_orders_df.explode('items')
        items_detail_df = pd.json_normalize(all_items_df['items'].apply(lambda x: x if isinstance(x, dict) else {}))

        # ตรวจสอบและสร้างคอลัมน์ 'item_total' ถ้ายังไม่มี
        if 'item_total' not in items_detail_df.columns:
            items_detail_df['item_total'] = 0
        items_detail_df['item_total'].fillna(0, inplace=True)
        # --------------------------------------------

        top_products = items_detail_df.groupby('product_name')['quantity'].sum().sort_values(ascending=False).reset_index()
        top_products.rename(columns={'product_name': 'สินค้า', 'quantity': 'จำนวนที่ขายได้'}, inplace=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📈 ยอดขายรายวัน")
            st.bar_chart(daily_sales, x='วันที่', y='ยอดขาย', use_container_width=True)
            
            st.subheader("🍰 ยอดขายตามหมวดหมู่")
            if products and not items_detail_df.empty:
                products_df = pd.DataFrame(products)
                product_category_map = products_df.set_index('id')['category'].to_dict()
                items_detail_df['category'] = items_detail_df['product_id'].apply(lambda x: product_category_map.get(x))
                category_sales_df = items_detail_df.dropna(subset=['category'])
                
                if not category_sales_df.empty:
                    category_sales = category_sales_df.groupby('category')['item_total'].sum().reset_index()
                    category_sales.rename(columns={'category': 'หมวดหมู่', 'item_total': 'ยอดขาย'}, inplace=True)
                    fig = px.pie(category_sales, names='หมวดหมู่', values='ยอดขาย', hole=.3)
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("ไม่พบข้อมูลยอดขายตามหมวดหมู่ในช่วงเวลานี้")
            else:
                 st.info("ไม่สามารถแสดงยอดขายตามหมวดหมู่ได้")

        with col2:
            st.subheader("⭐ 5 อันดับสินค้าขายดี")
            st.dataframe(top_products.head(5), use_container_width=True, hide_index=True)
            st.subheader("📋 รายละเอียดสินค้าขายดีทั้งหมด")
            st.dataframe(top_products, use_container_width=True, hide_index=True)