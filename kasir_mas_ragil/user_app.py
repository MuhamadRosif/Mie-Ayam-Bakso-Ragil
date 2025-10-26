import streamlit as st
import json
import os
import pandas as pd

MENU_FILE = "menu.json"
CHECKOUT_FILE = "checkout.json"

# --- Fungsi bantu load/save JSON ---
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

# --- Buat menu default kalau belum ada ---
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
        data = load_data(MENU_FILE, [])
        if not data:
            save_data(MENU_FILE, menu_default)

# --- Fungsi utama halaman user ---
def run_user():
    st.sidebar.title("🍜 Mie Ayam Bakso Mas Ragil")
    st.sidebar.markdown("### Selamat Datang, Pelanggan!")
    st.sidebar.markdown("---")

    st.title("📋 Menu Pilihan")
    init_menu()

    menu_data = load_data(MENU_FILE, [])
    checkout_data = load_data(CHECKOUT_FILE, [])

    if "cart" not in st.session_state:
        # Inisialisasi keranjang
        st.session_state.cart = {item["nama"]: 0 for item in menu_data}

    # --- Tampilkan daftar menu ---
    for item in menu_data:
        nama = item["nama"]
        harga = item["harga"]

        col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
        with col1:
            st.markdown(f"**{nama}**")
        with col2:
            st.markdown(f"Rp {harga:,}")
        with col3:
            if st.button("➖", key=f"min_{nama}"):
                if st.session_state.cart[nama] > 0:
                    st.session_state.cart[nama] -= 1
        with col4:
            if st.button("➕", key=f"plus_{nama}"):
                st.session_state.cart[nama] += 1

        st.progress(min(st.session_state.cart[nama] / 10, 1.0))  # indikasi jumlah
        st.caption(f"Jumlah: {st.session_state.cart[nama]} porsi")

    st.markdown("---")

    # --- Sidebar Keranjang ---
    st.sidebar.subheader("🛒 Keranjang Anda")

    cart_items = []
    total = 0
    for item in menu_data:
        jumlah = st.session_state.cart[item["nama"]]
        if jumlah > 0:
            subtotal = jumlah * item["harga"]
            cart_items.append({"nama": item["nama"], "harga": item["harga"], "jumlah": jumlah, "subtotal": subtotal})
            total += subtotal

    if cart_items:
        df = pd.DataFrame(cart_items)
        st.sidebar.dataframe(df[["nama", "jumlah", "subtotal"]], hide_index=True, use_container_width=True)
        st.sidebar.markdown(f"### 💰 Total: Rp {total:,}")

        if st.sidebar.button("Checkout Sekarang ✅"):
            save_data(CHECKOUT_FILE, cart_items)
            st.sidebar.success("Pesanan berhasil dikirim ke kasir!")
            st.session_state.cart = {item["nama"]: 0 for item in menu_data}
    else:
        st.sidebar.info("Belum ada pesanan 😋")

    st.sidebar.markdown("---")
    st.sidebar.caption("Gunakan tombol ➕ dan ➖ untuk menambah atau mengurangi pesanan Anda.")
