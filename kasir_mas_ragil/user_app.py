import streamlit as st
from kasir_mas_ragil import admin_app, user_app

st.set_page_config(page_title="Kasir Mas Ragil", page_icon="🍜", layout="wide")

# Session defaults
if "role" not in st.session_state:
    st.session_state.role = None
if "admin_login" not in st.session_state:
    st.session_state.admin_login = False
if "user_login" not in st.session_state:
    st.session_state.user_login = False
if "username" not in st.session_state:
    st.session_state.username = ""

# Login awal
st.title("🍜 Kasir Mas Ragil — Login")
role_choice = st.radio("Login sebagai:", ["Admin", "User"])

if role_choice == "Admin":
    username = st.text_input("Username Admin")
    password = st.text_input("Password Admin", type="password")
    if st.button("Masuk Admin"):
        if username.strip() == "admin" and password.strip() == "1234":
            st.session_state.admin_login = True
            st.session_state.role = "admin"
            st.experimental_rerun()
        else:
            st.error("Username atau password salah!")

elif role_choice == "User":
    user_app.run_user()  # Fungsi user login / registrasi di user_app.py

# Arahkan setelah login
if st.session_state.role == "admin" and st.session_state.admin_login:
    admin_app.run_admin()  # Fungsi dashboard admin
