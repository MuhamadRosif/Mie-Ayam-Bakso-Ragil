# app.py
import streamlit as st
from kasir_mas_ragil import admin_app, user_app

st.set_page_config(page_title="Kasir Mas Ragil", page_icon="🍜", layout="wide")

st.title("🍜 Kasir Mas Ragil")

# Pilih role login
if "role_selected" not in st.session_state:
    st.session_state.role_selected = False

if not st.session_state.role_selected:
    st.subheader("Login sebagai:")
    role_choice = st.radio("", ["Admin","User"], key="role_radio")
    if st.button("Lanjut"):
        st.session_state.role = role_choice
        st.session_state.role_selected = True
        st.experimental_rerun()
else:
    role_choice = st.session_state.role

# Panggil aplikasi sesuai role
if role_choice=="Admin":
    admin_app.run_admin()
else:
    user_app.run_user()
