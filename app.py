import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# ==============================================================
# CONFIG
# ==============================================================
st.set_page_config(page_title="Kasir Mas Ragil", page_icon="🍜", layout="wide")

MENU_FILE = "menu.json"
CHECKOUT_FILE = "checkout.json"
SALES_FILE = "penjualan.csv"

# ==============================================================
# LOAD & SAVE DATA
# ==============================================================
def load_json(file, default):
    if os.path.exists(file):
        with open(file, "r") as f:
            return json.load(f)
    return default

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=2)

menu_data = load_json(MENU_FILE, {
    "makanan": {"Bakso Super": 15000, "Mie Ayam": 12000, "Mie Ayam Bakso": 18000},
    "minuman": {"Es Teh": 5000, "Es Jeruk": 7000, "Air Mineral": 4000}
})
checkout = load_json(CHECKOUT_FILE, [])

# ==============================================================
# SESSION DEFAULTS
# ==============================================================
if "page" not in st.session_state:
    st.session_state.page = "user"
if "last_page" not in st.session_state:
    st.session_state.last_page = None
if "admin_logged" not in st.session_state:
    st.session_state.admin_logged = False
if "buyer_name" not in st.session_state:
    st.session_state.buyer_name = ""

# ==============================================================
# USER PAGE (Menu & Pesanan)
# ==============================================================
def user_page():
    # Reset nama pembeli jika baru pindah ke halaman ini
    if st.session_state.last_page != "user":
        st.session_state.buyer_name = ""
    st.session_state.last_page = "user"

    st.title("🍜 Menu & Pesanan")
    st.subheader("👤 Nama Pembeli (wajib diisi)")
    st.session_state.buyer_name = st.text_input("Nama Pembeli", value=st.session_state.buyer_name)

    disable_order = not st.session_state.buyer_name
    if disable_order:
        st.warning("Nama pembeli wajib diisi sebelum memesan")

    col_menu, col_cart = st.columns([2, 1])
    with col_menu:
        st.subheader("📜 Menu")
        kategori = st.selectbox("Kategori", list(menu_data.keys()))
        item = st.selectbox("Menu", list(menu_data[kategori].keys()))
        qty = st.number_input("Jumlah", min_value=1, value=1)
        if st.button("Tambah ke Keranjang", disabled=disable_order):
            checkout.append({
                "nama": item,
                "harga": menu_data[kategori][item],
                "jumlah": qty,
                "buyer": st.session_state.buyer_name
            })
            save_json(CHECKOUT_FILE, checkout)
            st.success("✅ Ditambahkan ke keranjang")
            st.rerun()

    with col_cart:
        st.subheader("🧾 Keranjang Saat Ini")
        if checkout:
            df = pd.DataFrame(checkout)
            df["total"] = df["harga"] * df["jumlah"]
            st.dataframe(df, use_container_width=True)
            if st.button("💰 Cetak Pembayaran"):
                total = df["total"].sum()
                st.success(f"Total Pembayaran: Rp{total:,}")
                st.info(f"Terima kasih, {st.session_state.buyer_name} 🙏")

                # Simpan ke riwayat penjualan
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                df["tanggal"] = now
                if os.path.exists(SALES_FILE):
                    old = pd.read_csv(SALES_FILE)
                    df_all = pd.concat([old, df], ignore_index=True)
                else:
                    df_all = df
                df_all.to_csv(SALES_FILE, index=False)

                # Hapus keranjang dan reset nama pembeli
                checkout.clear()
                save_json(CHECKOUT_FILE, checkout)
                st.session_state.buyer_name = ""  # ✅ Reset nama setelah cetak
                st.rerun()
        else:
            st.info("Keranjang kosong")

    if not st.session_state.admin_logged:
        if st.sidebar.button("Admin Login"):
            st.session_state.page = "admin_login"
            st.rerun()

# ==============================================================
# ADMIN LOGIN PAGE
# ==============================================================
def admin_login_page():
    st.title("🔐 Admin Login")
    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")
    if st.button("Login"):
        if user == "admin" and pwd == "123":
            st.session_state.admin_logged = True
            st.session_state.page = "admin_dashboard"
            st.rerun()
        else:
            st.error("Username atau password salah!")

# ==============================================================
# ADMIN DASHBOARD
# ==============================================================
def admin_dashboard():
    st.title("📊 Dashboard Admin")
    if os.path.exists(SALES_FILE):
        df = pd.read_csv(SALES_FILE)
        st.dataframe(df, use_container_width=True)
        st.metric("Total Transaksi", len(df))
        st.metric("Total Pendapatan", f"Rp{df['total'].sum():,}")
    else:
        st.info("Belum ada data penjualan.")
    if st.button("Logout Admin"):
        st.session_state.admin_logged = False
        st.session_state.page = "user"
        st.rerun()

# ==============================================================
# PAGE ROUTING
# ==============================================================
if st.session_state.page == "user":
    user_page()
elif st.session_state.page == "admin_login":
    admin_login_page()
elif st.session_state.page == "admin_dashboard":
    admin_dashboard()
