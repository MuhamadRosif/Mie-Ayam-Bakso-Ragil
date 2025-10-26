# =====================================================
# app.py — Kasir Mas Ragil (FINAL: Navbar Merah Elegan Global)
# =====================================================
import streamlit as st
from kasir_mas_ragil import admin_app, user_app

# ------------------------------------------------------
# Konfigurasi Halaman
# ------------------------------------------------------
st.set_page_config(page_title="Kasir Mas Ragil", page_icon="🍜", layout="wide")

# ------------------------------------------------------
# CSS: Navbar Merah Elegan
# ------------------------------------------------------
st.markdown("""
<style>
/* ======== NAVBAR ======== */
.navbar {
    position: fixed;
    top: 0;
    width: 100%;
    background-color: #b30000; /* merah elegan */
    color: white;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 14px 30px;
    z-index: 9999;
    transition: top 0.4s ease;
    font-family: 'Poppins', sans-serif;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.4);
}

/* Logo kiri */
.logo {
    font-weight: 700;
    font-size: 20px;
    display: flex;
    align-items: center;
}
.logo .dot {
    height: 12px;
    width: 12px;
    background-color: #ff4d4d;
    border-radius: 50%;
    display: inline-block;
    margin-right: 8px;
}

/* Tombol toggle (hamburger kanan) */
.toggle {
    cursor: pointer;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    height: 18px;
}
.toggle div {
    width: 25px;
    height: 3px;
    background-color: white;
    border-radius: 2px;
    transition: 0.3s;
}

/* Dropdown menu */
.menu {
    position: fixed;
    top: 56px;
    right: 20px;
    background-color: #800000; /* merah gelap */
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 8px 20px rgba(0,0,0,0.3);
    display: none;
    flex-direction: column;
}
.menu.show {
    display: flex;
    animation: fadeIn 0.3s ease;
}
.menu button {
    background: none;
    border: none;
    color: white;
    padding: 12px 18px;
    text-align: left;
    font-size: 15px;
    cursor: pointer;
}
.menu button:hover {
    background-color: #b30000;
}

/* Animasi */
@keyframes fadeIn {
    from {opacity: 0; transform: translateY(-5px);}
    to {opacity: 1; transform: translateY(0);}
}

/* Hilang saat scroll */
.hidden {
    top: -70px;
}
</style>

<script>
let lastScrollTop = 0;
window.addEventListener("scroll", function(){
    let navbar = document.querySelector(".navbar");
    let st = window.pageYOffset || document.documentElement.scrollTop;
    if(st > lastScrollTop){
        navbar.classList.add("hidden");
    } else {
        navbar.classList.remove("hidden");
    }
    lastScrollTop = st <= 0 ? 0 : st;
}, false);
</script>
""", unsafe_allow_html=True)

# ------------------------------------------------------
# Session defaults
# ------------------------------------------------------
if "role" not in st.session_state:
    st.session_state.role = None  # "user", "admin"
if "menu_open" not in st.session_state:
    st.session_state.menu_open = False
if "page" not in st.session_state:
    st.session_state.page = "Beranda"

# ------------------------------------------------------
# Navbar HTML
# ------------------------------------------------------
st.markdown(f"""
<div class="navbar">
  <div class="logo"><span class="dot"></span>Kasir Mas Ragil</div>
  <div class="toggle" onclick="toggleMenu()">
    <div></div><div></div><div></div>
  </div>
</div>

<div id="menu" class="menu">
""", unsafe_allow_html=True)

# ------------------------------------------------------
# Isi menu berdasarkan role
# ------------------------------------------------------
menu_items = []
if st.session_state.role == "admin":
    menu_items = ["Pesanan", "Pembayaran", "Laporan", "Kelola Menu", "Logout"]
elif st.session_state.role == "user":
    menu_items = ["Beranda", "Menu", "Keranjang", "Riwayat", "Tentang", "Logout"]
else:
    menu_items = ["Masuk sebagai User", "Masuk sebagai Admin"]

for item in menu_items:
    st.markdown(f'<button onclick="menuClicked(\'{item}\')">{item}</button>', unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------------------
# JavaScript toggle dan klik menu
# ------------------------------------------------------
st.markdown("""
<script>
function toggleMenu(){
    let menu = document.getElementById("menu");
    menu.classList.toggle("show");
}

function menuClicked(item){
    window.parent.postMessage({type: 'menuClick', value: item}, '*');
    let menu = document.getElementById("menu");
    menu.classList.remove("show");
}
</script>
""", unsafe_allow_html=True)

# ------------------------------------------------------
# Handle klik menu dari JS
# ------------------------------------------------------
import streamlit.components.v1 as components
components.html("""
<script>
window.addEventListener('message', (event) => {
    if (event.data.type === 'menuClick') {
        window.parent.postMessage(event.data, '*');
    }
});
</script>
""", height=0)

# ------------------------------------------------------
# Spacer untuk navbar fixed
# ------------------------------------------------------
st.markdown("<br><br><br><br>", unsafe_allow_html=True)

# ------------------------------------------------------
# Navigasi antar halaman
# ------------------------------------------------------
if st.session_state.role == "admin":
    admin_app.run_admin()

elif st.session_state.role == "user":
    user_app.run_user()

else:
    st.title("🍜 Kasir Mas Ragil")
    st.markdown("### Selamat datang di sistem kasir modern berbasis Streamlit!")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("👤 Masuk sebagai User"):
            st.session_state.role = "user"
            st.rerun()
    with col2:
        if st.button("🧰 Masuk sebagai Admin"):
            st.session_state.role = "admin"
            st.rerun()
