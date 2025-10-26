import streamlit as st
import json, os, pandas as pd
from datetime import datetime

MENU_FILE = "kasir_mas_ragil/menu.json"
DATA_FILE = "kasir_mas_ragil/riwayat_penjualan.csv"

def run_admin():
    if "login_admin" not in st.session_state:
        st.session_state.login_admin = False

    ADMIN_USER = "admin"
    ADMIN_PASS = "1234"

    if not st.session_state.login_admin:
        st.header("🔐 Login Admin")
        username = st.text_input("Username Admin", key="admin_user")
        password = st.text_input("Password Admin", type="password", key="admin_pass")
        if st.button("Masuk Admin", key="btn_admin_login"):
            if username == ADMIN_USER and password == ADMIN_PASS:
                st.session_state.login_admin = True
                st.experimental_rerun()
            else:
                st.error("Username atau password salah.")
        return

    # -------------------
    # Halaman Admin
    # -------------------
    st.header("🛠️ Admin Dashboard")
    menu = ["Laporan", "Admin Menu", "Struk", "Logout"]
    choice = st.sidebar.selectbox("Menu Admin", menu, key="menu_admin")

    # Logout
    if choice == "Logout":
        st.session_state.login_admin = False
        st.experimental_rerun()

    # Load data menu
    if os.path.exists(MENU_FILE):
        with open(MENU_FILE,"r",encoding="utf-8") as f:
            menu_data = json.load(f)
    else:
        menu_data = {"makanan":{},"minuman":{}}

    # Laporan
    if choice == "Laporan":
        st.subheader("📈 Laporan Penjualan")
        if os.path.exists(DATA_FILE):
            df = pd.read_csv(DATA_FILE, encoding="utf-8-sig")
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            st.dataframe(df)
        else:
            st.info("Belum ada transaksi.")

    # Admin Menu
    elif choice == "Admin Menu":
        st.subheader("🛠️ Admin Menu — Update/Tambah/Hapus")
        st.write(menu_data)
        st.info("Pengaturan menu disini (update/tambah/hapus)")
