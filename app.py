import streamlit as st
from kasir_mas_ragil import admin_app, user_app

st.set_page_config(page_title="Kasir Mas Ragil", page_icon="🍜", layout="wide")

# Pilih role
if "role" not in st.session_state:
    st.session_state.role = None  # "admin" / "user"

st.title("🍜 Kasir Mas Ragil")

col1, col2 = st.columns([2,1])
with col1:
    role_select = st.selectbox("Masuk sebagai:", ["Pilih Role","User","Admin"])
    if role_select != "Pilih Role":
        st.session_state.role = role_select.lower()

# Jalankan modul sesuai role
if st.session_state.role == "admin":
    admin_app.run_admin()
elif st.session_state.role == "user":
    user_app.run_user()
else:
    st.info("Silahkan pilih role di atas untuk mulai.")
