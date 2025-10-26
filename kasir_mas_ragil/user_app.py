import streamlit as st
import json
import os

MENU_FILE = "kasir_mas_ragil/menu.json"
PESANAN_FILE = "kasir_mas_ragil/user_pesanan.json"

def run_user():
    st.title("🍜 Kasir Mas Ragil — User Panel")
    
    # Session state
    if "user_login" not in st.session_state:
        st.session_state.user_login = False
    if "user_name" not in st.session_state:
        st.session_state.user_name = ""
    if "cart" not in st.session_state:
        st.session_state.cart = {}
    
    if not st.session_state.user_login:
        # Registrasi/Login
        st.subheader("🔑 Login / Registrasi User")
        username = st.text_input("Nama Pengguna")
        if st.button("Login / Register", key="user_login_btn"):
            if username.strip():
                st.session_state.user_login = True
                st.session_state.user_name = username.strip()
                st.experimental_rerun()
            else:
                st.warning("Masukkan nama pengguna")
        return
    
    st.write(f"Selamat datang, **{st.session_state.user_name}**")
    
    # Load menu
    if os.path.exists(MENU_FILE):
        with open(MENU_FILE,"r",encoding="utf-8") as f:
            menu_data = json.load(f)
    else:
        menu_data = {"makanan": {}, "minuman": {}}
    
    # Tampilkan menu
    st.subheader("🍽️ Menu Makanan")
    for item, harga in menu_data.get("makanan", {}).items():
        col1,col2,col3 = st.columns([3,1,2])
        with col1: st.write(f"**{item}** (Rp {harga:,})")
        with col2:
            if st.button("+", key=f"makanan_plus_{item}"):
                st.session_state.cart[item] = st.session_state.cart.get(item,0)+1
        with col3:
            st.write(f"Qty: {st.session_state.cart.get(item,0)}")
    
    st.subheader("🥤 Menu Minuman")
    for item, harga in menu_data.get("minuman", {}).items():
        col1,col2,col3 = st.columns([3,1,2])
        with col1: st.write(f"**{item}** (Rp {harga:,})")
        with col2:
            if st.button("+", key=f"minum_plus_{item}"):
                st.session_state.cart[item] = st.session_state.cart.get(item,0)+1
        with col3:
            st.write(f"Qty: {st.session_state.cart.get(item,0)}")
    
    # Keranjang
    st.subheader("🛒 Keranjang")
    if st.session_state.cart:
        for k,v in st.session_state.cart.items():
            st.write(f"{k} x {v}")
        if st.button("Submit Pesanan ke Admin"):
            # Simpan ke file
            if os.path.exists(PESANAN_FILE):
                with open(PESANAN_FILE,"r",encoding="utf-8") as f:
                    data = json.load(f)
            else:
                data = {}
            data[st.session_state.user_name] = st.session_state.cart
            with open(PESANAN_FILE,"w",encoding="utf-8") as f:
                json.dump(data,f,ensure_ascii=False,indent=2)
            st.success("Pesanan dikirim ke admin!")
            st.session_state.cart = {}
            st.experimental_rerun()
    else:
        st.info("Belum ada item di keranjang.")
