# =====================================================
# 🍜 Kasir Mas Ragil — Versi User
# =====================================================
import streamlit as st
import os
import json

# -----------------------
# Konfigurasi Aplikasi
# -----------------------
st.set_page_config(page_title="Kasir Mas Ragil — User", page_icon="🍜", layout="wide")
MENU_FILE = "menu.json"

# -----------------------
# Default Session
# -----------------------
defaults = {
    "menu_open": False,
    "page": "home",
    "pesanan": {},
    "nama_pelanggan": ""
}
for k,v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# -----------------------
# Load Menu
# -----------------------
if os.path.exists(MENU_FILE):
    with open(MENU_FILE,"r",encoding="utf-8") as f:
        data = json.load(f)
        menu_makanan = data.get("makanan",{})
        menu_minuman = data.get("minuman",{})
else:
    menu_makanan = {"Mie Ayam":15000,"Bakso Urat":18000,"Mie Ayam Bakso":20000,"Bakso Telur":19000}
    menu_minuman = {"Es Teh Manis":5000,"Es Jeruk":7000,"Teh Hangat":5000,"Jeruk Hangat":6000}

# -----------------------
# Styling
# -----------------------
st.markdown("""
<style>
.stApp {background: linear-gradient(180deg,#071026,#0b1440); color:#e6eef8;}
.topbar {display:flex; align-items:center; gap:12px; padding:10px 18px; 
         background: linear-gradient(90deg,#b71c1c,#9c2a2a); color:white; 
         border-radius:8px; box-shadow:0 2px 10px rgba(0,0,0,0.3);}
.right-panel {background: linear-gradient(180deg,#0c0e16,#181b26); padding:14px; border-radius:10px;}
.menu-item {display:block; width:100%; padding:10px; border-radius:8px; background:#222; color:white; border:none;}
.menu-item:hover {background:#333;}
.stButton>button {background: linear-gradient(90deg,#c62828,#9c1f1f); color:white; border:none; border-radius:6px; padding:8px 16px;}
.stButton>button:hover {transform:scale(1.05);}
</style>
""", unsafe_allow_html=True)

# -----------------------
# Topbar
# -----------------------
col_tb1, col_tb2 = st.columns([1,10])
with col_tb2:
    st.markdown('<div class="topbar"><div style="font-weight:800">🍜 Mie Ayam & Bakso — Mas Ragil (User)</div></div>', unsafe_allow_html=True)

# -----------------------
# Layout
# -----------------------
if st.session_state.menu_open:
    main_col, side_col = st.columns([7,3])
else:
    main_col = st.columns([1])[0]
    side_col = None

# -----------------------
# Sidebar Navigasi
# -----------------------
if side_col is not None:
    with side_col:
        st.markdown('<div class="right-panel">', unsafe_allow_html=True)
        if st.button("🏠 Beranda"): st.session_state.page="home"
        if st.button("🍜 Pesan Menu"): st.session_state.page="pesan"
        if st.button("🛒 Keranjang"): st.session_state.page="keranjang"
        if st.button("ℹ️ Tentang"): st.session_state.page="tentang"
        st.markdown("<hr>", unsafe_allow_html=True)
        if st.button("♻️ Reset Pesanan"):
            st.session_state.pesanan={}
            st.session_state.nama_pelanggan=""
            st.success("Pesanan direset.")
        st.markdown("<div style='font-size:12px;opacity:0.7;'>© Mas Ragil 2025</div>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# -----------------------
# Halaman Utama
# -----------------------
page = st.session_state.page
with main_col:
    if page=="home":
        st.header("🏠 Selamat Datang di Mie Ayam & Bakso Mas Ragil 🍜")
        st.write("Pilih menu, masukkan jumlah, dan lihat pesanan Anda di Keranjang.")
        st.image("https://via.placeholder.com/800x400/071026/ffffff?text=Mie+Ayam+%26+Bakso+Mas+Ragil", width=800)

    # ------------------- PESAN -------------------
    elif page=="pesan":
        st.header("🍜 Pesan Menu")
        nama = st.text_input("Nama Pelanggan", value=st.session_state.nama_pelanggan)
        st.session_state.nama_pelanggan = nama
        if not nama.strip():
            st.warning("Masukkan nama pelanggan sebelum memesan.")
        else:
            st.subheader("🍽️ Menu Makanan")
            for item,harga in menu_makanan.items():
                col1,col2,col3,col4 = st.columns([3,1,1,2])
                with col1: st.write(f"**{item}** (Rp {harga:,})")
                with col2:
                    if st.button("-", key=f"{item}-minus"): st.session_state.pesanan[item] = max(0, st.session_state.pesanan.get(item,0)-1)
                with col3: st.write(f"Qty: {st.session_state.pesanan.get(item,0)}")
                with col4:
                    if st.button("+", key=f"{item}-plus"): st.session_state.pesanan[item] = st.session_state.pesanan.get(item,0)+1

            st.subheader("🥤 Menu Minuman")
            for item,harga in menu_minuman.items():
                col1,col2,col3,col4 = st.columns([3,1,1,2])
                with col1: st.write(f"**{item}** (Rp {harga:,})")
                with col2:
                    if st.button("-", key=f"{item}-minus-minum"): st.session_state.pesanan[item] = max(0, st.session_state.pesanan.get(item,0)-1)
                with col3: st.write(f"Qty: {st.session_state.pesanan.get(item,0)}")
                with col4:
                    if st.button("+", key=f"{item}-plus-minum"): st.session_state.pesanan[item] = st.session_state.pesanan.get(item,0)+1

    # ------------------- KERANJANG -------------------
    elif page=="keranjang":
        st.header("🛒 Keranjang Pesanan")
        pesanan_aktif = {k:v for k,v in st.session_state.pesanan.items() if v>0}
        if not pesanan_aktif:
            st.info("Keranjang kosong.")
        else:
            total = 0
            for k,v in pesanan_aktif.items():
                harga_satuan = menu_makanan.get(k, menu_minuman.get(k,0))
                subtotal = harga_satuan*v
                total += subtotal
                col1,col2,col3 = st.columns([4,2,2])
                with col1: st.write(f"{k} x {v}")
                with col2: st.write(f"Rp {subtotal:,}")
                with col3:
                    if st.button("❌ Hapus", key=f"hapus-{k}"):
                        del st.session_state.pesanan[k]
                        st.experimental_rerun()
            st.markdown(f"**Total: Rp {total:,}**")

    # ------------------- TENTANG -------------------
    elif page=="tentang":
        st.header("ℹ️ Tentang Aplikasi")
        st.write("Aplikasi Kasir Mie Ayam & Bakso Mas Ragil 🍜")
        st.write("Versi User: Bisa pesan, lihat keranjang, dan reset pesanan.")
        st.write("Dibuat dengan ❤️ oleh Mas Ragil.")

st.markdown("---")
st.caption("© 2025 Mas Ragil — Aplikasi Kasir 🍜 | Versi User")
