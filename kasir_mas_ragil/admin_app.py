import streamlit as st

def run_admin():
    st.header("🛠️ Admin Dashboard")
    if st.button("Logout Admin"):
        st.session_state.admin_login = False
        st.session_state.role = None
        st.experimental_rerun()

    st.subheader("📈 Laporan Penjualan")
    st.info("Ini halaman admin, kamu bisa tambahkan laporan, menu admin, dll.")
