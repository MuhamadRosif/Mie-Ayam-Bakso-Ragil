import streamlit as st
from streamlit_extras.switch_page_button import switch_page

# ========== KONFIGURASI DASAR ==========
st.set_page_config(page_title="Mie Ayam & Bakso — Mas Ragil", layout="wide")

# ========== CSS STYLING ==========
st.markdown("""
<style>
/* ====== NAVBAR ====== */
.navbar {
    background-color: #b71c1c;
    color: white;
    padding: 14px;
    border-radius: 12px;
    font-weight: bold;
    font-size: 18px;
    display: flex;
    align-items: center;
    justify-content: flex-start;
    gap: 10px;
}

/* ====== PANEL PUTIH SLIDE ====== */
.side-panel {
    position: fixed;
    top: 0;
    right: -80%;
    width: 70%;
    height: 100%;
    background: rgba(255, 255, 255, 0.97);
    backdrop-filter: blur(8px);
    box-shadow: -3px 0 12px rgba(0,0,0,0.2);
    z-index: 999;
    transition: right 0.3s ease;
    padding: 20px;
}
.side-panel.open {
    right: 0;
}

/* Overlay (klik luar menutup) */
.overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0,0,0,0.4);
    z-index: 998;
    display: none;
    transition: 0.3s;
}
.overlay.show {
    display: block;
}

/* ====== TOMBOL MENU ====== */
.menu-item {
    display: block;
    width: 100%;
    text-align: left;
    border: none;
    padding: 14px 18px;
    border-radius: 10px;
    margin: 6px 0;
    background: #f5f5f5;
    color: #b71c1c;
    font-weight: 600;
    font-size: 16px;
    cursor: pointer;
    transition: 0.2s;
}
.menu-item:hover {
    background: #ffe5e5;
}
.menu-item.active {
    background: #ffcccc;
    color: #7f0000;
}

/* ====== ANIMASI MASUK KONTEN ====== */
.fadein {
    animation: fadeIn 0.6s ease;
}
@keyframes fadeIn {
  from {opacity: 0; transform: translateY(10px);}
  to {opacity: 1; transform: translateY(0);}
}

/* ====== DARK MODE OTOMATIS ====== */
@media (prefers-color-scheme: dark) {
    body, .stApp {
        background-color: #0e0e0e !important;
        color: white !important;
    }
    .side-panel {
        background: rgba(32,32,32,0.95);
        color: white;
    }
    .menu-item {
        background: #1f1f1f;
        color: #ffecec;
    }
    .menu-item:hover {
        background: #333;
    }
    .menu-item.active {
        background: #800000;
        color: white;
    }
}
</style>
""", unsafe_allow_html=True)

# ========== STATE ==========
if "menu_open" not in st.session_state:
    st.session_state.menu_open = False
if "page" not in st.session_state:
    st.session_state.page = "home"

# ========== NAVBAR ==========
st.markdown("""
<div class="navbar">
    <button onclick="togglePanel()" style="background:none;border:none;color:white;font-size:20px;cursor:pointer;">☰</button>
    🍜 Mie Ayam & Bakso — Mas Ragil
</div>
""", unsafe_allow_html=True)

# ========== PANEL & OVERLAY ==========
panel_open = "open" if st.session_state.menu_open else ""
st.markdown(f"""
<div id="overlay" class="overlay" onclick="closePanel()"></div>
<div id="panel" class="side-panel {panel_open}">
  <button class="menu-item {'active' if st.session_state.page=='home' else ''}" onclick="window.location.href='?page=home'">🏠 Beranda</button>
  <button class="menu-item {'active' if st.session_state.page=='pesan' else ''}" onclick="window.location.href='?page=pesan'">🍜 Pesan Menu</button>
  <button class="menu-item {'active' if st.session_state.page=='bayar' else ''}" onclick="window.location.href='?page=bayar'">💳 Pembayaran</button>
  <button class="menu-item {'active' if st.session_state.page=='struk' else ''}" onclick="window.location.href='?page=struk'">📄 Struk</button>
  <button class="menu-item {'active' if st.session_state.page=='tentang' else ''}" onclick="window.location.href='?page=tentang'">ℹ️ Tentang</button>
</div>

<script>
function togglePanel() {{
  const panel = document.getElementById('panel');
  const overlay = document.getElementById('overlay');
  if (panel.classList.contains('open')) {{
    panel.classList.remove('open');
    overlay.classList.remove('show');
  }} else {{
    panel.classList.add('open');
    overlay.classList.add('show');
  }}
}}
function closePanel() {{
  document.getElementById('panel').classList.remove('open');
  document.getElementById('overlay').classList.remove('show');
}}
</script>
""", unsafe_allow_html=True)

# ========== HANDLE PAGE PARAMETER ==========
query_params = st.query_params
if "page" in query_params:
    st.session_state.page = query_params["page"][0]

# ========== ISI HALAMAN ==========
page = st.session_state.page

if page == "home":
    st.markdown("""
    <div class="fadein">
        <h2>Selamat Datang di Mie Ayam & Bakso Mas Ragil 🍜</h2>
        <p>Warung rumahan dengan cita rasa otentik. Pilih menu, hitung total, lalu bayar dan cetak struk.</p>
    </div>
    """, unsafe_allow_html=True)

elif page == "pesan":
    st.markdown("""
    <div class="fadein">
        <h2>🍜 Pesan Menu</h2>
        <p>Silakan pilih menu yang ingin dipesan.</p>
    </div>
    """, unsafe_allow_html=True)

elif page == "bayar":
    st.markdown("""
    <div class="fadein">
        <h2>💳 Pembayaran</h2>
        <p>Silakan hitung total di menu Pesan terlebih dahulu.</p>
    </div>
    """, unsafe_allow_html=True)

elif page == "struk":
    st.markdown("""
    <div class="fadein">
        <h2>📄 Struk</h2>
        <p>Struk pembelian Anda akan muncul di sini.</p>
    </div>
    """, unsafe_allow_html=True)

elif page == "tentang":
    st.markdown("""
    <div class="fadein">
        <h2>ℹ️ Tentang</h2>
        <p>Aplikasi pemesanan Mie Ayam & Bakso — dibuat oleh Mas Ragil menggunakan Streamlit.</p>
    </div>
    """, unsafe_allow_html=True)
