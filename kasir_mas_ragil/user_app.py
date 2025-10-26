# kasir_mas_ragil/user_app.py
import streamlit as st
import json
import os
from datetime import datetime

MENU_FILE = "kasir_mas_ragil/menu.json"
CHECKOUT_FILE = "kasir_mas_ragil/checkout.json"

# ------------------------------
# Fungsi load menu
# ------------------------------
def load_menu():
    if os.path.exists(MENU_FILE):
        with open(MENU_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("makanan", {}), data.get("minuman", {})
    else:
        makanan = {"Mie Ayam":15000, "Bakso Urat":18000}
        minuman = {"Es Teh Manis":5000, "Es Jeruk":7000}
        with open(MENU_FILE, "w", encoding="utf-8") as f:
            json.dump({"makanan":makanan, "minuman":minuman}, f, ensure_ascii=False, indent=2)
        return makanan, minuman

# ------------------------------
# Fungsi load checkout
# ------------------------------
def load_checkout():
    if os.path.exists(CHECKOUT_FILE):
        with open(CHECKOUT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        with open(CHECKOUT_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        return []

def save_checkout(data):
    with open(CHECKOUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ------------------------------
# User App
# ------------------------------
def run_user():
    st.markdown("<h2>🍜 User Kasir Mas Ragil</h2>", unsafe_allow_html=True)

    if "user_login" not in st.session_state:
        st.session_state.user_login = False
    if "user_name" not in st.session_state:
        st.session_state.user_name = ""
    if "keranjang" not in st.session_state:
        st.session_state.keranjang = {}

    # --------------------------
    # Login & Register Button
    # --------------------------
    if not st.session_state.user_login:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔑 Login"):
                st.session_state.user_action = "login"
        with col2:
            if st.button("📝 Daftar"):
                st.session_state.user_action = "register"

        action = st.session_state.get("user_action", None)

        if action == "login":
            st.subheader("Login User")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.button("Masuk"):
                # Simple auth: simpan di checkout.json sebagai user list
                users = load_checkout()
                found = False
                for u in users:
                    if u["username"] == username and u.get("password","") == password:
                        found = True
                        break
                if found:
                    st.success(f"Login berhasil! Selamat datang {username}")
                    st.session_state.user_login = True
                    st.session_state.user_name = username
                    st.rerun()
                else:
                    st.error("Username atau password salah!")

        elif action == "register":
            st.subheader("Daftar User Baru")
            username = st.text_input("Username Baru")
            password = st.text_input("Password Baru", type="password")
            if st.button("Daftar"):
                users = load_checkout()
                # cek username unik
                if any(u["username"]==username for u in users):
                    st.warning("Username sudah terdaftar")
                elif username.strip()=="" or password.strip()=="":
                    st.warning("Isi username dan password")
                else:
                    users.append({"username":username, "password":password, "checkout":[]})
                    save_checkout(users)
                    st.success("Pendaftaran berhasil! Silakan login")
                    st.session_state.user_action = "login"
                    st.rerun()

    else:
        # --------------------------
        # User Sudah Login
        # --------------------------
        st.write(f"Selamat datang, **{st.session_state.user_name}**!")
        if st.button("🚪 Logout"):
            st.session_state.user_login = False
            st.session_state.user_name = ""
            st.session_state.keranjang = {}
            st.session_state.user_action = None
            st.rerun()

        # --------------------------
        # Menu dan Keranjang
        # --------------------------
        makanan, minuman = load_menu()
        st.subheader("🍽️ Menu Makanan")
        for item, harga in makanan.items():
            col1,col2,col3,col4 = st.columns([3,1,1,2])
            with col1: st.write(f"**{item}** (Rp {harga:,})")
            with col2:
                if st.button("-", key=f"{item}-minus"): st.session_state.keranjang[item] = max(0, st.session_state.keranjang.get(item,0)-1)
            with col3: st.write(f"Qty: {st.session_state.keranjang.get(item,0)}")
            with col4:
                if st.button("+", key=f"{item}-plus"): st.session_state.keranjang[item] = st.session_state.keranjang.get(item,0)+1

        st.subheader("🥤 Menu Minuman")
        for item, harga in minuman.items():
            col1,col2,col3,col4 = st.columns([3,1,1,2])
            with col1: st.write(f"**{item}** (Rp {harga:,})")
            with col2:
                if st.button("-", key=f"{item}-minus-minum"): st.session_state.keranjang[item] = max(0, st.session_state.keranjang.get(item,0)-1)
            with col3: st.write(f"Qty: {st.session_state.keranjang.get(item,0)}")
            with col4:
                if st.button("+", key=f"{item}-plus-minum"): st.session_state.keranjang[item] = st.session_state.keranjang.get(item,0)+1

        keranjang_aktif = {k:v for k,v in st.session_state.keranjang.items() if v>0}
        if keranjang_aktif:
            st.markdown("**📋 Keranjang Saat Ini:**")
            subtotal = 0
            for k,v in keranjang_aktif.items():
                harga_satuan = makanan.get(k, minuman.get(k,0))
                st.write(f"{k} x {v} = Rp {v*harga_satuan:,}")
                subtotal += v*harga_satuan
            st.info(f"Subtotal: Rp {subtotal:,}")
            if st.button("✅ Checkout"):
                # Tambahkan ke checkout.json untuk admin proses
                users = load_checkout()
                for u in users:
                    if u["username"] == st.session_state.user_name:
                        u["checkout"].append({"items":keranjang_aktif, "subtotal":subtotal, "timestamp":datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
                        break
                save_checkout(users)
                st.success("Pesanan berhasil dikirim ke admin untuk pembayaran!")
                st.session_state.keranjang = {}
        else:
            st.info("Belum ada item di keranjang.")
