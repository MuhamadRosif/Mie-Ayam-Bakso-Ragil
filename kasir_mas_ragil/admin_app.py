import streamlit as st
import pandas as pd
import json
import os

MENU_FILE = os.path.join(os.path.dirname(__file__), "menu.json")
CHECKOUT_FILE = os.path.join(os.path.dirname(__file__), "checkout.json")

def load_json(file_path):
    if not os.path.exists(file_path):
        with open(file_path, "w") as f:
            json.dump([], f)
    with open(file_path, "r") as f:
        return json.load(f)

def save_json(file_path, data):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

def run_admin():
    st.title("👑 Panel Admin - Mie Ayam Bakso Mas Ragil")
    menu = st.sidebar.selectbox("Menu", ["Laporan Penjualan", "Kelola Menu", "Data Pesanan"])

    if menu == "Laporan Penjualan":
        st.subheader("📊 Laporan Penjualan")
        checkout_data = load_json(CHECKOUT_FILE)
        if checkout_data:
            df = pd.DataFrame(checkout_data)
            total = df["total"].sum()
            st.dataframe(df, use_container_width=True)
            st.success(f"Total Penjualan Hari Ini: Rp {total:,}")
        else:
            st.info("Belum ada data pesanan yang masuk.")

    elif menu == "Kelola Menu":
        st.subheader("🍜 Kelola Menu")
        nama = st.text_input("Nama Menu")
        harga = st.number_input("Harga (Rp)", min_value=0, step=1000)

        if st.button("Tambah Menu"):
            data = load_json(MENU_FILE)
            data.append({"menu": nama, "harga": harga})
            save_json(MENU_FILE, data)
            st.success(f"Menu {nama} berhasil ditambahkan!")

        st.write("📋 Daftar Menu Saat Ini:")
        data = load_json(MENU_FILE)
        if data:
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Belum ada menu yang tersimpan.")

    elif menu == "Data Pesanan":
        st.subheader("💵 Data Pesanan Pelanggan")
        checkout_data = load_json(CHECKOUT_FILE)
        if checkout_data:
            df = pd.DataFrame(checkout_data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Belum ada pesanan yang masuk.")
