# admin_app.py
import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

DATA_FILE = "riwayat_penjualan.csv"
MENU_FILE = "menu.json"

ADMIN_USER = "admin"
ADMIN_PASS = "1234"

# -------------------------
# Session Defaults
# -------------------------
if "admin_login" not in st.session_state:
    st.session_state.admin_login = False
if "menu_makanan" not in st.session_state:
    st.session_state.menu_makanan = {}
if "menu_minuman" not in st.session_state:
    st.session_state.menu_minuman = {}

# -------------------------
# Load Menu
# -------------------------
if os.path.exists(MENU_FILE):
    with open(MENU_FILE,"r",encoding="utf-8") as f:
        data = json.load(f)
        st.session_state.menu_makanan = data.get("makanan",{})
        st.session_state.menu_minuman = data.get("minuman",{})
else:
    st.session_state.menu_makanan = {"Mie Ayam":15000,"Bakso Urat":18000}
    st.session_state.menu_minuman = {"Es Teh":5000,"Es Jeruk":7000}
    with open(MENU_FILE,"w",encoding="utf-8") as f:
        json.dump({"makanan":st.session_state.menu_makanan,"minuman":st.session_state.menu_minuman}, f, ensure_ascii=False, indent=2)

# -------------------------
# Login Admin
# -------------------------
def admin_login():
    st.title("🔐 Login Admin")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Masuk", key="admin_login_btn"):
        if username == ADMIN_USER and password == ADMIN_PASS:
            st.session_state.admin_login = True
            st.rerun()
        else:
            st.error("Username atau password salah.")

# -------------------------
# Save Transaction
# -------------------------
def save_transaction(record):
    df = pd.DataFrame([record])
    if os.path.exists(DATA_FILE):
        df.to_csv(DATA_FILE, mode="a", header=False, index=False, encoding="utf-8-sig")
    else:
        df.to_csv(DATA_FILE, index=False, encoding="utf-8-sig")

# -------------------------
# Admin Dashboard
# -------------------------
def admin_dashboard():
    st.sidebar.title("Admin Menu")
    page = st.sidebar.radio("Navigasi:", ["📈 Laporan","🛠 Admin Menu","🚪 Logout"])

    if page == "🚪 Logout":
        st.session_state.admin_login = False
        st.rerun()

    elif page == "📈 Laporan":
        st.header("📊 Laporan Penjualan")
        if os.path.exists(DATA_FILE):
            df = pd.read_csv(DATA_FILE, encoding="utf-8-sig")
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            st.dataframe(df)
            st.bar_chart(df.groupby(df['timestamp'].dt.date)['total'].sum())
            # Delete transaksi
            st.markdown("### ❌ Hapus Transaksi")
            for idx,row in df.iterrows():
                if st.button(f"Hapus {row['nama']} {row['timestamp']}", key=f"del-{idx}"):
                    df.drop(idx,inplace=True)
                    df.to_csv(DATA_FILE,index=False,encoding="utf-8-sig")
                    st.success("Transaksi dihapus")
                    st.rerun()
        else:
            st.info("Belum ada transaksi.")

    elif page == "🛠 Admin Menu":
        st.header("⚙️ Update / Tambah / Hapus Menu")

        # Makanan
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
                    with open(MENU_FILE,"w",encoding="utf-8") as f:
                        json.dump({"makanan":st.session_state.menu_makanan,"minuman":st.session_state.menu_minuman}, f, ensure_ascii=False, indent=2)
                    st.success(f"{item} dihapus")
                    st.rerun()
            # Update
            if st.button("💾 Update", key=f"update-makanan-{item}"):
                st.session_state.menu_makanan[nama_baru] = harga_baru
                if nama_baru != item: del st.session_state.menu_makanan[item]
                with open(MENU_FILE,"w",encoding="utf-8") as f:
                    json.dump({"makanan":st.session_state.menu_makanan,"minuman":st.session_state.menu_minuman}, f, ensure_ascii=False, indent=2)
                st.success(f"{nama_baru} diperbarui")
                st.rerun()

        # Minuman
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
                    with open(MENU_FILE,"w",encoding="utf-8") as f:
                        json.dump({"makanan":st.session_state.menu_makanan,"minuman":st.session_state.menu_minuman}, f, ensure_ascii=False, indent=2)
                    st.success(f"{item} dihapus")
                    st.rerun()
            if st.button("💾 Update", key=f"update-minum-{item}"):
                st.session_state.menu_minuman[nama_baru] = harga_baru
                if nama_baru != item: del st.session_state.menu_minuman[item]
                with open(MENU_FILE,"w",encoding="utf-8") as f:
                    json.dump({"makanan":st.session_state.menu_makanan,"minuman":st.session_state.menu_minuman}, f, ensure_ascii=False, indent=2)
                st.success(f"{nama_baru} diperbarui")
                st.rerun()

        # Tambah menu baru
        st.markdown("### ➕ Tambah Menu Baru")
        nama_baru = st.text_input("Nama Menu Baru")
        harga_baru = st.number_input("Harga Menu Baru", min_value=0, step=1000)
        jenis = st.selectbox("Jenis Menu", ["Makanan","Minuman"])
        if st.button("Tambah Menu"):
            if nama_baru.strip() and harga_baru>0:
                if jenis=="Makanan":
                    st.session_state.menu_makanan[nama_baru] = harga_baru
                else:
                    st.session_state.menu_minuman[nama_baru] = harga_baru
                with open(MENU_FILE,"w",encoding="utf-8") as f:
                    json.dump({"makanan":st.session_state.menu_makanan,"minuman":st.session_state.menu_minuman}, f, ensure_ascii=False, indent=2)
                st.success(f"{nama_baru} berhasil ditambahkan")
                st.rerun()
            else:
                st.warning("Isi nama dan harga menu dengan benar.")

# -------------------------
# Run Admin App
# -------------------------
def run_admin():
    if not st.session_state.admin_login:
        admin_login()
    else:
        admin_dashboard()
