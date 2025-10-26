import streamlit as st
from kasir_mas_ragil import admin_app, user_app

# ===============================
# Konfigurasi halaman
# ===============================
st.set_page_config(page_title="Kasir Mas Ragil 🍜", page_icon="🍜", layout="wide")

# ===============================
# Session defaults
# ===============================
if "role" not in st.session_state:
    st.session_state.role = None  # "admin" atau "user"
if "sidebar_open" not in st.session_state:
    st.session_state.sidebar_open = False
if "page" not in st.session_state:
    st.session_state.page = "home"

# ===============================
# Gaya CSS (navbar + sidebar)
# ===============================
st.markdown("""
<style>
/* Navbar */
.navbar {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 60px;
    background-color: #b30000;
    color: white;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 20px;
    z-index: 100;
    font-family: 'Poppins', sans-serif;
    box-shadow: 0 2px 8px rgba(0,0,0,0.2);
}
.navbar-title {
    font-size: 22px;
    font-weight: bold;
}
.hamburger {
    font-size: 28px;
    cursor: pointer;
    transition: 0.3s;
}
.hamburger:hover {transform: scale(1.2);}

/* Sidebar */
.sidebar-panel {
    position: fixed;
    top: 0;
    right: -300px;
    width: 280px;
    height: 100%;
    background-color: white;
    box-shadow: -2px 0 10px rgba(0,0,0,0.2);
    padding: 20px;
    transition: right 0.4s ease;
    z-index: 200;
    display: flex;
    flex-direction: column;
    font-family: 'Poppins', sans-serif;
}
.sidebar-panel.open {
    right: 0;
}
.sidebar-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 2px solid #f1f1f1;
    padding-bottom: 10px;
}
.sidebar-header h3 {
    color: #b30000;
    margin: 0;
}
.sidebar-menu {
    margin-top: 20px;
}
.sidebar-menu button {
    background: none;
    border: none;
    width: 100%;
    text-align: left;
    font-size: 16px;
    padding: 12px 5px;
    color: #333;
    cursor: pointer;
    border-radius: 8px;
    transition: background 0.3s;
}
.sidebar-menu button:hover {
    background-color: #f8f8f8;
    color: #b30000;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# ===============================
# Navbar HTML
# ===============================
st.markdown(f"""
<div class="navbar">
    <div class="navbar-title">🍜 Kasir Mas Ragil</div>
    <div class="hamburger" onclick="toggleSidebar()">☰</div>
</div>

<div id="sidebar" class="sidebar-panel">
    <div class="sidebar-header">
        <h3>Menu</h3>
        <div style="font-size:22px;cursor:pointer;" onclick="toggleSidebar()">✕</div>
    </div>
    <div class="sidebar-menu">
""", unsafe_allow_html=True)

# ===============================
# Sidebar Menu (Dinamis)
# ===============================
if st.session_state.role == "admin":
    menu_list = {
        "📦 Pesanan": "pesanan",
        "💳 Pembayaran": "pembayaran",
        "📊 Laporan": "laporan",
        "🍴 Kelola Menu": "kelola_menu",
        "🚪 Logout": "logout"
    }
elif st.session_state.role == "user":
    menu_list = {
        "🏠 Beranda": "home",
        "🍜 Menu Makanan & Minuman": "menu",
        "🛒 Keranjang": "keranjang",
        "🧾 Riwayat": "riwayat",
        "ℹ️ Tentang": "tentang",
        "🚪 Logout": "logout"
    }
else:
    menu_list = {
        "👤 Login sebagai User": "login_user",
        "🧑‍💼 Login sebagai Admin": "login_admin"
    }

# Render tombol sidebar
for name, value in menu_list.items():
    st.markdown(f"""
    <button onclick="fetch('/?_page={value}', {{method:'POST'}})">{name}</button>
    """, unsafe_allow_html=True)

st.markdown("</div></div>", unsafe_allow_html=True)

# ===============================
# Javascript Toggle Sidebar
# ===============================
st.markdown("""
<script>
function toggleSidebar(){
    var sb = document.getElementById("sidebar");
    if(sb.classList.contains("open")){
        sb.classList.remove("open");
    } else {
        sb.classList.add("open");
    }
}
</script>
""", unsafe_allow_html=True)

# ===============================
# Konten Utama
# ===============================
st.markdown("<div style='margin-top:70px;'></div>", unsafe_allow_html=True)

if st.session_state.page == "home":
    st.title("Selamat Datang di 🍜 Kasir Mas Ragil")
    st.write("Pilih menu di kanan atas untuk mulai.")
elif st.session_state.page == "login_user":
    user_app.run_user()
elif st.session_state.page == "login_admin":
    admin_app.run_admin()
else:
    st.write(f"📄 Halaman: {st.session_state.page}")

