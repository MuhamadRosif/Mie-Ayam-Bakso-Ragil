import streamlit as st
import json
import os
import pandas as pd

MENU_FILE = "menu.json"
CHECKOUT_FILE = "checkout.json"

# --- Fungsi bantu load/save JSON dengan fallback aman ---
def load_data(file, default):
    if os.path.exists(file):
        try:
            with open(file, "r") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
        except json.JSONDecodeError:
            pass
    return default

def save_data(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# --- Buat file menu default kalau belum ada atau rusak ---
def init_menu():
    menu_default = [
        {"nama": "Mie Ayam Original", "harga": 12000},
        {"nama": "Mie Ayam Bakso", "harga": 15000},
        {"nama": "Bakso Campur", "harga": 18000},
        {"nama": "Es Teh Manis", "harga": 5000},
        {"nama": "Es Jeruk", "harga": 6000},
    ]
    if not os.path.exists(MENU_FILE):
        save_data(MENU_FILE, menu_default)
    else:
        # Validasi kalau file menu.json rusak
        data = load_data(MENU_FILE, [])
        if not data:
            save_data(MENU_FILE, menu_default)

# --- Halaman utama User ---
def run_user():
    st.title("🍜 Menu Mie Ayam Bakso Mas Ragil")

    init_menu()
    menu_data = load_data(MENU_FILE, [])
    checkout_data = load_data(CHECKOUT_FILE, [])

    if not menu_data:
        st.error("Gagal memuat menu! File menu.json kosong atau rusak.")
        return

    st.subheader("📋 Daftar Menu")

    for i, item in enumerate(menu_data):
        nama = item.get("nama", f"Item {i+1}")
        harga = item.get("harga", 0)
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.markdown(f"**{nama}**")
        with col2:
            st.markdown(f"Rp {harga:,}")
        with col3:
            if st.button(f"Pesan Sekarang ({nama})"):
                checkout_data.append({"nama": nama, "harga": harga})
                save_data(CHECKOUT_FILE, checkout_data)
                st.success(f"{nama} ditambahkan ke pesanan!")

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
            save_data(CHECKOUT_FILE, [])  # Kosongkan keranjang
    else:
        st.info("Belum ada pesanan. Silakan pilih menu di atas 🍜")
