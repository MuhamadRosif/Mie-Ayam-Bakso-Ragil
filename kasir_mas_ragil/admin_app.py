import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

DATA_FILE = "riwayat_penjualan.csv"
MENU_FILE = "kasir_mas_ragil/menu.json"

ADMIN_USER = "admin"
ADMIN_PASS = "1234"

def run_admin():
    # Session default
    if "admin_login" not in st.session_state:
        st.session_state.admin_login = False
    if "menu_makanan" not in st.session_state:
        st.session_state.menu_makanan = {}
    if "menu_minuman" not in st.session_state:
        st.session_state.menu_minuman = {}

    # Load menu
    if os.path.exists(MENU_FILE):
        with open(MENU_FILE,"r",encoding="utf-8") as f:
            data = json.load(f)
            st.session_state.menu_makanan = data.get("makanan",{})
            st.session_state.menu_minuman = data.get("minuman",{})
    else:
        st.session_state.menu_makanan = {"Mie Ayam":15000,"Bakso Urat":18000}
        st.session_state.menu_minuman = {"Es Teh Manis":5000,"Es Jeruk":7000}

    # Login admin
    if not st.session_state.admin_login:
        st.subheader("🔐 Login Admin")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Masuk Admin"):
            if username == ADMIN_USER and password == ADMIN_PASS:
                st.session_state.admin_login = True
                st.success("Login berhasil!")
                st.rerun()
            else:
                st.error("Username atau password salah.")
        return

    # Admin UI
    st.title("🛠️ Admin Dashboard — Kasir Mas Ragil")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📈 Laporan Penjualan"):
            show_laporan()
    with col2:
        if st.button("📄 Struk Terakhir"):
            show_struk()
    with col3:
        if st.button("🔑 Logout Admin"):
            st.session_state.admin_login = False
            st.rerun()

    st.subheader("🛠️ Admin Menu — Update/Tambah/Hapus Menu")
    show_admin_menu()

def show_admin_menu():
    st.subheader("🍽️ Menu Makanan")
    for item,harga in st.session_state.menu_makanan.copy().items():
        col1,col2,col3 = st.columns([3,2,1])
        with col1:
            nama_baru = st.text_input(f"{item}", value=item, key=f"makanan-{item}")
        with col2:
            harga_baru = st.number_input(f"Harga {item}", value=harga, step=1000, key=f"harga-{item}")
        with col3:
            if st.button("❌", key=f"del-makanan-{item}"):
                del st.session_state.menu_makanan[item]
                save_menu()
                st.success(f"{item} dihapus")
                st.rerun()
        # Tombol update
        if st.button("💾 Update", key=f"update-makanan-{item}"):
            st.session_state.menu_makanan[nama_baru] = harga_baru
            if nama_baru != item:
                del st.session_state.menu_makanan[item]
            save_menu()
            st.success(f"{nama_baru} diperbarui")
            st.rerun()

    st.subheader("🥤 Menu Minuman")
    for item,harga in st.session_state.menu_minuman.copy().items():
        col1,col2,col3 = st.columns([3,2,1])
        with col1:
            nama_baru = st.text_input(f"{item}", value=item, key=f"minum-{item}")
        with col2:
            harga_baru = st.number_input(f"Harga {item}", value=harga, step=1000, key=f"harga-minum-{item}")
        with col3:
            if st.button("❌", key=f"del-minum-{item}"):
                del st.session_state.menu_minuman[item]
                save_menu()
                st.success(f"{item} dihapus")
                st.rerun()
        # Tombol update
        if st.button("💾 Update", key=f"update-minum-{item}"):
            st.session_state.menu_minuman[nama_baru] = harga_baru
            if nama_baru != item:
                del st.session_state.menu_minuman[item]
            save_menu()
            st.success(f"{nama_baru} diperbarui")
            st.rerun()

    # Tambah menu baru
    st.markdown("### ➕ Tambah Menu Baru")
    nama_baru = st.text_input("Nama Menu Baru", key="new_menu_name")
    harga_baru = st.number_input("Harga Menu Baru", min_value=0, step=1000, key="new_menu_price")
    jenis = st.selectbox("Jenis Menu", ["Makanan","Minuman"], key="new_menu_type")
    if st.button("Tambah Menu"):
        if nama_baru.strip() and harga_baru>0:
            if jenis=="Makanan":
                st.session_state.menu_makanan[nama_baru] = harga_baru
            else:
                st.session_state.menu_minuman[nama_baru] = harga_baru
            save_menu()
            st.success(f"{nama_baru} berhasil ditambahkan")
            st.rerun()
        else:
            st.warning("Isi nama dan harga menu dengan benar.")

def save_menu():
    with open(MENU_FILE,"w",encoding="utf-8") as f:
        json.dump({"makanan":st.session_state.menu_makanan,"minuman":st.session_state.menu_minuman}, f, ensure_ascii=False, indent=2)

def show_laporan():
    st.subheader("📈 Laporan Penjualan")
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE, encoding="utf-8-sig")
        st.dataframe(df)
        daily = df.groupby("nama")["total"].sum()
        st.bar_chart(daily)
    else:
        st.info("Belum ada transaksi.")

def show_struk():
    if os.path.exists("struk_terakhir.txt"):
        with open("struk_terakhir.txt","r",encoding="utf-8") as f:
            struk = f.read()
        st.text(struk)
    else:
        st.info("Belum ada struk.")
