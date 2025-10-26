import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd

DATA_FILE = "riwayat_penjualan.csv"
MENU_FILE = "menu.json"

def run_user():
    if "user_login" not in st.session_state:
        st.session_state.user_login = False
    if "users" not in st.session_state:
        st.session_state.users = {}  # username:password
    if "cart" not in st.session_state:
        st.session_state.cart = {}

    # Registrasi/Login
    st.header("🍜 Login / Registrasi User")
    tab1, tab2 = st.tabs(["Login", "Daftar"])
    
    with tab1:
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login", key="login_btn"):
            if username in st.session_state.users and st.session_state.users[username]==password:
                st.session_state.user_login = username
                st.success(f"Login berhasil! Selamat datang, {username}")
            else:
                st.error("Username/password salah atau belum daftar.")

    with tab2:
        new_user = st.text_input("Username", key="reg_user")
        new_pass = st.text_input("Password", type="password", key="reg_pass")
        if st.button("Daftar", key="reg_btn"):
            if new_user.strip() and new_pass.strip():
                st.session_state.users[new_user] = new_pass
                st.success("Pendaftaran berhasil! Silahkan login.")
            else:
                st.warning("Isi username dan password dengan benar.")

    if st.session_state.user_login:
        st.header(f"👋 Selamat datang, {st.session_state.user_login}")
        # Load menu
        if os.path.exists(MENU_FILE):
            with open(MENU_FILE,"r",encoding="utf-8") as f:
                menu_data = json.load(f)
        else:
            menu_data = {"makanan":{"Mie Ayam":15000,"Bakso":18000},
                         "minuman":{"Es Teh":5000,"Es Jeruk":7000}}

        # Menu Pesan
        st.subheader("🍽️ Menu Makanan")
        for item, harga in menu_data["makanan"].items():
            col1, col2 = st.columns([3,1])
            with col1: st.write(f"{item} - Rp {harga:,}")
            with col2:
                if st.button(f"Tambah {item}"):
                    st.session_state.cart[item] = st.session_state.cart.get(item,0)+1

        st.subheader("🥤 Menu Minuman")
        for item, harga in menu_data["minuman"].items():
            col1, col2 = st.columns([3,1])
            with col1: st.write(f"{item} - Rp {harga:,}")
            with col2:
                if st.button(f"Tambah {item}"):
                    st.session_state.cart[item] = st.session_state.cart.get(item,0)+1

        # Keranjang
        st.subheader("🛒 Keranjang")
        if st.session_state.cart:
            total = 0
            for k,v in st.session_state.cart.items():
                harga = menu_data["makanan"].get(k, menu_data["minuman"].get(k,0))
                st.write(f"{k} x {v} = Rp {v*harga:,}")
                total += v*harga
            st.info(f"Total: Rp {total:,}")
            
            bayar = st.number_input("Uang Diterima", min_value=0, value=total, step=1000)
            if st.button("Bayar"):
                if bayar>=total:
                    kembalian = bayar - total
                    st.success(f"✅ Pembayaran berhasil! Kembalian: Rp {kembalian:,}")
                    # Simpan transaksi
                    record={"timestamp":datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            "nama":st.session_state.user_login,
                            "items":json.dumps(st.session_state.cart,ensure_ascii=False),
                            "total":total,
                            "bayar":bayar,
                            "kembalian":kembalian}
                    df=pd.DataFrame([record])
                    if os.path.exists(DATA_FILE):
                        df.to_csv(DATA_FILE,mode="a",header=False,index=False,encoding="utf-8-sig")
                    else:
                        df.to_csv(DATA_FILE,index=False,encoding="utf-8-sig")
                    st.session_state.cart = {}
                else:
                    st.error("Uang kurang!")
        else:
            st.info("Keranjang kosong.")
