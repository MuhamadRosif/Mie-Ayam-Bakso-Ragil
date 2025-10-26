# =========================
# user_app.py — Kasir Mas Ragil
# =========================
import streamlit as st
import json
import os

MENU_FILE = "kasir_mas_ragil/menu.json"
USERS_FILE = "kasir_mas_ragil/users.json"

def load_menu():
    if os.path.exists(MENU_FILE):
        with open(MENU_FILE,"r",encoding="utf-8") as f:
            data = json.load(f)
            return data.get("makanan",{}), data.get("minuman",{})
    else:
        # default menu jika file belum ada
        makanan = {"Mie Ayam":15000,"Bakso Urat":18000,"Mie Ayam Bakso":20000,"Bakso Telur":19000}
        minuman = {"Es Teh Manis":5000,"Es Jeruk":7000,"Teh Hangat":5000,"Jeruk Hangat":6000}
        with open(MENU_FILE,"w",encoding="utf-8") as f:
            json.dump({"makanan":makanan,"minuman":minuman}, f, ensure_ascii=False, indent=2)
        return makanan, minuman

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE,"r",encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE,"w",encoding="utf-8") as f:
        json.dump(users,f,ensure_ascii=False,indent=2)

def run_user():
    st.set_page_config(page_title="Kasir Mas Ragil - User", page_icon="🍜", layout="wide")
    
    # ------------------------------------
    # Inisialisasi session state
    # ------------------------------------
    if "user_login" not in st.session_state:
        st.session_state.user_login = False
    if "username" not in st.session_state:
        st.session_state.username = ""
    if "cart" not in st.session_state:
        st.session_state.cart = {}
    
    st.markdown("""
    <style>
    .stApp {background: linear-gradient(180deg,#071026,#0b1440); color:#e6eef8;}
    .login-card {background-color:#1b1b1b; padding:30px; border-radius:12px; width:360px; 
                 margin:100px auto; text-align:center; box-shadow:0 4px 20px rgba(0,0,0,0.4);}
    .stTextInput>div>div>input {background-color:#2b2b2b; color:#fff; border-radius:6px;}
    .stButton>button {background-color:#c62828; color:white; border:none; border-radius:6px; padding:8px 20px;}
    </style>
    """, unsafe_allow_html=True)
    
    # ------------------------------------
    # Login / Registrasi
    # ------------------------------------
    if not st.session_state.user_login:
        st.markdown('<div class="login-card"><h3>🔐 Login / Registrasi User</h3>', unsafe_allow_html=True)
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        col1, col2 = st.columns(2)
        users = load_users()
        with col1:
            if st.button("Login"):
                if username in users and users[username]==password:
                    st.session_state.user_login = True
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error("Username atau password salah.")
        with col2:
            if st.button("Registrasi"):
                if username.strip()=="" or password.strip()=="":
                    st.warning("Isi username dan password!")
                elif username in users:
                    st.warning("Username sudah terdaftar!")
                else:
                    users[username] = password
                    save_users(users)
                    st.success("Registrasi berhasil! Silakan login.")
        st.markdown('</div>', unsafe_allow_html=True)
        st.stop()
    
    # ------------------------------------
    # User sudah login
    # ------------------------------------
    st.header(f"👋 Selamat datang, {st.session_state.username}!")
    
    makanan, minuman = load_menu()
    
    st.subheader("🍽️ Menu Makanan")
    for item,harga in makanan.items():
        col1,col2,col3,col4 = st.columns([3,1,1,2])
        with col1: st.write(f"**{item}** (Rp {harga:,})")
        with col2:
            if st.button("-", key=f"{item}-minus"):
                st.session_state.cart[item] = max(0, st.session_state.cart.get(item,0)-1)
        with col3:
            st.write(f"Qty: {st.session_state.cart.get(item,0)}")
        with col4:
            if st.button("+", key=f"{item}-plus"):
                st.session_state.cart[item] = st.session_state.cart.get(item,0)+1
    
    st.subheader("🥤 Menu Minuman")
    for item,harga in minuman.items():
        col1,col2,col3,col4 = st.columns([3,1,1,2])
        with col1: st.write(f"**{item}** (Rp {harga:,})")
        with col2:
            if st.button("-", key=f"{item}-minus-minum"):
                st.session_state.cart[item] = max(0, st.session_state.cart.get(item,0)-1)
        with col3:
            st.write(f"Qty: {st.session_state.cart.get(item,0)}")
        with col4:
            if st.button("+", key=f"{item}-plus-minum"):
                st.session_state.cart[item] = st.session_state.cart.get(item,0)+1
    
    # ------------------------------------
    # Keranjang
    # ------------------------------------
    st.subheader("🛒 Keranjang Pesanan")
    cart_items = {k:v for k,v in st.session_state.cart.items() if v>0}
    if cart_items:
        total = 0
        for k,v in cart_items.items():
            harga_satuan = makanan.get(k, minuman.get(k,0))
            subtotal = harga_satuan*v
            total += subtotal
            st.write(f"{k} x {v} = Rp {subtotal:,}")
        st.info(f"💰 Total: Rp {total:,}")
        if st.button("Reset Keranjang"):
            st.session_state.cart = {}
            st.rerun()
    else:
        st.info("Belum ada pesanan.")
    
    if st.button("Logout"):
        st.session_state.user_login = False
        st.session_state.username = ""
        st.session_state.cart = {}
        st.rerun()
