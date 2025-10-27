import streamlit as st
import json
import os
import pandas as pd

MENU_FILE = "menu.json"
CHECKOUT_FILE = "checkout.json"

# ------------------ Fungsi bantu ------------------
def load_data(file, default):
    if os.path.exists(file):
        try:
            with open(file, "r") as f:
                return json.load(f)
        except:
            pass
    return default

def save_data(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def init_menu():
    if not os.path.exists(MENU_FILE):
        data = [
            {"nama": "Mie Ayam Original", "harga": 12000},
            {"nama": "Mie Ayam Bakso", "harga": 15000},
            {"nama": "Bakso Campur", "harga": 18000},
            {"nama": "Es Teh Manis", "harga": 5000},
            {"nama": "Es Jeruk", "harga": 6000},
        ]
        save_data(MENU_FILE, data)

# ------------------ Fungsi utama admin ------------------
def run_admin():
    st.sidebar.title("👑 Admin Panel - Mas Ragil")
    menu = st.sidebar.selectbox("Menu", ["Laporan Penjualan", "Kelola Menu", "Data Pesanan"])
    st.sidebar.markdown("---")

    init_menu()
    menu_data = load_data(MENU_FILE, [])
    checkout_data = load_data(CHECKOUT_FILE, [])

    # =========================
    # LAPORAN PENJUALAN
    # =========================
    if menu == "Laporan Penjualan":
        st.title("📊 Laporan Penjualan")

        if not checkout_data:
            st.info("Belum ada transaksi yang tercatat.")
        else:
            df = pd.DataFrame(checkout_data)
            df["subtotal"] = df["harga"] * df["jumlah"]
            total = df["subtotal"].sum()

            st.dataframe(df, use_container_width=True)
            st.markdown(f"### 💰 Total Pendapatan: Rp {total:,}")

    # =========================
    # KELOLA MENU
    # =========================
    elif menu == "Kelola Menu":
        st.title("🍜 Kelola Menu Restoran")

        df = pd.DataFrame(menu_data)
        st.dataframe(df, use_container_width=True)

        st.subheader("➕ Tambah Menu Baru")
        nama = st.text_input("Nama Menu Baru")
        harga = st.number_input("Harga (Rp)", min_value=0, step=1000)

        if st.button("Simpan Menu"):
            if nama and harga > 0:
                menu_data.append({"nama": nama, "harga": harga})
                save_data(MENU_FILE, menu_data)
                st.success(f"Menu '{nama}' berhasil ditambahkan!")
            else:
                st.warning("Harap isi nama dan harga dengan benar.")

        if st.button("🔄 Refresh Data"):
            st.rerun()

    # =========================
    # DATA PESANAN
    # =========================
    elif menu == "Data Pesanan":
        st.title("🧾 Data Pesanan Pelanggan")

        if not checkout_data:
            st.info("Belum ada pesanan dari pelanggan.")
        else:
            df = pd.DataFrame(checkout_data)
            st.dataframe(df, use_container_width=True)
            st.markdown(f"Total pesanan: **{len(df)} item**")

            if st.button("🧹 Hapus Semua Data Pesanan"):
                save_data(CHECKOUT_FILE, [])
                st.warning("Semua data pesanan telah dihapus!")
                st.rerun()
