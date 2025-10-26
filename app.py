import streamlit as st
from kasir_mas_ragil import admin_app, user_app

# Session login
if "login" not in st.session_state:
    st.session_state.login = False
if "role" not in st.session_state:
    st.session_state.role = None  # 'admin' atau 'user'

# Halaman login sederhana
if not st.session_state.login:
    st.title("🔐 Login Kasir Mas Ragil")
    role = st.selectbox("Login sebagai", ["User", "Admin"])
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Masuk"):
        if role=="Admin" and username=="admin" and password=="1234":
            st.session_state.login = True
            st.session_state.role = "admin"
            st.experimental_rerun()
        elif role=="User":  # user bisa login tanpa password
            st.session_state.login = True
            st.session_state.role = "user"
            st.experimental_rerun()
        else:
            st.error("Username/password salah")

# Jalankan modul sesuai role
if st.session_state.login:
    if st.session_state.role=="admin":
        admin_app.run()
    elif st.session_state.role=="user":
        user_app.run()
