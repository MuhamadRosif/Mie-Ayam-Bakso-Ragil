# app.py
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
# Admin Login (Modern & Berwarna)
# -----------------------
if "login" not in st.session_state:
    st.session_state.login = False

ADMIN_USER = "admin"
ADMIN_PASS = "1234"

if not st.session_state.login:
    st.markdown("""
    <style>
    .login-container {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100vh;
        background: linear-gradient(135deg,#ff5858,#f857a6);
    }
    .login-card {
        background: linear-gradient(135deg,#1f1f1f,#121212);
        padding: 50px;
        border-radius: 15px;
        width: 400px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.6);
        color: #e6eef8;
        text-align: center;
    }
    .stTextInput>div>div>input { 
        background: rgba(255,255,255,0.05); 
        color: #e6eef8; 
        border-radius:5px; 
        padding:8px;
        font-weight:bold;
    }
    .stButton>button { 
        background: linear-gradient(90deg,#ff512f,#dd2476); 
        color:white; 
        font-weight:bold; 
        width:100%; 
        margin-top:15px; 
        padding:10px; 
        border-radius:8px;
    }
    .login-title { font-size:24px; font-weight:bold; margin-bottom:20px; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="login-container"><div class="login-card">', unsafe_allow_html=True)
    st.markdown('<div class="login-title">🔐 Login Admin — Kasir Mas Ragil</div>', unsafe_allow_html=True)
    
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Masuk"):
        if username == ADMIN_USER and password == ADMIN_PASS:
            st.session_state.login = True
            st.success("Login berhasil — Selamat datang, admin!")
            st.experimental_rerun()
        else:
            st.error("Username atau password salah.")
    st.markdown('</div></div>', unsafe_allow_html=True)
    st.stop()

# -----------------------
# Session defaults
# -----------------------
defaults = {
    "menu_open": False,
    "page": "home",
    "pesanan": {},
    "nama_pelanggan": "",
    "total_bayar": 0,
    "struk": ""
}
for k,v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# -----------------------
# Styling
# -----------------------
st.markdown("""
<style>
.stApp { background: linear-gradient(180deg,#071026,#0b1440); color: #e6eef8; }
.topbar { display:flex; align-items:center; gap:12px; padding:10px 18px; background: linear-gradient(90deg,#b71c1c,#9c2a2a); color:white; border-radius:8px;}
.right-panel { background: linear-gradient(180deg, rgba(8,10,16,0.94), rgba(12,14,22,0.90)); padding: 14px; border-radius: 10px; box-shadow: -6px 6px 30px rgba(0,0,0,0.5); color: #fff; }
.menu-item { display:block; width:100%; text-align:left; padding:10px 12px; margin:8px 0; border-radius:8px; background: rgba(255,255,255,0.03); color: #fff; font-weight:600; border: none; }
.nota { background-color:#141826; padding:18px; border-radius:10px; border:1px solid #2f3340; font-family: "Courier New", monospace; white-space: pre; color:#e6eef8; }
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
# Layout & Sidebar
# -----------------------
if st.session_state.menu_open:
    main_col, side_col = st.columns([7,3])
else:
    main_col = st.columns([1])[0]
    side_col = None

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
        df.to_csv(DATA_FILE,mode="a",header=False,index=False)
    else:
        df.to_csv(DATA_FILE,index=False)

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
# Pages
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
        st.write("Pesanan Saat Ini:", {k:v for k,v in st.session_state.pesanan.items() if v>0})

st.markdown("---")
st.caption("© 2025 Mas Ragil — Aplikasi Kasir")
