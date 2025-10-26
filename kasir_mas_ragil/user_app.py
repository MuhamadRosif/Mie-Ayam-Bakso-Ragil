import streamlit as st
import json
import os
import pandas as pd

MENU_FILE = "menu.json"
CHECKOUT_FILE = "checkout.json"

# --- Fungsi bantu untuk load / save JSON ---
def load_data(file, default):
    if os.path.exists(file):
        with open(file, "r") as f:
            return json.load(f)
    else:
        return default

def save_data(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)

# --- Inisialisasi file menu.json ---
def init_menu():
    if not os.path.exists(MENU_FILE):
        menu_default = [
            {"nama": "Mie Ayam Original", "harga": 12000},
            {"nama": "Mie Ayam Bakso", "harga": 15000},
            {"nama": "Bakso Campur", "harga": 18000},
            {"nama": "Es Teh Manis", "harga": 5000},
            {"nama": "Es Jeruk", "harga": 6000},
        ]
        save_data(MENU_FILE, menu_default)

# --- Fungsi utama halaman User ---
def run_user():
    st.title("🍜 Menu Mie Ayam Bakso Mas Ragil")

    init_menu()
    menu_data = load_data(MENU_FILE, [])
    checkout_data = load_data(CHECKOUT_FILE, [])

    st.subheader("Daftar Menu")

    # Tampilkan menu dalam grid
    for item in menu_data:
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.markdown(f"**{item['nama']}**")
        with col2:
            st.markdown(f"Rp {item['harga']:,}")
        with col3:
            if st.button(f"Pesan Sekarang ({item['nama']})"):
                checkout_data.append(item)
                save_data(CHECKOUT_FILE, checkout_data)
                st.success(f"{item['nama']} ditambahkan ke pesanan!")

    st.markdown("---")
    st.subheader("🛒 Keranjang Pesanan")

    if len(checkout_data) > 0:
        df = pd.DataFrame(checkout_data)
        df["harga"] = df["harga"].astype(int)
        total = df["harga"].sum()
        st.dataframe(df, use_container_width=True)
        st.markdown(f"### 💰 Total: Rp {total:,}")

        if st.button("Checkout Sekarang ✅"):
            st.success("Pesanan berhasil dikirim ke kasir!")
            save_data(CHECKOUT_FILE, [])  # Kosongkan setelah checkout
    else:
        st.info("Belum ada pesanan. Silakan pilih menu di atas 🍜")
