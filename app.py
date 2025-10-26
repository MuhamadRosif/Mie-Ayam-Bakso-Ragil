# app.py — Rumah Makan Mas Ragil (final: login + navbar + Oishi-style sidebar)
import streamlit as st
from kasir_mas_ragil import admin_app, user_app
from datetime import datetime

# -------------------------
# Page config
# -------------------------
st.set_page_config(page_title="Rumah Makan Mas Ragil", page_icon="🍜", layout="wide")

# -------------------------
# Session defaults
# -------------------------
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

# -------------------------
# CSS (blue theme, login + navbar + sidebar)
# -------------------------
st.markdown(
    """
    <style>
    :root{
      --blue-dark: #0b1e3f;
      --blue-mid: #1565c0;
      --blue-light: #1976d2;
      --white: #ffffff;
      --muted: #cfddeb;
    }
    /* body background */
    .stApp {
      background-color: #f6f8fb;
    }

    /* NAVBAR */
    .top-navbar {
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
      box-shadow: 0 2px 8px rgba(6,20,39,0.25);
      transition: top 0.35s ease;
    }
    .nav-left {
      display:flex;
      align-items:center;
      gap:10px;
      font-family: 'Poppins', sans-serif;
    }
    .nav-title {
      font-weight:700;
      font-size:18px;
      color: var(--white);
    }
    .nav-right {
      display:flex;
      align-items:center;
    }
    .hamburger-btn {
      background: transparent;
      border: none;
      color: var(--white);
      font-size: 24px;
      cursor: pointer;
      padding: 6px 10px;
      border-radius: 6px;
    }
    .hamburger-btn:hover { background: rgba(255,255,255,0.06); transform: scale(1.03); }

    /* SIDEBAR (slide from right) */
    .sidebar {
      position: fixed;
      top: 0;
      right: -380px; /* hidden by default */
      width: 360px;
      height: 100%;
      background: linear-gradient(180deg, var(--blue-dark) 0%, var(--blue-light) 100%);
      color: var(--white);
      box-shadow: -6px 0 24px rgba(6,20,39,0.4);
      padding: 20px;
      transition: right 0.45s cubic-bezier(.2,.9,.2,1);
      z-index: 998;
      overflow-y: auto;
      font-family: 'Poppins', sans-serif;
    }
    .sidebar.open { right: 0; }

    .sidebar .header {
      display:flex;
      justify-content:space-between;
      align-items:center;
      margin-bottom: 14px;
    }
    .sidebar .header h3 { margin:0; color:var(--white); }
    .sidebar .menu-block {
      margin-top: 8px;
      background: rgba(255,255,255,0.03);
      border-radius: 8px;
      overflow: hidden;
    }
    .sidebar .menu-item {
      display:flex;
      align-items:center;
      padding: 18px 16px;
      border-bottom: 1px dashed rgba(255,255,255,0.12);
      cursor: pointer;
      color: var(--white);
      font-size: 15px;
    }
    .sidebar .menu-item:last-child { border-bottom:none; }
    .sidebar .menu-item:hover {
      background: rgba(255,255,255,0.06);
      color: #fff;
      font-weight:600;
    }
    .sidebar .menu-sub {
      padding-left: 24px;
      font-size: 14px;
      color: rgba(255,255,255,0.85);
    }

    /* LOGIN BOX (centered) */
    .login-wrap {
      display:flex;
      justify-content:center;
      align-items:center;
      min-height:calc(100vh - 60px);
      padding-top:60px;
      padding-bottom:40px;
    }
    .login-box {
      width: 420px;
      background: var(--blue-dark);
      border-radius: 12px;
      padding: 28px;
      box-shadow: 0 8px 30px rgba(6,20,39,0.22);
      color: var(--white);
      border: 1px solid rgba(255,255,255,0.04);
      font-family: 'Poppins', sans-serif;
    }
    .login-box h2 { margin:6px 0 6px 0; }
    .login-box .muted { color: var(--muted); margin-bottom: 14px; }

    /* streamlit form element tweaks */
    .stTextInput>div>div>input, .stTextInput>div>div>textarea {
      border-radius:8px !important;
      padding:10px !important;
      border: none !important;
    }
    .stSelectbox>div>div>div>select {
      border-radius:8px !important;
      padding:8px !important;
    }

    .login-actions {
      display:flex;
      gap:12px;
      margin-top:14px;
      align-items:center;
    }
    .btn-primary {
      background: linear-gradient(180deg,var(--blue-mid),var(--blue-light));
      color: #fff;
      border-radius:8px;
      padding:10px 14px;
      border:none;
      font-weight:600;
    }
    .btn-primary:hover { opacity:0.95; cursor:pointer; }

    .forgot {
      margin-top:10px;
      color: #ffd97a; /* soft yellow */
      font-size:13px;
      text-decoration: underline;
      cursor:pointer;
    }

    /* content container spacing when sidebar open */
    .content {
      padding: 20px;
      margin-top: 70px;
      transition: filter 0.3s ease;
    }
    .content.dim { filter: blur(2px) brightness(0.95); }

    /* small screens */
    @media (max-width: 600px) {
      .login-box { width: 92%; padding: 20px; }
      .sidebar { width: 92%; right: -100%; }
      .sidebar.open { right: 0; width: 92%; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------
# Helper: render navbar with Streamlit elements (top fixed)
# -------------------------
def render_navbar():
    # use columns to lay out navbar so hamburger is a real Streamlit button
    left_col, mid_col, right_col = st.columns([2, 8, 1], gap="small")
    with left_col:
        st.markdown(
            f"""<div style="padding-top:8px;"><span style='font-weight:700;color:#fff;font-family:Poppins, sans-serif'>🍜 Rumah Makan Mas Ragil</span></div>""",
            unsafe_allow_html=True,
        )
    with mid_col:
        st.write("")  # spacer
    with right_col:
        # hamburger toggles sidebar
        if st.button("☰", key="hamburger"):
            st.session_state.sidebar_open = not st.session_state.sidebar_open

# -------------------------
# Helper: render sidebar HTML (class open depends on session_state)
# -------------------------
def render_sidebar():
    open_class = "open" if st.session_state.sidebar_open else ""
    # build menu list according to role
    if st.session_state.is_logged_in and st.session_state.role == "Admin":
        menu = [
            ("📦 Pesanan", "pesanan"),
            ("💳 Pembayaran", "pembayaran"),
            ("📊 Laporan", "laporan"),
            ("🍴 Kelola Menu", "kelola_menu"),
            ("🚪 Logout", "logout"),
        ]
    elif st.session_state.is_logged_in and st.session_state.role == "User":
        menu = [
            ("🏠 Beranda", "beranda"),
            ("📋 Menu Makanan", "menu"),
            ("🛒 Keranjang", "keranjang"),
            ("🧾 Riwayat", "riwayat"),
            ("ℹ️ Tentang", "tentang"),
            ("🚪 Logout", "logout"),
        ]
    else:
        menu = [
            ("👤 Login sebagai User", "login_user"),
            ("🧑‍💼 Login sebagai Admin", "login_admin"),
        ]

    # Sidebar HTML wrapper
    st.markdown(
        f"""
        <div class="sidebar {open_class}" id="sidebar_panel">
            <div class="header">
                <h3>Navigasi</h3>
                <div style="cursor:pointer;font-weight:700;" onclick="document.getElementById('close_sidebar_btn').click();">✕</div>
            </div>
            <div class="menu-block">
        """,
        unsafe_allow_html=True,
    )

    # Render each menu item as a Streamlit button (so clicks handled in Python)
    for label, key in menu:
        # use st.button with unique key so it shows and is clickable
        clicked = st.button(label, key=f"menu_{key}")
        if clicked:
            # handle actions
            if key == "logout":
                st.session_state.is_logged_in = False
                st.session_state.role = None
                st.session_state.username = ""
                st.session_state.page = "Beranda"
                st.session_state.sidebar_open = False
                st.success("Logout berhasil.")
                st.experimental_rerun()
            elif key == "login_user":
                st.session_state.sidebar_open = False
                st.session_state.is_logged_in = False
                st.session_state.role = None
                st.session_state.page = "login"
                st.experimental_rerun()
            elif key == "login_admin":
                st.session_state.sidebar_open = False
                st.session_state.page = "login"
                st.experimental_rerun()
            else:
                # set page and close sidebar
                st.session_state.page = key
                st.session_state.sidebar_open = False
                st.experimental_rerun()

    # close wrapper
    st.markdown("</div></div>", unsafe_allow_html=True)

    # hidden Streamlit button used by the close "✕" (JS triggers click on this)
    st.markdown(
        """<script>
        // make the close x call the hidden Streamlit button
        function closeSidebar() {
            const btn = document.getElementById('close_sidebar_btn');
            if(btn) btn.click();
        }
        </script>""",
        unsafe_allow_html=True,
    )
    # create the hidden button
    st.button("close", key="close_sidebar_btn", help="hidden button to close sidebar", on_click=lambda: st.session_state.update({"sidebar_open": False}))

# -------------------------
# LOGIN UI
# -------------------------
def login_ui():
    st.markdown('<div class="login-wrap">', unsafe_allow_html=True)
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    st.markdown("<h2>Rumah Makan Mas Ragil</h2>", unsafe_allow_html=True)
    st.markdown("<div class='muted'>Silakan masuk untuk melanjutkan</div>", unsafe_allow_html=True)

    username = st.text_input("ID Pengguna", key="login_id")
    password = st.text_input("Kata Sandi", type="password", key="login_pw")
    role = st.selectbox("Sebagai", ["User", "Admin"], key="login_role")

    cols = st.columns([1,1])
    with cols[0]:
        if st.button("Masuk", key="login_submit"):
            # NOTE: this is a placeholder check; you can replace with real auth
            if username.strip() == "" or password.strip() == "":
                st.error("Isi ID Pengguna dan Kata Sandi.")
            else:
                st.session_state.is_logged_in = True
                st.session_state.role = role
                st.session_state.username = username
                st.success(f"Login berhasil sebagai {role} — {username}")
                st.experimental_rerun()
    with cols[1]:
        st.markdown("<div style='margin-top:6px;'><a class='forgot'>Lupa password?</a></div>", unsafe_allow_html=True)

    st.markdown("</div></div>", unsafe_allow_html=True)

# -------------------------
# MAIN RENDER
# -------------------------
# Render navbar always (top)
st.markdown('<div class="top-navbar" id="topnav"></div>', unsafe_allow_html=True)
# We use column approach to show visible navbar contents & interactive hamburger button:
with st.container():
    # Use an empty container to place the navbar elements (they visually sit on top via CSS)
    render_navbar()

# Render sidebar (HTML + Streamlit buttons) — placed near top so overlay works
render_sidebar()

# Dim content when sidebar open
content_class = "content dim" if st.session_state.sidebar_open else "content"

st.markdown(f'<div class="{content_class}">', unsafe_allow_html=True)

# Page routing / content
if not st.session_state.is_logged_in:
    # show login page centered
    login_ui()
else:
    # If logged in, route to pages or to apps
    # Provide some quick header and route pages
    if st.session_state.role == "Admin":
        # admin main app handles its own sidebar etc (we kept original run_admin)
        admin_app.run_admin()
    else:
        # user
        user_app.run_user()

st.markdown("</div>", unsafe_allow_html=True)

# -------------------------
# Optional: auto close sidebar on resize small screens (JS)
# -------------------------
st.markdown(
    """
    <script>
    (function(){
        window.addEventListener('resize', function(){
            // close sidebar on small screens to avoid overflow
            if(window.innerWidth < 600){
                try{ document.getElementById('close_sidebar_btn').click(); }catch(e){}
            }
        });
    })();
    </script>
    """,
    unsafe_allow_html=True,
)
