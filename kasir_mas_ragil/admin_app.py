# =====================================================
# admin_app.py — Admin Kasir Mas Ragil
# =====================================================
import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

MENU_FILE = "kasir_mas_ragil/menu.json"
DATA_FILE = "kasir_mas_ragil/checkout.json"

def run_admin():
    st.title("🛠️ Admin Panel — Kasir Mas Ragil")

    # -----------------------
    # Admin Login
    # -----------------------
    if "admin_login" not in st.session_state:
        st.session_state.admin_login = False

    ADMIN_USER = "admin"
    ADMIN_PASS = "1234"

    if not st.session_state.admin_login:
        st.subheader("🔐 Login Admin")
        username = st.text_input("Username Admin")
        password = st.text_input("Password Admin", type="password")
        if st.button("Login Admin"):
            if username == ADMIN_USER and password == ADMIN_PASS:
                st.session_state.admin_login = True
                st.success("Login admin berhasil!")
                st.experimental_rerun()
            else:
                st.error("Username atau password salah.")
        return

    # -----------------------
    # Menu Admin
    # -----------------------
    tabs = st.tabs(["Pesanan Users", "Menu Admin", "Laporan Harian", "Logout"])

    # -----------------------
    # TAB 1: Pesanan Users (Checkout)
    # -----------------------
    with tabs[0]:
        st.header("📋 Pesanan Users (Checkout)")
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                checkout_data = json.load(f)
            if checkout_data:
                for idx, co in enumerate(checkout_data):
                    st.markdown(f"**{co['username']} — {co['timestamp']}**")
                    for item, qty in co['items'].items():
                        st.write(f"{item} x {qty} = Rp {co['subtotal'][item]:,}")
                    st.write(f"Total Bayar: Rp {co['total_bayar']:,}")
                    st.write("---")
                    if st.button(f"✅ Bayar {co['username']}", key=f"pay-{idx}"):
                        st.success(f"Pesanan {co['username']} sudah dibayar.")
                        checkout_data.pop(idx)
                        with open(DATA_FILE, "w", encoding="utf-8") as f:
                            json.dump(checkout_data, f, ensure_ascii=False, indent=2)
                        st.experimental_rerun()
                    if st.button(f"❌ Hapus {co['username']}", key=f"del-{idx}"):
                        checkout_data.pop(idx)
                        with open(DATA_FILE, "w", encoding="utf-8") as f:
                            json.dump(checkout_data, f, ensure_ascii=False, indent=2)
                        st.success(f"Pesanan {co['username']} dihapus.")
                        st.experimental_rerun()
            else:
                st.info("Belum ada checkout dari users.")
        else:
            st.info("Belum ada checkout dari users.")

    # -----------------------
    # TAB 2: Admin Menu (Makanan & Minuman)
    # -----------------------
    with tabs[1]:
        st.header("🍽️ Update/Tambah/Hapus Menu")
        if os.path.exists(MENU_FILE):
            with open(MENU_FILE, "r", encoding="utf-8") as f:
                menu_data = json.load(f)
        else:
            menu_data = {"makanan": {}, "minuman": {}}

        st.subheader("Makanan")
        for item, harga in menu_data["makanan"].copy().items():
            col1, col2, col3 = st.columns([3,2,1])
            with col1:
                nama_baru = st.text_input(f"{item}", value=item, key=f"makanan-{item}")
            with col2:
                harga_baru = st.number_input(f"Harga {item}", value=harga, step=1000, key=f"harga-makanan-{item}")
            with col3:
                if st.button("❌", key=f"del-makanan-{item}"):
                    del menu_data["makanan"][item]
                    with open(MENU_FILE,"w",encoding="utf-8") as f:
                        json.dump(menu_data, f, ensure_ascii=False, indent=2)
                    st.success(f"{item} dihapus")
                    st.experimental_rerun()
            if st.button("💾 Update", key=f"update-makanan-{item}"):
                menu_data["makanan"][nama_baru] = harga_baru
                if nama_baru != item:
                    del menu_data["makanan"][item]
                with open(MENU_FILE,"w",encoding="utf-8") as f:
                    json.dump(menu_data, f, ensure_ascii=False, indent=2)
                st.success(f"{nama_baru} diperbarui")
                st.experimental_rerun()

        st.subheader("Minuman")
        for item, harga in menu_data["minuman"].copy().items():
            col1, col2, col3 = st.columns([3,2,1])
            with col1:
                nama_baru = st.text_input(f"{item}", value=item, key=f"minum-{item}")
            with col2:
                harga_baru = st.number_input(f"Harga {item}", value=harga, step=1000, key=f"harga-minum-{item}")
            with col3:
                if st.button("❌", key=f"del-minum-{item}"):
                    del menu_data["minuman"][item]
                    with open(MENU_FILE,"w",encoding="utf-8") as f:
                        json.dump(menu_data, f, ensure_ascii=False, indent=2)
                    st.success(f"{item} dihapus")
                    st.experimental_rerun()
            if st.button("💾 Update", key=f"update-minum-{item}"):
                menu_data["minuman"][nama_baru] = harga_baru
                if nama_baru != item:
                    del menu_data["minuman"][item]
                with open(MENU_FILE,"w",encoding="utf-8") as f:
                    json.dump(menu_data, f, ensure_ascii=False, indent=2)
                st.success(f"{nama_baru} diperbarui")
                st.experimental_rerun()

        # Tambah menu baru
        st.markdown("### ➕ Tambah Menu Baru")
        nama_baru = st.text_input("Nama Menu Baru", key="nama_baru")
        harga_baru = st.number_input("Harga Menu Baru", min_value=0, step=1000, key="harga_baru")
        jenis = st.selectbox("Jenis Menu", ["Makanan","Minuman"], key="jenis_menu")
        if st.button("Tambah Menu"):
            if nama_baru.strip() and harga_baru>0:
                if jenis=="Makanan":
                    menu_data["makanan"][nama_baru] = harga_baru
                else:
                    menu_data["minuman"][nama_baru] = harga_baru
                with open(MENU_FILE,"w",encoding="utf-8") as f:
                    json.dump(menu_data, f, ensure_ascii=False, indent=2)
                st.success(f"{nama_baru} berhasil ditambahkan")
                st.experimental_rerun()
            else:
                st.warning("Isi nama dan harga menu dengan benar.")

    # -----------------------
    # TAB 3: Laporan Harian
    # -----------------------
    with tabs[2]:
        st.header("📈 Laporan Harian")
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                checkout_data = json.load(f)
            if checkout_data:
                df = pd.DataFrame(checkout_data)
                st.dataframe(df)
                if st.button("❌ Hapus Semua Laporan"):
                    os.remove(DATA_FILE)
                    st.success("Semua laporan dihapus")
                    st.experimental_rerun()
            else:
                st.info("Belum ada laporan harian.")
        else:
            st.info("Belum ada laporan harian.")

    # -----------------------
    # TAB 4: Logout
    # -----------------------
    with tabs[3]:
        if st.button("Logout Admin"):
            st.session_state.admin_login = False
            st.success("Logout berhasil!")
            st.experimental_rerun()
