import streamlit as st
from kasir_mas_ragil import admin_app, user_app

st.set_page_config(page_title="Kasir Mas Ragil", page_icon="🍜", layout="wide")

# Pilih role
role_choice = st.radio("Login sebagai:", ["Admin", "User"], key="role_select")

if role_choice == "Admin":
    admin_app.run_admin()
else:
    user_app.run_user()
