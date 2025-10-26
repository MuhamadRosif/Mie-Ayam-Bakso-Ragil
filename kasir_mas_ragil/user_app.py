import streamlit as st
import json, os
from datetime import datetime

MENU_FILE = "kasir_mas_ragil/menu.json"
DATA_FILE = "kasir_mas_ragil/riwayat_penjualan.csv"

def run_user():
    if "login_user" not in st.session_state:
        st.session_state.login_user = False
    if "user_registered" not in st.session_state:
        st.session_state.user_registered = False

    # Registrasi & Login
    if not st.session_state.login_user:
        st.header("📝 Registrasi / Login User")
        if not st.session_state.user_registered:
            st.subheader("Registrasi User")
            username = st.text_input("Username", key="reg_user")
            password = st.text_input("Password", type="password", key="reg_pass")
            if st.button("Daftar", key="btn_register"):
                if username.strip() and password.strip():
                    st.session_state.user_registered = True
                    st.session_state.user_credentials = {"username":username,"password":password}
                    st.success("Registrasi berhasil! Silakan login.")
                    st.experimental_rerun()
                else:
                    st.warning("Isi username dan password.")
        else:
            st.subheader("Login User")
            username = st.text_input("Username", key="login_user_input")
            password = st.text_input("Password", type="password", key="login_user_pass")
            if st.button("Login", key="btn_login_user"):
                creds = st.session_state.user_credentials
                if username == creds["username"] and password == creds["password"]:
                    st.session_state.login_user = True
                    st.experimental_rerun()
                else:
                    st.error("Username atau password salah.")
        return

    # -------------------
    # Halaman User
    # -------------------
    st.header("🏠 Beranda Mie Ayam & Bakso Mas Ragil 🍜")

    # Load menu
    if os.path.exists(MENU_FILE):
        with open(MENU_FILE,"r",encoding="utf-8") as f:
            menu_data = json.load(f)
            menu_makanan = menu_data.get("makanan",{})
            menu_minuman = menu_data.get("minuman",{})
    else:
        menu_makanan = {"Mie Ayam":15000}
        menu_minuman = {"Es Teh":5000}

    if "cart" not in st.session_state:
        st.session_state.cart = {}

    st.subheader("🍽️ Menu Makanan")
    for item, harga in menu_makanan.items():
        col1,col2 = st.columns([3,1])
        with col1: st.write(f"{item} (Rp {harga:,})")
        with col2:
            if st.button(f"Tambah {item}", key=f"makanan-{item}"):
                st.session_state.cart[item] = st.session_state.cart.get(item,0)+1

    st.subheader("🥤 Menu Minuman")
    for item, harga in menu_minuman.items():
        col1,col2 = st.columns([3,1])
        with col1: st.write(f"{item} (Rp {harga:,})")
        with col2:
            if st.button(f"Tambah {item}", key=f"minum-{item}"):
                st.session_state.cart[item] = st.session_state.cart.get(item,0)+1

    # Tampilkan keranjang
    if st.session_state.cart:
        st.subheader("🛒 Keranjang")
        total = 0
        for k,v in st.session_state.cart.items():
            harga_satuan = menu_makanan.get(k, menu_minuman.get(k,0))
            subtotal = harga_satuan*v
            st.write(f"{k} x {v} = Rp {subtotal:,}")
            total += subtotal
        st.info(f"Total Bayar: Rp {total:,}")

        if st.button("🧾 Checkout", key="btn_checkout"):
            # Simpan ke file penjualan
            record = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "nama": st.session_state.user_credentials["username"],
                "items": json.dumps(st.session_state.cart,ensure_ascii=False),
                "total": total
            }
            import pandas as pd
            df = pd.DataFrame([record])
            if os.path.exists(DATA_FILE):
                df.to_csv(DATA_FILE,mode="a",header=False,index=False,encoding="utf-8-sig")
            else:
                df.to_csv(DATA_FILE,index=False,encoding="utf-8-sig")
            st.success("Pesanan berhasil! Admin dapat melihat laporan.")
            st.session_state.cart = {}
