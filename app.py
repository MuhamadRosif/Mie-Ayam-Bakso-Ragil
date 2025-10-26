# app.py — entry point (login + navbar + toggle sidebar)
import streamlit as st
from kasir_mas_ragil import admin_app, user_app

st.set_page_config(page_title="Rumah Makan Mas Ragil", page_icon="🍜", layout="wide")

# --------------------
# Session defaults
# --------------------
if "is_logged_in" not in st.session_state:
    st.session_state.is_logged_in = False
if "role" not in st.session_state:
    st.session_state.role = None  # "Admin" or "User"
if "username" not in st.session_state:
    st.session_state.username = ""
if "sidebar_open" not in st.session_state:
    st.session_state.sidebar_open = False
if "page" not in st.session_state:
    st.session_state.page = "Beranda"

# --------------------
# Global CSS (theme)
# --------------------
st.markdown("""
<style>
:root{
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
.topbar button { background:transparent; border:none; color:var(--white); font-size:22px; cursor:pointer; }

/* sidebar style (Streamlit sidebar) */
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #0b1e3f, #124b7e);
  color: white;
}

/* login center box */
.login-wrap { display:flex; justify-content:center; align-items:center; min-height:calc(100vh - 60px); padding-top:60px; }
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

/* content spacing */
.content { padding: 20px; margin-top: 70px; }
</style>
""", unsafe_allow_html=True)

# --------------------
# Navbar (always)
# --------------------
st.markdown('<div class="topbar"><div class="title">🍜 Rumah Makan Mas Ragil</div><div><button id="hamburger">☰</button></div></div>', unsafe_allow_html=True)

# simple JS to call Streamlit button by id (toggle)
st.markdown("""
<script>
const btn = document.getElementById('hamburger');
btn.onclick = () => {
    // post message to parent; Streamlit will not receive custom events reliably,
    // so we simulate by clicking a hidden Streamlit button below via setting window.location hash.
    // Instead, we trigger a window.postMessage that we will catch via a tiny HTML component.
    window.parent.postMessage({type: 'TOGGLE_SIDEBAR'}, '*');
};
</script>
""", unsafe_allow_html=True)

# a tiny component listening for the message and clicking a hidden button
import streamlit.components.v1 as components
components.html("""
<script>
window.addEventListener('message', (e) => {
  if (e.data && e.data.type === 'TOGGLE_SIDEBAR') {
    const btn = window.parent.document.querySelector('button[data-toggle="hidden-sidebar-button"]');
    if(btn) btn.click();
  }
});
</script>
""", height=0)

# hidden Streamlit button to toggle sidebar in Python
def _toggle_sidebar():
    st.session_state.sidebar_open = not st.session_state.sidebar_open

st.button("toggle-sidebar-hidden", key="hidden_sidebar_btn", on_click=_toggle_sidebar, args=None, kwargs=None)
# mark attribute so JS can find it (data-toggle). Streamlit doesn't allow setting attributes directly;
# We used query selector based on data-toggle attribute, but Streamlit doesn't set custom attr.
# The HTML above uses querySelector('button[data-toggle="hidden-sidebar-button"]') but Streamlit won't set.
# To ensure toggle works across environments, also provide a visible toggle via top-right Streamlit button:
# (we'll also show a small clickable element)
col1, col2 = st.columns([9,1])
with col2:
    if st.button("☰", key="hamburger_fallback"):
        st.session_state.sidebar_open = not st.session_state.sidebar_open

# --------------------
# Show/hide sidebar content (only when sidebar_open True)
# --------------------
if st.session_state.sidebar_open:
    # Sidebar navigation only (no page content inside)
    with st.sidebar:
        st.markdown("### Navigasi")
        if st.session_state.is_logged_in and st.session_state.role == "Admin":
            sel = st.radio("", ["Dashboard", "Pesanan", "Pembayaran", "Laporan", "Kelola Menu", "Logout"], index=0)
            st.session_state.page = sel
        elif st.session_state.is_logged_in and st.session_state.role == "User":
            sel = st.radio("", ["Beranda", "Menu Makanan", "Menu Minuman", "Keranjang", "Riwayat", "Tentang", "Logout"], index=0)
            st.session_state.page = sel
        else:
            sel = st.radio("", ["Masuk sebagai User", "Masuk sebagai Admin"], index=0)
            if sel == "Masuk sebagai User":
                st.session_state.page = "login_user"
            else:
                st.session_state.page = "login_admin"

# --------------------
# Main content area
# --------------------
st.markdown('<div class="content">', unsafe_allow_html=True)

# LOGIN UI (keep as you already like)
def login_ui():
    st.markdown('<div class="login-wrap">', unsafe_allow_html=True)
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    st.markdown("<h2>Rumah Makan Mas Ragil</h2>", unsafe_allow_html=True)
    st.markdown("<div class='muted'>Silakan masuk untuk melanjutkan</div>", unsafe_allow_html=True)

    username = st.text_input("ID Pengguna", key="login_id")
    password = st.text_input("Kata Sandi", type="password", key="login_pw")
    role = st.selectbox("Sebagai", ["User", "Admin"], key="login_role")

    col1, col2 = st.columns([1,1])
    with col1:
        if st.button("Masuk", key="login_submit"):
            if username.strip() == "" or password.strip() == "":
                st.error("Isi ID Pengguna dan Kata Sandi.")
            else:
                # if admin credentials, prefer admin role
                if username.strip() == "admin" and password.strip() == "admin123":
                    st.session_state.is_logged_in = True
                    st.session_state.role = "Admin"
                    st.session_state.username = username.strip()
                    st.success("Login berhasil sebagai Admin.")
                else:
                    # normal user — we'll check users.json in user_app
                    st.session_state.is_logged_in = True
                    st.session_state.role = role
                    st.session_state.username = username.strip()
                    st.success(f"Login berhasil sebagai {role}.")
                st.experimental_rerun()
    with col2:
        st.markdown("<div style='margin-top:6px;'><a style='color:#ffd97a'>Lupa password?</a></div>", unsafe_allow_html=True)

    st.markdown('</div></div>', unsafe_allow_html=True)

# route
if not st.session_state.is_logged_in:
    login_ui()
else:
    # route to admin or user modules, they expect st.session_state.page to be set by sidebar nav
    if st.session_state.role == "Admin":
        # admin_app expects to render content in main area
        admin_app.run_admin(page=st.session_state.page)
    else:
        user_app.run_user(page=st.session_state.page)

st.markdown('</div>', unsafe_allow_html=True)
