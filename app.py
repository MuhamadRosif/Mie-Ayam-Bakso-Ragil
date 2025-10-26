import streamlit as st
from kasir_mas_ragil import admin_app, user_app

st.set_page_config(page_title="Kasir Mas Ragil", page_icon="🍜", layout="wide")

# Pilihan role login
role = st.selectbox("Pilih Mode:", ["User", "Admin"])

if role == "Admin":
    admin_app.run_admin_app()
else:
    user_app.run_user_app()
