import streamlit as st
from kasir_mas_ragil import user_app, admin_app

# ===============================
# CONFIG
# ===============================
st.set_page_config(page_title="Rumah Makan Mas Ragil", page_icon="🍜", layout="wide")

# ===============================
# CUSTOM STYLE
# ===============================
st.markdown("""
<style>
/* ====== NAVBAR ====== */
.navbar {
    background-color: #0b1e3f;
    color: white;
    padding: 14px 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-radius: 0 0 12px 12px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.3);
    font-family: 'Segoe UI', sans-serif;
}
.nav-title {
    font-size: 20px;
    font-weight: bold;
    letter-spacing: 0.5px;
}
.menu-icon {
    cursor: pointer;
    font-size: 24px;
    color: #4db8ff;
    transition: 0.3s;
}
.menu-icon:hover {
    color: #7fd3ff;
}

/* ====== SIDEBAR ====== */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0b1e3f, #124b7e);
    color: white !important;
    animation: slideIn 0.3s ease-in-out;
}
@keyframes slideIn {
    from { transform: translateX(100%); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
}
[data-testid="stSidebarNav"] span {
    color: white !important;
}
.stButton>button {
    background-color: #1565c0;
    color: white;
    border-radius: 8px;
    padding: 8px 20px;
    font-weight: 600;
    border: none;
}
.stButton>button:hover {
    background-color: #1976d2;
}

/* ====== LOGIN BOX ====== */
.login-box {
    background-color: #0b1e3f;
    color: white;
    padding: 40px;
    border-radius: 16px;
    width: 360px;
    margin: 80px auto;
    box-shadow: 0px 8px 25px rgba(0,0,0,0.35);
    text-align: center;
}
.login-box h2 {
    font-size: 26px;
    margin-bottom: 10px;
}
.login-box label {
    float: left;
    color: #c9d6e3;
    font-size: 15px;
}
.login-button {
    background-color: #1565c0;
    color: white;
    border: none;
    padding: 10px 0;
    width: 100%;
    border-radius: 8px;
    font-size: 16px;
    margin-top: 20px;
}
.login-button:hover {
    background-color: #1976d2;
    cursor: pointer;
}
.forgot {
    font-size: 13px;
    color: #f9d46e;
    margin-top: 12px;
}
</style>
""", unsafe_allow_html=True)

# ===============================
# SESSION
# ===============================
if "is_logged_in" not in st.session_state:
    st.session_state.is_logged_in = False
if "role" not in st.session_state:
    st.session_state.role = None
if "show_sidebar" not in st.session_state:
    st.session_state.show_sidebar = False

# ===============================
# NAVBAR
# ===============================
def navbar():
    col1, col2 = st.columns([5,1])
    with col1:
        st.markdown('<div class="nav-title">🍜 Rumah Makan Mas Ragil</div>', unsafe_allow_html=True)
    with col2:
        if st.button("☰", key="toggle_menu", help="Menu", use_container_width=True):
            st.session_state.show_sidebar = not st.session_state.show_sidebar
            st.experimental_rerun()

# ===============================
# LOGIN PAGE
# ===============================
def login_page():
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    st.markdown("<h2>Rumah Makan Mas Ragil</h2>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:14px;color:#c9d6e3;margin-bottom:25px;'>Silakan masuk untuk melanjutkan</p>", unsafe_allow_html=True)

    username = st.text_input("ID Pengguna", placeholder="Masukkan ID Pengguna")
    password = st.text_input("Kata Sandi", type="password", placeholder="Masukkan kata sandi")
    role = st.selectbox("Masuk sebagai", ["User", "Admin"])
    if st.button("Masuk", key="login", use_container_width=True):
        if username.strip() and password.strip():
            st.session_state.is_logged_in = True
            st.session_state.role = role
            st.success(f"Login berhasil sebagai {role}")
            st.rerun()
        else:
            st.error("Harap isi semua kolom login.")

    st.markdown("<p class='forgot'>Lupa password?</p>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ===============================
# MAIN APP
# ===============================
if not st.session_state.is_logged_in:
    login_page()
else:
    navbar()
    if st.session_state.show_sidebar:
        with st.sidebar:
            if st.session_state.role == "Admin":
                st.markdown("## 🧩 Menu Admin")
                menu = st.radio("", ["Pesanan", "Pembayaran", "Laporan", "Kelola Menu", "Logout"], label_visibility="collapsed")

                if menu == "Pesanan":
                    admin_app.run_admin()
                elif menu == "Pembayaran":
                    admin_app.run_admin()
                elif menu == "Laporan":
                    admin_app.run_admin()
                elif menu == "Kelola Menu":
                    admin_app.run_admin()
                elif menu == "Logout":
                    st.session_state.is_logged_in = False
                    st.session_state.show_sidebar = False
                    st.rerun()

            elif st.session_state.role == "User":
                st.markdown("## 👤 Menu User")
                menu = st.radio("", ["Beranda", "Tentang", "Menu", "Keranjang", "Riwayat", "Logout"], label_visibility="collapsed")

                if menu in ["Beranda", "Tentang", "Menu", "Keranjang", "Riwayat"]:
                    user_app.run_user()
                elif menu == "Logout":
                    st.session_state.is_logged_in = False
                    st.session_state.show_sidebar = False
                    st.rerun()
