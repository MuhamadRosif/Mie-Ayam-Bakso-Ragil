import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# -----------------------
# Konfigurasi Aplikasi
# -----------------------
st.set_page_config(page_title="Admin Kasir Mas Ragil", page_icon="🍜", layout="wide")
DATA_FILE = "riwayat_penjualan.csv"
MENU_FILE = "menu.json"

# -----------------------
# Login Admin
# -----------------------
if "login" not in st.session_state:
    st.session_state.login = False

ADMIN_USER = "admin"
ADMIN_PASS = "1234"

if not st.session_state.login:
    st.header("🔐 Login Admin — Kasir Mas Ragil")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Masuk"):
        if username == ADMIN_USER and password == ADMIN_PASS:
            st.session_state.login = True
            st.experimental_rerun()
        else:
            st.error("Username atau password salah")
    st.stop()

# -----------------------
# Load Menu
# -----------------------
if os.path.exists(MENU_FILE):
    with open(MENU_FILE,"r",encoding="utf-8") as f:
        menu_data = json.load(f)
else:
    menu_data = {"makanan":{"Mie Ayam":15000,"Bakso Urat":18000},"minuman":{"Es Teh":5000}}
    with open(MENU_FILE,"w",encoding="utf-8") as f:
        json.dump(menu_data,f,ensure_ascii=False, indent=2)

# -----------------------
# Sidebar Admin
# -----------------------
st.sidebar.title("Menu Admin")
page = st.sidebar.radio("Navigasi", ["Laporan","Menu Admin","Tentang"])

# -----------------------
# Fungsi
# -----------------------
def save_menu():
    with open(MENU_FILE,"w",encoding="utf-8") as f:
        json.dump(menu_data,f,ensure_ascii=False, indent=2)

def save_transaction(record):
    df = pd.DataFrame([record])
    if os.path.exists(DATA_FILE):
        df.to_csv(DATA_FILE, mode="a", header=False,index=False,encoding="utf-8-sig")
    else:
        df.to_csv(DATA_FILE,index=False,encoding="utf-8-sig")

# -----------------------
# Halaman Admin
# -----------------------
if page=="Laporan":
    st.header("📈 Laporan Penjualan")
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE,encoding="utf-8-sig")
        st.dataframe(df)
        # Delete transaksi
        st.markdown("### ❌ Hapus Transaksi")
        for idx,row in df.iterrows():
            if st.button(f"Hapus {row['nama']} {row['timestamp']}", key=f"del-{idx}"):
                df.drop(idx,inplace=True)
                df.to_csv(DATA_FILE,index=False,encoding="utf-8-sig")
                st.success("Transaksi dihapus")
                st.experimental_rerun()
    else:
        st.info("Belum ada transaksi")

elif page=="Menu Admin":
    st.header("🛠️ Menu Admin — Update/Tambah/Hapus")
    st.subheader("🍽️ Menu Makanan")
    for item,harga in menu_data["makanan"].copy().items():
        col1,col2,col3 = st.columns([3,2,1])
        with col1:
            nama_baru = st.text_input(f"{item}", value=item, key=f"makanan-{item}")
        with col2:
            harga_baru = st.number_input(f"Harga {item}", value=harga, step=1000, key=f"harga-{item}")
        with col3:
            if st.button("❌", key=f"del-makanan-{item}"):
                del menu_data["makanan"][item]
                save_menu()
                st.success(f"{item} dihapus")
                st.experimental_rerun()
        if st.button("💾 Update", key=f"update-makanan-{item}"):
            menu_data["makanan"][nama_baru] = harga_baru
            if nama_baru != item:
                del menu_data["makanan"][item]
            save_menu()
            st.success(f"{nama_baru} diperbarui")
            st.experimental_rerun()

    st.subheader("🥤 Menu Minuman")
    for item,harga in menu_data["minuman"].copy().items():
        col1,col2,col3 = st.columns([3,2,1])
        with col1:
            nama_baru = st.text_input(f"{item}", value=item, key=f"minum-{item}")
        with col2:
            harga_baru = st.number_input(f"Harga {item}", value=harga, step=1000, key=f"harga-minum-{item}")
        with col3:
            if st.button("❌", key=f"del-minum-{item}"):
                del menu_data["minuman"][item]
                save_menu()
                st.success(f"{item} dihapus")
                st.experimental_rerun()
        if st.button("💾 Update", key=f"update-minum-{item}"):
            menu_data["minuman"][nama_baru] = harga_baru
            if nama_baru != item:
                del menu_data["minuman"][item]
            save_menu()
            st.success(f"{nama_baru} diperbarui")
            st.experimental_rerun()

    st.markdown("### ➕ Tambah Menu Baru")
    nama_baru = st.text_input("Nama Menu Baru")
    harga_baru = st.number_input("Harga Menu Baru", min_value=0, step=1000)
    jenis = st.selectbox("Jenis Menu", ["Makanan","Minuman"])
    if st.button("Tambah Menu"):
        if nama_baru.strip() and harga_baru>0:
            menu_data[jenis.lower()][nama_baru] = harga_baru
            save_menu()
            st.success(f"{nama_baru} berhasil ditambahkan")
            st.experimental_rerun()

elif page=="Tentang":
    st.header("ℹ️ Tentang Aplikasi")
    st.write("Admin Kasir Mie Ayam & Bakso Mas Ragil 🍜")
    st.write("Dibuat dengan ❤️ oleh Mas Ragil")
