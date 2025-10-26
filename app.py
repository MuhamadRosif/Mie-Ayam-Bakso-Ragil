import streamlit as st
from kasir_mas_ragil import admin_app, user_app

st.set_page_config(page_title="Kasir Mas Ragil", page_icon="🍜", layout="wide")

# Session state default
if "admin_login" not in st.session_state:
    st.session_state.admin_login = False
if "user_login" not in st.session_state:
    st.session_state.user_login = False

# Pilih role
role_choice = st.radio("Login sebagai:", ["Admin", "User"], key="role_select_unique")

if role_choice == "Admin":
    admin_app.run_admin()
else:
    user_app.run_user()
