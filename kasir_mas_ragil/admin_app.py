import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd

MENU_FILE = "kasir_mas_ragil/menu.json"
USERS_FILE = "kasir_mas_ragil/users.json"
DATA_FILE = "kasir_mas_ragil/riwayat_penjualan.csv"

def run_admin():
    if "admin_login" not in st.session_state:
        st.session_state.admin_login = False

    ADMIN_USER = "admin"
    ADMIN_PASS = "1234"

    if not st.session_state.admin_login:
        st.subheader("🔐 Login Admin")
        username = st.text_input("Username Admin")
        password = st.text_input("Password Admin", type="password")
        if st.button("Login Admin"):
            if username==ADMIN_USER and password==ADMIN_PASS:
                st.session_state.admin_login = True
                st.success("Login Admin Berhasil!")
                st.experimental_rerun()
            else:
                st.error("Username/Password Admin salah.")

    if st.session_state.admin_login:
        st.header("👑 Admin Panel")
        # Lihat pesanan user
        st.subheader("📋 Semua Pesanan User")
        users_file = USERS_FILE
        users = {}
        if os.path.exists(users_file):
            with open(users_file,"r") as f:
                users = json.load(f)
        # Ambil keranjang tiap user dari session (untuk contoh sederhana)
        st.info("Semua pesanan dari user yang sedang aktif akan ditampilkan disini (sementara demo).")

        st.subheader("💳 Pembayaran")
        if os.path.exists(DATA_FILE):
            df = pd.read_csv(DATA_FILE)
        else:
            df = pd.DataFrame(columns=["timestamp","user","item","qty","subtotal"])
        st.dataframe(df)

        st.subheader("🛠️ Admin Menu")
        if os.path.exists(MENU_FILE):
            with open(MENU_FILE,"r") as f:
                menu_data = json.load(f)
        else:
            menu_data = {"makanan":{},"minuman":{}}
        st.write(menu_data)
