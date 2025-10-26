# app.py — entry point (login tetap seperti yang kamu suka; global navbar + sidebar navigation)
import streamlit as st
from kasir_mas_ragil import admin_app, user_app

st.set_page_config(page_title="Rumah Makan Mas Ragil", page_icon="🍜", layout="wide")

# -----------------------
# Session defaults
# -----------------------
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

# -----------------------
# Global CSS (login + theme)
# -----------------------
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

/* sidebar appearance (when used) */
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #0b1e3f, #124b7e);
  color: white;
}

/* login center box (KEEP THIS: your favorite login) */
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

/* content spacing (main area) */
.content { padding: 20px; margin-top: 70px; }
</style>
""", unsafe_allow_html=True)

# -----------------------
# Topbar (visual)
# -----------------------
st.markdown(
    f"""
    <div class="topbar">
      <div class="title">🍜 Rumah Makan Mas Ragil</div>
      <div>
        <form>
          <button class="hamb" id="hamb-streamlit">☰</button>
        </form>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Provide a real Streamlit button as fallback to toggle sidebar (clicking the JS button will also try to press this)
def _toggle_sidebar():
    st.session_state.sidebar_open = not st.session_state.sidebar_open
st.button("hidden-toggle-sidebar", key="hidden_toggle_sidebar", on_click=_toggle_sidebar, help="hidden toggle")

# Small JS to forward the click on the styled button to the hidden Streamlit button
st.components.v1.html("""
<script>
document.getElementById('hamb-streamlit').addEventListener('click', function(e){
    e.preventDefault();
    // Find the hidden Streamlit button and click it
    const btn = window.parent.document.querySelector('button[kind="primary"], button[data-baseweb="button"]');
    // As fallback, trigger click on any Streamlit button with label "hidden-toggle-sidebar"
    // But direct DOM for Streamlit internals is fragile; the hidden streamlit button above will be near top.
    try {
        const hidden = window.parent.document.querySelector('button[title="hidden_toggle_sidebar"], button[aria-label="hidden_toggle_sidebar"], button[role="button"]');
        if(hidden) hidden.click();
    } catch(e){}
    // Also dispatch a window message to be safe
    window.parent.postMessage({type:"TOGGLE_SIDEBAR"}, "*");
});
</script>
""", height=0)

# -----------------------
# Sidebar navigation (when open)
# -----------------------
if st.session_state.sidebar_open:
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

# -----------------------
# Main content area
# -----------------------
st.markdown('<div class="content">', unsafe_allow_html=True)

# -----------------------
# LOGIN UI (kept exactly like you liked)
# -----------------------
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
                # admin special credential
                if username.strip() == "admin" and password.strip() == "admin123":
                    st.session_state.is_logged_in = True
                    st.session_state.role = "Admin"
                    st.session_state.username = username.strip()
                    st.success("Login berhasil sebagai Admin.")
                    st.rerun()
                else:
                    # treat as normal user (user_app will also allow registration if needed)
                    st.session_state.is_logged_in = True
                    st.session_state.role = "User"
                    st.session_state.username = username.strip()
                    st.success(f"Login berhasil sebagai {role}.")
                    st.rerun()
    with col2:
        st.markdown("<div style='margin-top:6px;'><a style='color:#ffd97a'>Lupa password?</a></div>", unsafe_allow_html=True)

    st.markdown('</div></div>', unsafe_allow_html=True)

# -----------------------
# Route: render login or app pages
# -----------------------
if not st.session_state.is_logged_in:
    login_ui()
else:
    # If logged in, forward page rendering to admin/user modules.
    # They expect a `page` argument (string from sidebar navigation); default provided in admin/user code.
    if st.session_state.role == "Admin":
        admin_app.run_admin(page=st.session_state.page)
    else:
        user_app.run_user(page=st.session_state.page)

st.markdown('</div>', unsafe_allow_html=True)
