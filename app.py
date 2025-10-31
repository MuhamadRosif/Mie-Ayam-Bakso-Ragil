# ====== FIX PATH UNTUK SERVER / DEPLOY ======
import sys, os
sys.path.append(os.path.dirname(__file__))

import streamlit as st
from kasir_mas_ragil.admin_app import run_admin
from kasir_mas_ragil.user_app import run_user

# ====== KONFIGURASI STREAMLIT ======
st.set_page_config(page_title="Mie Ayam Bakso Mas Ragil", page_icon="🍜", layout="centered")

# ====== CUSTOM CSS ======
st.markdown("""
<style>
body {
    background: url('https://images.unsplash.com/photo-1606755962773-0e2d7efc4b5b') no-repeat center center fixed;
    background-size: cover;
    font-family: 'Poppins', sans-serif;
}
.overlay {
    background: rgba(0, 0, 0, 0.6);
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    z-index: 0;
}
.login-card {
    position: relative;
    z-index: 1;
    max-width: 400px;
    margin: 5rem auto;
    padding: 3rem 2rem 2rem;
    background: rgba(255, 183, 77, 0.18);
    backdrop-filter: blur(14px);
    border-radius: 25px;
    box-shadow: 0 0 25px rgba(255, 150, 0, 0.3);
    text-align: center;
    color: #fff;
}
.header h2 {
    font-weight: 700;
    color: #ffcc00;
    text-shadow: 0 0 15px rgba(255,200,50,0.6);
}
.stTextInput>div>div>input {
    background-color: rgba(255,255,255,0.15);
    color: white !important;
    border-radius: 10px;
}
.stButton>button {
    width: 100%;
    height: 45px;
    border-radius: 12px;
    border: none;
    background: linear-gradient(270deg, #ff6b00, #ffb300);
    font-weight: 700;
    cursor: pointer;
}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ====== SESSION LOGIN ======
if "role" not in st.session_state:
    st.session_state.role = None

# ====== LOGIN PAGE ======
def login_page():
    st.markdown("<div class='overlay'></div>", unsafe_allow_html=True)
    st.markdown("<div class='login-card'>", unsafe_allow_html=True)

    st.markdown("<h2>Selamat Datang di<br>Mie Ayam Bakso Mas Ragil 🍜</h2>", unsafe_allow_html=True)

    role = st.selectbox("Masuk sebagai", ["Pelanggan", "Admin"])
    username = st.text_input("Email / ID Pengguna")
    password = st.text_input("Password", type="password")
    
    login = st.button("MASUK")

    if login:
        if role == "Admin":
            if username == "admin" and password == "123":
                st.session_state.role = "admin"
                st.rerun()
            else:
                st.error("ID atau password admin salah!")
        else:
            if username == "user" and password == "123":
                st.session_state.role = "user"
                st.rerun()
            else:
                st.error("Email atau password pelanggan salah!")

    st.markdown("</div>", unsafe_allow_html=True)

# ====== ROUTING ======
if st.session_state.role == "admin":
    st.sidebar.button("🚪 Logout", on_click=lambda: st.session_state.update({"role": None}))
    run_admin()

elif st.session_state.role == "user":
    st.sidebar.button("🚪 Logout", on_click=lambda: st.session_state.update({"role": None}))
    run_user()

else:
    login_page()
