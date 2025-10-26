import streamlit as st
import json, os
from datetime import datetime

MENU_FILE = "kasir_mas_ragil/menu.json"
KERANJANG_FILE = "kasir_mas_ragil/keranjang.json"
USER_FILE = "kasir_mas_ragil/users.json"

def load_menu():
    if os.path.exists(MENU_FILE):
        with open(MENU_FILE,"r",encoding="utf-8") as f:
            data = json.load(f)
            return data.get("makanan",{}), data.get("minuman",{})
    return {}, {}

def save_keranjang(data):
    with open(KERANJANG_FILE,"w",encoding="utf-8") as f:
        json.dump(data,f,ensure_ascii=False,indent=2)

def load_keranjang():
    if os.path.exists(KERANJANG_FILE):
        with open(KERANJANG_FILE,"r",encoding="utf-8") as f:
            return json.load(f)
    return {}

def register_user(username,password):
    users = {}
    if os.path.exists(USER_FILE):
        with open(USER_FILE,"r",encoding="utf-8") as f:
            users = json.load(f)
    if username in users:
        return False
    users[username] = password
    with open(USER_FILE,"w",encoding="utf-8") as f:
        json.dump(users,f,ensure_ascii=False,indent=2)
    return True

def login_user(username,password):
    if os.path.exists(USER_FILE):
        with open(USER_FILE,"r",encoding="utf-8") as f:
            users = json.load(f)
            return users.get(username)==password
    return False

def run_user():
    st.title("🍜 Kasir Mas Ragil — User")

    if "user_login" not in st.session_state:
        st.session_state.user_login = False
        st.session_state.username = ""

    if not st.session_state.user_login:
        tab = st.tabs(["Login","Registrasi"])
        with tab[0]:
            username = st.text_input("Username", key="login_user")
            password = st.text_input("Password", type="password", key="login_pass")
            if st.button("Login"):
                if login_user(username,password):
                    st.session_state.user_login = True
                    st.session_state.username = username
                    st.success(f"Selamat datang {username}!")
                    st.experimental_rerun()
                else:
                    st.error("Username atau password salah")
        with tab[1]:
            new_user = st.text_input("Username", key="reg_user")
            new_pass = st.text_input("Password", type="password", key="reg_pass")
            if st.button("Daftar"):
                if register_user(new_user,new_pass):
                    st.success("Registrasi berhasil! Silakan login.")
                else:
                    st.error("Username sudah ada")
        return

    # ------------------- Menu Pemesanan -------------------
    makanan,minuman = load_menu()
    if "pesanan" not in st.session_state:
        st.session_state.pesanan = load_keranjang().get(st.session_state.username,{})

    st.header("🍽️ Menu Makanan")
    for item,harga in makanan.items():
        col1,col2,col3,col4 = st.columns([3,1,1,2])
        with col1: st.write(f"**{item}** (Rp {harga:,})")
        with col2:
            if st.button("-", key=f"{item}-minus"):
                st.session_state.pesanan[item] = max(0, st.session_state.pesanan.get(item,0)-1)
        with col3: st.write(f"Qty: {st.session_state.pesanan.get(item,0)}")
        with col4:
            if st.button("+", key=f"{item}-plus"):
                st.session_state.pesanan[item] = st.session_state.pesanan.get(item,0)+1

    st.header("🥤 Menu Minuman")
    for item,harga in minuman.items():
        col1,col2,col3,col4 = st.columns([3,1,1,2])
        with col1: st.write(f"**{item}** (Rp {harga:,})")
        with col2:
            if st.button("-", key=f"{item}-minus-minum"):
                st.session_state.pesanan[item] = max(0, st.session_state.pesanan.get(item,0)-1)
        with col3: st.write(f"Qty: {st.session_state.pesanan.get(item,0)}")
        with col4:
            if st.button("+", key=f"{item}-plus-minum"):
                st.session_state.pesanan[item] = st.session_state.pesanan.get(item,0)+1

    st.subheader("📋 Keranjang Anda")
    pesanan_aktif = {k:v for k,v in st.session_state.pesanan.items() if v>0}
    if pesanan_aktif:
        total = 0
        for k,v in pesanan_aktif.items():
            h = makanan.get(k, minuman.get(k,0))
            total += v*h
            st.write(f"{k} x {v} = Rp {v*h:,}")
        st.info(f"Total: Rp {total:,}")
        if st.button("Simpan ke keranjang"):
            keranjang_all = load_keranjang()
            keranjang_all[st.session_state.username] = pesanan_aktif
            save_keranjang(keranjang_all)
            st.success("Pesanan tersimpan, admin akan memproses pembayaran.")
    else:
        st.info("Keranjang kosong.")
