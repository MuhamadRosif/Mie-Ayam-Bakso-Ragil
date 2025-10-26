# kasir_mas_ragil/user_app.py
import streamlit as st
import os
import json
from datetime import datetime

MENU_FILE = "kasir_mas_ragil/menu.json"
CHECKOUT_FILE = "kasir_mas_ragil/checkout.json"

# =====================
# Fungsi simpan & load
# =====================
def load_menu():
    if os.path.exists(MENU_FILE):
        with open(MENU_FILE,"r",encoding="utf-8") as f:
            return json.load(f)
    else:
        default_menu = {
            "makanan":{"Mie Ayam":15000,"Bakso Urat":18000,"Mie Ayam Bakso":20000,"Bakso Telur":19000},
            "minuman":{"Es Teh Manis":5000,"Es Jeruk":7000,"Teh Hangat":5000,"Jeruk Hangat":6000}
        }
        with open(MENU_FILE,"w",encoding="utf-8") as f:
            json.dump(default_menu,f,ensure_ascii=False,indent=2)
        return default_menu

def save_checkout(user_data):
    if os.path.exists(CHECKOUT_FILE):
        with open(CHECKOUT_FILE,"r",encoding="utf-8") as f:
            all_data = json.load(f)
    else:
        all_data = []
    all_data.append(user_data)
    with open(CHECKOUT_FILE,"w",encoding="utf-8") as f:
        json.dump(all_data,f,ensure_ascii=False,indent=2)

# =====================
# Fungsi User
# =====================
def run_user():
    st.header("👤 User Panel — Kasir Mas Ragil")

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.username = ""

    if not st.session_state.logged_in:
        st.subheader("📝 Registrasi / Login User")
        username = st.text_input("Nama")
        if st.button("Masuk / Daftar"):
            if username.strip():
                st.session_state.logged_in = True
                st.session_state.username = username.strip()
                st.session_state.cart = {}
                st.success(f"Selamat datang, {st.session_state.username}!")
                st.rerun()
            else:
                st.warning("Masukkan nama Anda terlebih dahulu.")
    else:
        st.subheader(f"Selamat datang, {st.session_state.username}!")
        menu = load_menu()
        # ----------------
        st.subheader("🍽️ Menu Makanan")
        for item, harga in menu["makanan"].items():
            col1,col2,col3 = st.columns([3,1,1])
            with col1: st.write(f"{item} — Rp {harga:,}")
            with col2:
                if st.button("-", key=f"m-{item}"): 
                    st.session_state.cart[item] = max(0, st.session_state.cart.get(item,0)-1)
            with col3:
                if st.button("+", key=f"p-{item}"): 
                    st.session_state.cart[item] = st.session_state.cart.get(item,0)+1

        st.subheader("🥤 Menu Minuman")
        for item, harga in menu["minuman"].items():
            col1,col2,col3 = st.columns([3,1,1])
            with col1: st.write(f"{item} — Rp {harga:,}")
            with col2:
                if st.button("-", key=f"m-{item}-minum"): 
                    st.session_state.cart[item] = max(0, st.session_state.cart.get(item,0)-1)
            with col3:
                if st.button("+", key=f"p-{item}-minum"): 
                    st.session_state.cart[item] = st.session_state.cart.get(item,0)+1

        # ----------------
        cart_items = {k:v for k,v in st.session_state.cart.items() if v>0}
        if cart_items:
            st.subheader("🛒 Keranjang Pesanan")
            total = 0
            for k,v in cart_items.items():
                harga = menu["makanan"].get(k, menu["minuman"].get(k,0))
                subtotal = v*harga
                total += subtotal
                st.write(f"{k} x {v} = Rp {subtotal:,}")
            st.info(f"Total sementara: Rp {total:,}")

            if st.button("✅ Checkout"):
                user_data = {
                    "username": st.session_state.username,
                    "cart": cart_items,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                save_checkout(user_data)
                st.success("Pesanan berhasil di checkout! Silahkan tunggu admin memproses pembayaran.")
                st.session_state.cart = {}
        else:
            st.info("Belum ada item di keranjang.")
