import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime

MENU_FILE = "kasir_mas_ragil/menu.json"
DATA_FILE = "kasir_mas_ragil/riwayat_penjualan.csv"

def run_admin():
    st.header("🛠️ Admin Panel — Kasir Mas Ragil")

    # Load menu
    if os.path.exists(MENU_FILE):
        with open(MENU_FILE,"r",encoding="utf-8") as f:
            data = json.load(f)
            menu_makanan = data.get("makanan",{})
            menu_minuman = data.get("minuman",{})
    else:
        menu_makanan = {"Mie Ayam":15000,"Bakso Urat":18000}
        menu_minuman = {"Es Teh":5000,"Es Jeruk":7000}

    # Laporan penjualan
    st.subheader("📈 Laporan Penjualan")
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        st.dataframe(df)
    else:
        st.info("Belum ada transaksi.")

    # Admin menu update/tambah/hapus
    st.subheader("🛠️ Admin Menu")
    st.write("Menu Makanan:", menu_makanan)
    st.write("Menu Minuman:", menu_minuman)

    if st.button("Logout", on_click=logout):
        pass

def logout():
    st.session_state.login=False
    st.session_state.username=""
    st.session_state.role=""
    st.experimental_rerun()
