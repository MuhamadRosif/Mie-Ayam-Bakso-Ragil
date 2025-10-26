import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

DATA_FILE = "riwayat_penjualan.csv"
MENU_FILE = "menu.json"

ADMIN_USER = "admin"
ADMIN_PASS = "1234"

def run_admin():
    if "admin_login" not in st.session_state:
        st.session_state.admin_login = False

    # Login Admin
    if not st.session_state.admin_login:
        st.markdown("""
        <style>
        .stApp {background: linear-gradient(180deg,#071026,#0b1440); color:#e6eef8;}
        .login-card {background-color:#1b1b1b; padding:40px; border-radius:12px; width:360px; 
                     margin:120px auto; text-align:center; box-shadow:0 4px 20px rgba(0,0,0,0.4);}
        .stTextInput>div>div>input {background-color:#2b2b2b; color:#fff; border-radius:6px;}
        .stButton>button {background-color:#c62828; color:white; border:none; border-radius:6px; padding:8px 20px;}
        </style>
        """, unsafe_allow_html=True)
        st.markdown('<div class="login-card"><h3>🔐 Login Admin</h3>', unsafe_allow_html=True)
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Masuk"):
            if username == ADMIN_USER and password == ADMIN_PASS:
                st.session_state.admin_login = True
                st.experimental_rerun()
            else:
                st.error("Username atau password salah.")
        st.markdown('</div>', unsafe_allow_html=True)
        st.stop()

    st.header("🛠️ Admin Dashboard")
    st.write("Hanya admin yang bisa melihat menu ini.")

    # Load menu
    if os.path.exists(MENU_FILE):
        with open(MENU_FILE,"r",encoding="utf-8") as f:
            menu_data = json.load(f)
    else:
        menu_data = {"makanan":{},"minuman":{}}

    # Laporan
    st.subheader("📈 Laporan Penjualan")
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE, encoding="utf-8-sig")
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['total'] = df['total'].astype(int)
        st.dataframe(df[['timestamp','nama','subtotal','diskon','total','bayar','kembalian']])
        daily_revenue = df.groupby(df['timestamp'].dt.date)['total'].sum()
        st.bar_chart(daily_revenue)
    else:
        st.info("Belum ada transaksi.")

    # Admin menu update/tambah/hapus
    st.subheader("🛠️ Menu Admin")
    st.write("Update, Tambah, atau Hapus menu makanan/minuman")
