import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# Cấu hình trang
st.set_page_config(page_title="Quản Lý Thu Chi Gia Đình", page_icon="💰", layout="centered")

# Kết nối Database (Dùng SQLite)
conn = sqlite3.connect("data_thu_chi.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS transactions (id INTEGER PRIMARY KEY, date TEXT, type TEXT, amount REAL, note TEXT)")
conn.commit()

# --- GIAO DIỆN NHẬP LIỆU ---
st.title("💰 Quản Lý Thu Chi")

with st.form("input_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        amount = st.number_input("Số tiền (VNĐ):", min_value=0, step=1000, format="%d")
    with col2:
        transaction_type = st.selectbox("Loại:", ["Chi", "Thu"])
    
    note = st.text_input("Ghi chú:")
    submit_button = st.form_submit_button("Lưu Giao Dịch")

    if submit_button:
        if amount > 0:
            full_dt = datetime.now().strftime("%d/%m/%Y %H:%M")
            cursor.execute("INSERT INTO transactions (date, type, amount, note) VALUES (?,?,?,?)", 
                           (full_dt, transaction_type, amount, note))
            conn.commit()
            st.success(f"Đã lưu: {amount:,.0f}đ".replace(',', '.'))
        else:
            st.error("Vui lòng nhập số tiền!")

# --- THỐNG KÊ & LỊCH SỬ ---
st.divider()
st.subheader("📊 Lịch sử giao dịch")

# Lọc dữ liệu
month_filter = st.text_input("Lọc Tháng/Năm (vd: 04/2026):", datetime.now().strftime("%m/%Y"))

# Lấy dữ liệu từ DB
query = "SELECT * FROM transactions"
if month_filter:
    query += f" WHERE date LIKE '%{month_filter}%'"
query += " ORDER BY id DESC"

df = pd.read_sql_query(query, conn)

if not df.empty:
    # Tính toán tổng
    t_thu = df[df['type'] == 'Thu']['amount'].sum()
    t_chi = df[df['type'] == 'Chi']['amount'].sum()
    balance = t_thu - t_chi

    # Hiển thị 3 mục màu sắc
    c1, c2, c3 = st.columns(3)
    c1.metric("Tổng Thu", f"{t_thu:,.0f}đ".replace(',', '.'), delta_color="normal")
    c2.metric("Tổng Chi", f"-{t_chi:,.0f}đ".replace(',', '.'), delta_color="inverse")
    c3.metric("CÒN LẠI", f"{balance:,.0f}đ".replace(',', '.'), delta=balance)

    # Hiển thị bảng dữ liệu có màu sắc
    def color_type(val):
        color = 'blue' if val == 'Thu' else 'red'
        return f'color: {color}; font-weight: bold'

    st.dataframe(df.style.applymap(color_type, subset=['type']), use_container_width=True)

    # Nút xóa giao dịch
    st.write("---")
    del_id = st.number_input("Nhập ID để xóa:", min_value=1, step=1)
    if st.button("Xóa dòng này"):
        cursor.execute("DELETE FROM transactions WHERE id=?", (del_id,))
        conn.commit()
        st.warning(f"Đã xóa dòng ID {del_id}")
        st.rerun()
else:
    st.info("Chưa có dữ liệu cho tháng này.")
