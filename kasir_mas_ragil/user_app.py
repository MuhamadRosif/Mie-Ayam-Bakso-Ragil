import streamlit as st
import json
import os
import pandas as pd

MENU_FILE = "menu.json"
CHECKOUT_FILE = "checkout.json"

# --- Fungsi bantu ---
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

# --- Tampilan utama User ---
def run_user():
    st.sidebar.title("🍜 Mie Ayam Bakso Mas Ragil")
    menu = st.sidebar.radio("Navigasi", ["🏠 Beranda", "📋 Pesan Menu", "🛒 Keranjang", "📖 Riwayat Pesanan"])
    st.sidebar.markdown("---")
    st.sidebar.info("Gunakan menu di atas untuk navigasi 👆")

    init_menu()
    menu_data = load_data(MENU_FILE, [])
    checkout_data = load_data(CHECKOUT_FILE, [])

    if "cart" not in st.session_state:
        st.session_state.cart = {}

    # ======================================
    # BERANDA
    # ======================================
    if menu == "🏠 Beranda":
        st.title("Selamat Datang 🍜")
        st.markdown("""
        Selamat datang di **Mie Ayam Bakso Mas Ragil!**  
        Nikmati berbagai pilihan mie ayam dan bakso terbaik kami dengan harga bersahabat 😋  

        Gunakan menu di sidebar kiri untuk:
        - 📋 Melihat daftar menu dan pesan makanan  
        - 🛒 Mengecek pesanan Anda  
        - 📖 Melihat riwayat checkout sebelumnya  
        """)
        st.image("https://images.unsplash.com/photo-1606755962773-0e2d7efc4b5b", use_column_width=True)

    # ======================================
    # PESAN MENU
    # ======================================
    elif menu == "📋 Pesan Menu":
        st.title("📋 Daftar Menu")

        for item in menu_data:
            nama = item["nama"]
            harga = item["harga"]

            if nama not in st.session_state.cart:
                st.session_state.cart[nama] = 0

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

            st.caption(f"Jumlah: {st.session_state.cart[nama]} porsi")
            st.markdown("---")

    # ======================================
    # KERANJANG
    # ======================================
    elif menu == "🛒 Keranjang":
        st.title("🛒 Keranjang Pesanan")

        cart_items = []
        total = 0
        for item in menu_data:
            jumlah = st.session_state.cart.get(item["nama"], 0)
            if jumlah > 0:
                subtotal = item["harga"] * jumlah
                cart_items.append({
                    "nama": item["nama"],
                    "jumlah": jumlah,
                    "harga": item["harga"],
                    "subtotal": subtotal
                })
                total += subtotal

        if cart_items:
            df = pd.DataFrame(cart_items)
            st.dataframe(df, use_container_width=True)
            st.markdown(f"### 💰 Total: Rp {total:,}")
            if st.button("Checkout Sekarang ✅"):
                save_data(CHECKOUT_FILE, cart_items)
                st.success("Pesanan berhasil dikirim ke kasir!")
                st.session_state.cart = {}
        else:
            st.info("Keranjang Anda masih kosong 🍜")

    # ======================================
    # RIWAYAT PESANAN
    # ======================================
    elif menu == "📖 Riwayat Pesanan":
        st.title("📖 Riwayat Pesanan Sebelumnya")

        data = load_data(CHECKOUT_FILE, [])
        if data:
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Belum ada riwayat pesanan 😅")
