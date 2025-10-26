import streamlit as st
import json
import os

MENU_FILE = "kasir_mas_ragil/menu.json"

def run_user():
    if "user_login" not in st.session_state:
        st.session_state.user_login = False
    if "username" not in st.session_state:
        st.session_state.username = ""
    if "keranjang" not in st.session_state:
        st.session_state.keranjang = {}

    st.subheader("📝 Registrasi / Login User")
    col1, col2 = st.columns(2)
    with col1:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
    with col2:
        if st.button("Login"):
            if username and password:
                st.session_state.username = username
                st.session_state.user_login = True
                st.success(f"Login berhasil! Halo, {username}")
                st.experimental_rerun()
        if st.button("Daftar"):
            if username and password:
                # Simpan user ke file
                users_file = "kasir_mas_ragil/users.json"
                users = {}
                if os.path.exists(users_file):
                    with open(users_file,"r") as f:
                        users = json.load(f)
                if username in users:
                    st.warning("Username sudah ada!")
                else:
                    users[username] = password
                    with open(users_file,"w") as f:
                        json.dump(users,f)
                    st.success("Pendaftaran berhasil! Silakan login.")

    if st.session_state.user_login:
        st.header(f"👋 Halo, {st.session_state.username}!")
        # Load menu
        if os.path.exists(MENU_FILE):
            with open(MENU_FILE,"r") as f:
                menu_data = json.load(f)
        else:
            menu_data = {
                "makanan": {"Mie Ayam":15000,"Bakso Urat":18000},
                "minuman": {"Es Teh Manis":5000,"Es Jeruk":7000}
            }
        st.subheader("🍽️ Menu Makanan")
        for item,harga in menu_data.get("makanan",{}).items():
            col1,col2,col3 = st.columns([4,1,1])
            with col1: st.write(f"**{item}** (Rp {harga:,})")
            with col2:
                if st.button("-", key=f"{item}-min"):
                    st.session_state.keranjang[item] = max(0, st.session_state.keranjang.get(item,0)-1)
            with col3:
                if st.button("+", key=f"{item}-plus"):
                    st.session_state.keranjang[item] = st.session_state.keranjang.get(item,0)+1

        st.subheader("🥤 Menu Minuman")
        for item,harga in menu_data.get("minuman",{}).items():
            col1,col2,col3 = st.columns([4,1,1])
            with col1: st.write(f"**{item}** (Rp {harga:,})")
            with col2:
                if st.button("-", key=f"{item}-minum-min"):
                    st.session_state.keranjang[item] = max(0, st.session_state.keranjang.get(item,0)-1)
            with col3:
                if st.button("+", key=f"{item}-minum-plus"):
                    st.session_state.keranjang[item] = st.session_state.keranjang.get(item,0)+1

        # Keranjang
        st.subheader("🛒 Keranjang")
        keranjang_aktif = {k:v for k,v in st.session_state.keranjang.items() if v>0}
        if keranjang_aktif:
            total = 0
            for k,v in keranjang_aktif.items():
                harga_satuan = menu_data.get("makanan",{}).get(k, menu_data.get("minuman",{}).get(k,0))
                st.write(f"{k} x {v} = Rp {v*harga_satuan:,}")
                total += v*harga_satuan
            st.info(f"Total Pesanan (akan dibayar admin): Rp {total:,}")
        else:
            st.info("Keranjang kosong.")
