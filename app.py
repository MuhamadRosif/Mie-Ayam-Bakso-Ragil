# ==============================
# Kasir Mas Ragil 🍜 — Versi Final
# ==============================
import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime

# -----------------------
# Config
# -----------------------
st.set_page_config(page_title="Kasir Mas Ragil", page_icon="🍜", layout="wide")
DATA_FILE = "riwayat_penjualan.csv"

# -----------------------
# Admin Login (Dark Centered)
# -----------------------
if "login" not in st.session_state:
    st.session_state.login = False

ADMIN_USER = "admin"
ADMIN_PASS = "1234"

if not st.session_state.login:
    st.markdown("""
    <style>
    body {background-color: #0e0e0e;}
    .stApp {background-color: #0e0e0e;}
    .login-container {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100vh;
    }
    .login-card {
        background-color: #1b1b1b;
        padding: 40px;
        border-radius: 12px;
        width: 360px;
        color: #fff;
        text-align: center;
        font-family: "Segoe UI", sans-serif;
        box-shadow: 0 4px 20px rgba(0,0,0,0.4);
    }
    .login-title {
        font-size: 22px;
        font-weight: bold;
        margin-bottom: 20px;
    }
    .stTextInput>div>div>input {
        background-color: #2b2b2b;
        color: #fff;
        border: 1px solid #444;
        border-radius: 6px;
        padding: 10px;
    }
    .stButton>button {
        background-color: #c62828;
        color: white;
        font-weight: bold;
        border: none;
        border-radius: 6px;
        padding: 10px 20px;
        width: 100px;
        margin-top: 10px;
    }
    .stButton>button:hover {
        background-color: #9c1f1f;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="login-container"><div class="login-card">', unsafe_allow_html=True)
    st.markdown('<div class="login-title">🔐 Login Admin — Kasir Mas Ragil</div>', unsafe_allow_html=True)
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Masuk"):
        if username == ADMIN_USER and password == ADMIN_PASS:
            st.session_state.login = True
            st.experimental_rerun()
        else:
            st.error("Username atau password salah.")
    st.markdown('</div></div>', unsafe_allow_html=True)
    st.stop()

# -----------------------
# Default Session
# -----------------------
defaults = {
    "menu_open": False,
    "page": "home",
    "pesanan": {},
    "nama_pelanggan": "",
    "total_bayar": 0,
    "struk": ""
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# -----------------------
# Styling
# -----------------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg,#071026,#0b1440);
    color: #e6eef8;
    font-family: "Segoe UI", sans-serif;
}
.topbar {
    display:flex;
    align-items:center;
    gap:12px;
    padding:10px 18px;
    background: linear-gradient(90deg,#b71c1c,#9c2a2a);
    color:white;
    border-radius:8px;
}
.right-panel {
    background: linear-gradient(180deg, rgba(8,10,16,0.94), rgba(12,14,22,0.90));
    padding: 14px;
    border-radius: 10px;
    box-shadow: -6px 6px 30px rgba(0,0,0,0.5);
    color: #fff;
}
.menu-item {
    display:block;
    width:100%;
    text-align:left;
    padding:10px 12px;
    margin:8px 0;
    border-radius:8px;
    background: rgba(255,255,255,0.03);
    color: #fff;
    font-weight:600;
    border: none;
}
.nota {
    background-color:#141826;
    padding:18px;
    border-radius:10px;
    border:1px solid #2f3340;
    font-family: "Courier New", monospace;
    white-space: pre;
    color:#e6eef8;
}
</style>
""", unsafe_allow_html=True)

# -----------------------
# Topbar
# -----------------------
col_tb1, col_tb2, col_tb3 = st.columns([1,10,2])
with col_tb1:
    if st.button("≡", key="hamb_btn"):
        st.session_state.menu_open = not st.session_state.menu_open
with col_tb2:
    st.markdown('<div class="topbar"><div style="font-weight:800">🍜 Mie Ayam & Bakso — Mas Ragil</div></div>', unsafe_allow_html=True)
with col_tb3:
    if st.button("🚪 Logout"):
        st.session_state.login = False
        st.experimental_rerun()

# -----------------------
# Layout
# -----------------------
if st.session_state.menu_open:
    main_col, side_col = st.columns([7,3])
else:
    main_col = st.columns([1])[0]
    side_col = None

# -----------------------
# Sidebar
# -----------------------
if side_col is not None:
    with side_col:
        st.markdown('<div class="right-panel">', unsafe_allow_html=True)
        st.markdown("<div style='font-weight:700;margin-bottom:8px'>Menu Navigasi</div>", unsafe_allow_html=True)
        if st.button("🏠 Beranda"): st.session_state.page="home"
        if st.button("🍜 Pesan Menu"): st.session_state.page="pesan"
        if st.button("💳 Pembayaran"): st.session_state.page="bayar"
        if st.button("📄 Struk"): st.session_state.page="struk"
        if st.button("📈 Laporan"): st.session_state.page="laporan"
        if st.button("ℹ️ Tentang"): st.session_state.page="tentang"
        st.markdown("<hr>", unsafe_allow_html=True)
        if st.button("♻️ Reset Pesanan"):
            st.session_state.pesanan={}
            st.session_state.nama_pelanggan=""
            st.session_state.total_bayar=0
            st.session_state.struk=""
            st.success("Pesanan direset.")
        st.markdown("<div style='font-size:12px;opacity:0.9;margin-top:8px'>Mas Ragil • Aplikasi Kasir</div>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# -----------------------
# Menu & Helpers
# -----------------------
menu_makanan = {"Mie Ayam":15000,"Bakso Urat":18000,"Mie Ayam Bakso":20000,"Bakso Telur":19000}
menu_minuman = {"Es Teh Manis":5000,"Es Jeruk":7000,"Teh Hangat":5000,"Jeruk Hangat":6000}

def save_transaction(timestamp,nama,items_dict,subtotal,diskon,total,bayar=None,kembalian=None):
    record={"timestamp":timestamp,"nama":nama,"items":json.dumps(items_dict,ensure_ascii=False),
            "subtotal":subtotal,"diskon":diskon,"total":total,"bayar":bayar if bayar else "","kembalian":kembalian if kembalian else ""}
    df=pd.DataFrame([record])
    if os.path.exists(DATA_FILE):
        df.to_csv(DATA_FILE,mode="a",header=False,index=False,encoding="utf-8-sig")
    else:
        df.to_csv(DATA_FILE,index=False,encoding="utf-8-sig")

def build_struk(nama,pesanan_dict,total_before,diskon,total_bayar,uang_bayar=None,kembalian=None):
    t="===== STRUK PEMBAYARAN =====\n"
    t+=f"Tanggal : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    t+=f"Nama    : {nama}\n"
    t+="-----------------------------\n"
    for it,subtotal in pesanan_dict.items():
        t+=f"{it:<20} Rp {subtotal:,}\n"
    t+="-----------------------------\n"
    t+=f"Sub Total           : Rp {total_before:,}\n"
    t+=f"Diskon              : Rp {diskon:,}\n"
    t+=f"Total Bayar         : Rp {total_bayar:,}\n"
    if uang_bayar:
        t+=f"Uang Diterima       : Rp {uang_bayar:,}\n"
        t+=f"Kembalian           : Rp {kembalian:,}\n"
    t+="=============================\n"
    t+="Terima kasih! Salam, Mas Ragil\n"
    return t

# -----------------------
# Halaman
# -----------------------
page = st.session_state.page
with main_col:
    if page=="home":
        st.header("Selamat Datang di Mie Ayam & Bakso Mas Ragil 🍜")
        st.write("Warung rumahan dengan cita rasa otentik. Pilih menu, hitung total, lalu bayar dan cetak struk.")
    elif page=="pesan":
        st.header("🍜 Pesan Menu")
        nama = st.text_input("Nama Pelanggan", value=st.session_state.nama_pelanggan)
        st.session_state.nama_pelanggan = nama
        st.subheader("Menu Makanan")
        for item, harga in menu_makanan.items():
            col1, col2, col3 = st.columns([2,1,1])
            with col1: st.write(f"{item} (Rp {harga:,})")
            with col2:
                if st.button("-", key=f"{item}-minus"): 
                    st.session_state.pesanan[item] = max(0, st.session_state.pesanan.get(item,0)-1)
            with col3:
                if st.button("+", key=f"{item}-plus"): 
                    st.session_state.pesanan[item] = st.session_state.pesanan.get(item,0)+1
        st.subheader("Menu Minuman")
        for item, harga in menu_minuman.items():
            col1, col2, col3 = st.columns([2,1,1])
            with col1: st.write(f"{item} (Rp {harga:,})")
            with col2:
                if st.button("-", key=f"{item}-minus-minum"): 
                    st.session_state.pesanan[item] = max(0, st.session_state.pesanan.get(item,0)-1)
            with col3:
                if st.button("+", key=f"{item}-plus-minum"): 
                    st.session_state.pesanan[item] = st.session_state.pesanan.get(item,0)+1
        st.write("Pesanan Saat Ini:", {k:v for k,v in st.session_state.pesanan.items() if v>0})
    elif page=="bayar":
        st.header("💳 Pembayaran")
        if not st.session_state.pesanan or sum(st.session_state.pesanan.values())==0:
            st.warning("Belum ada pesanan. Silakan pilih menu terlebih dahulu.")
        else:
            subtotal = sum(menu_makanan.get(k,0)*v + menu_minuman.get(k,0)*v for k,v in st.session_state.pesanan.items())
            diskon = int(subtotal*0.05) if subtotal>=100000 else 0
            total_bayar = subtotal - diskon
            st.write(f"Sub Total: Rp {subtotal:,}")
            st.write(f"Diskon: Rp {diskon:,}")
            st.write(f"Total Bayar: Rp {total_bayar:,}")
            uang = st.number_input("Uang Diterima", min_value=0, value=0)
            if st.button("Bayar"):
                if uang >= total_bayar:
                    kembalian = uang - total_bayar
                    st.success(f"Pembayaran berhasil. Kembalian: Rp {kembalian:,}")
                    struk = build_struk(
                        st.session_state.nama_pelanggan,
                        {k: v*(menu_makanan.get(k, menu_minuman.get(k,0))) for k,v in st.session_state.pesanan.items() if v>0},
                        subtotal,
                        diskon,
                        total_bayar,
                        uang,
                        kembalian
                    )
                    st.session_state.struk = struk
                    save_transaction(
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        st.session_state.nama_pelanggan,
                        {k:v for k,v in st.session_state.pesanan.items() if v>0},
                        subtotal,
                        diskon,
                        total_bayar,
                        uang,
                        kembalian
                    )
                    st.session_state.pesanan = {}
                else:
                    st.error("Uang diterima kurang!")
    elif page=="struk":
        st.header("📄 Struk")
        if st.session_state.struk:
            st.text(st.session_state.struk)
            if st.button("💾 Simpan Struk ke File"):
                with open("struk_terakhir.txt", "w", encoding="utf-8") as f:
                    f.write(st.session_state.struk)
                st.success("Struk berhasil disimpan ke file 'struk_terakhir.txt'.")
        else:
            st.warning("Belum ada struk. Silakan lakukan pembayaran terlebih dahulu.")
    elif page=="laporan":
        st.header("📈 Laporan Penjualan")
        if os.path.exists(DATA_FILE):
            df = pd.read_csv(DATA_FILE, encoding="utf-8-sig")
            df['total'] = df['total'].apply(lambda x: f"Rp {int(x):,}")
            st.dataframe(df)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            summary = df.groupby(df['timestamp'].dt.date)['total'].count()
            st.subheader("Total Transaksi per Hari")
            st.bar_chart(summary)
        else:
            st.info("Belum ada transaksi.")
    elif page=="tentang":
        st.header("ℹ️ Tentang Aplikasi")
        st.write("Aplikasi Kasir Mie Ayam & Bakso Mas Ragil versi Streamlit.")
        st.write("Membantu mencatat pesanan, pembayaran, dan laporan penjualan dengan mudah.")

st.markdown("---")
st.caption("© 2025 Mas Ragil — Aplikasi Kasir 🍜")
