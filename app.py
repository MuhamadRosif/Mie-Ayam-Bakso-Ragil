# ==========================================================
# app.py — Entry Point Utama
# Rumah Makan Mas Ragil 🍜
# ==========================================================
import streamlit as st
from kasir_mas_ragil import admin_app, user_app

# ----------------------------------------------------------
# Konfigurasi halaman
# ----------------------------------------------------------
st.set_page_config(
    page_title="Rumah Makan Mas Ragil",
    page_icon="🍜",
    layout="wide",
)

# ----------------------------------------------------------
# Session Defaults
# ----------------------------------------------------------
defaults = {
    "is_logged_in": False,
    "role": None,        # "Admin" atau "User"
    "username": "",
    "sidebar_open": False,
    "page": "Beranda",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ----------------------------------------------------------
# CSS (Global Theme + Login Box)
# ----------------------------------------------------------
st.markdown("""
<style>
:root {
  --blue-dark: #0b1e3f;
  --blue-mid: #1565c0;
  --white: #ffffff;
  --muted: #cfddeb;
}

/* page background */
.stApp {
  background-color: #f6f8fb;
}

/* top navbar */
.topbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 60px;
  background: var(--blue-dark);
  color: var(--white);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 18px;
  z-index: 999;
  box-shadow: 0 2px 8px rgba(0,0,0,0.25);
}
.topbar .title { font-weight:700; font-size:18px; }
.topbar .hamb {
  background: transparent;
  border: none;
  color: var(--white);
  font-size: 22px;
  cursor: pointer;
  padding: 6px 10px;
  border-radius: 6px;
}
.topbar .hamb:hover { background: rgba(255,255,255,0.06); transform: scale(1.03); }

/* sidebar appearance */
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #0b1e3f, #124b7e);
  color: white;
}

/* login center box */
.login-wrap { 
  display:flex; 
  justify-content:center; 
  align-items:center; 
  min-height:calc(100vh - 60px); 
  padding-top:60px; 
}
.login-box {
  width:420px;
  background:var(--blue-dark);
  color:var(--white);
  padding:28px;
  border-radius:12px;
  box-shadow:0 8px 30px rgba(0,0,0,0.22);
}
.login-box h2 { margin-bottom:6px; }
.login-box .muted { color:var(--muted); margin-bottom:16px; }

/* main content spacing */
.content { padding: 20px; margin-top: 70px; }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------
# Topbar (navbar atas)
# ----------------------------------------------------------
st.markdown("""
<div class="topbar">
  <div class="title">🍜 Rumah Makan Mas Ragil</div>
  <div>
    <button class="hamb" id="hamb-streamlit">☰</button>
  </div>
</div>
""", unsafe_allow_html=True)

# ----------------------------------------------------------
# Sidebar Toggle
# ----------------------------------------------------------
def _toggle_sidebar():
    st.session_state.sidebar_open = not st.session_state.sidebar_open

# Tombol Streamlit tersembunyi (buat ditrigger via JS)
st.button("hidden_toggle_sidebar", on_click=_toggle_sidebar, key="hidden_toggle")

# JS listener buat tombol ☰
st.components.v1.html("""
<script>
document.getElementById('hamb-streamlit').addEventListener('click', function(e){
  e.preventDefault();
  const btns = window.parent.document.querySelectorAll('button');
  btns.forEach(b=>{
    if(b.innerText.includes('hidden_toggle_sidebar')){ b.click(); }
  });
});
</script>
""", height=0)

# ----------------------------------------------------------
# Sidebar Navigasi
# ----------------------------------------------------------
if st.session_state.sidebar_open:
    with st.sidebar:
        st.markdown("### Navigasi")

        if st.session_state.is_logged_in:
            if st.session_state.role == "Admin":
                sel = st.radio(
                    "",
                    ["Dashboard", "Pesanan", "Pembayaran", "Laporan", "Kelola Menu", "Logout"],
                    index=0,
                )
            else:
                sel = st.radio(
                    "",
                    ["Beranda", "Menu Makanan", "Menu Minuman", "Keranjang", "Riwayat", "Tentang", "Logout"],
                    index=0,
                )
            st.session_state.page = sel
        else:
            sel = st.radio("", ["Masuk sebagai User", "Masuk sebagai Admin"], index=0)
            st.session_state.page = "login_user" if sel == "Masuk sebagai User" else "login_admin"

# ----------------------------------------------------------
# Login UI
# ----------------------------------------------------------
def login_ui():
    st.markdown('<div class="login-wrap"><div class="login-box">', unsafe_allow_html=True)
    st.markdown("<h2>Rumah Makan Mas Ragil</h2>", unsafe_allow_html=True)
    st.markdown("<div class='muted'>Silakan masuk untuk melanjutkan</div>", unsafe_allow_html=True)

    username = st.text_input("ID Pengguna", key="login_id")
    password = st.text_input("Kata Sandi", type="password", key="login_pw")
    role = st.selectbox("Sebagai", ["User", "Admin"], key="login_role")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Masuk", key="login_submit"):
            if not username.strip() or not password.strip():
                st.error("Isi ID Pengguna dan Kata Sandi.")
            else:
                if username == "admin" and password == "admin123":
                    st.session_state.is_logged_in = True
                    st.session_state.role = "Admin"
                    st.session_state.username = username
                    st.success("Login berhasil sebagai Admin.")
                    st.rerun()
                else:
                    # User login (registrasi dikelola di user_app)
                    st.session_state.is_logged_in = True
                    st.session_state.role = "User"
                    st.session_state.username = username
                    st.success(f"Login berhasil sebagai {role}.")
                    st.rerun()

    with col2:
        st.markdown("<div style='margin-top:6px;'><a style='color:#ffd97a'>Lupa password?</a></div>", unsafe_allow_html=True)

    st.markdown('</div></div>', unsafe_allow_html=True)

# ----------------------------------------------------------
# Routing Halaman
# ----------------------------------------------------------
st.markdown('<div class="content">', unsafe_allow_html=True)

if not st.session_state.is_logged_in:
    login_ui()
else:
    if st.session_state.role == "Admin":
        admin_app.run_admin(page=st.session_state.page)
    else:
        user_app.run_user(page=st.session_state.page)

st.markdown('</div>', unsafe_allow_html=True)
