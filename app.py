# ==============================
# Kasir Mas Ragil 🍜 — Final Enhanced
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
# Admin Login
# -----------------------
if "login" not in st.session_state:
    st.session_state.login = False

ADMIN_USER = "admin"
ADMIN_PASS = "1234"

if not st.session_state.login:
    st.markdown("""
    <style>
    .stApp { background: linear-gradient(180deg,#071026,#0b1440); color:#e6eef8; font-family:"Segoe UI";}
    .login-card { background-color:#1b1b1b; padding:40px; border-radius:12px; width:360px; text-align:center; margin:100px auto; box-shadow:0 4px 20px rgba(0,0,0,0.4);}
    .login-title { font-size:22px; font-weight:bold; margin-bottom:20px;}
    .stTextInput>div>div>input { background-color:#2b2b2b; color:#fff; border:1px solid #444; border-radius:6px; padding:10px;}
    .stButton>button { background-color:#c62828; color:white; border:none; border-radius:6px; padding:10px 20px; width:100px; margin-top:10px;}
    .stButton>button:hover { background-color:#9c1f1f;}
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    st.markdown('<div class="login-title">🔐 Login Admin — Kasir Mas Ragil</div>', unsafe_allow_html=True)
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Masuk"):
        if username == ADMIN_USER and password == ADMIN_PASS:
            st.session_state.login = True
            st.rerun()
        else:
            st.error("Username atau password salah.")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# -----------------------
# Session Defaults
# -----------------------
defaults = {"menu_open": False, "page": "home", "pesanan": {}, "nama_pelanggan": "", "total_bayar": 0, "struk": ""}
for k,v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# -----------------------
# Enhanced Styling
# -----------------------
st.markdown("""
<style>
.stApp { background: linear-gradient(180deg,#071026,#0b1440); color:#e6eef8; font-family:"Segoe UI";}
.topbar { display:flex; align-items:center; gap:12px; padding:10px 18px; background:linear-gradient(90deg,#b71c1c,#9c2a2a); color:white; border-radius:8px;}
.right-panel { background:linear-gradient(180deg,rgba(8,10,16,0.94),rgba(12,14,22,0.90)); padding:14px; border-radius:10px; box-shadow:-6px 6px 30px rgba(0,0,0,0.5);}
.nota { background-color:#141826; padding:18px; border-radius:10px; border:1px solid #2f3340; font-family:"Courier New", monospace; white-space: pre; color:#e6eef8; box-shadow: inset 0 0 10px rgba(0,0,0,0.5);}
.qty-btn button { background-color:#444; color:#fff; width:30px; height:30px; border:none; border-radius:6px; font-weight:bold; transition:all 0.2s; }
.qty-btn button:hover { background-color:#666; }
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
        st.rerun()

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
if side_col:
    with side_col:
        st.markdown('<div class="right-panel">', unsafe_allow_html=True)
        st.markdown("<div style='font-weight:700;margin-bottom:8px'>🍽️ Menu Navigasi</div>", unsafe_allow_html=True)
        if st.button("🏠 Beranda", key="nav_home"): st.session_state.page="home"
        if st.button("🍜 Pesan Menu", key="nav_pesan"): st.session_state.page="pesan"
        if st.button("💳 Pembayaran", key="nav_bayar"): st.session_state.page="bayar"
        if st.button("📄 Struk", key="nav_struk"): st.session_state.page="struk"
        if st.button("📈 Laporan", key="nav_laporan"): st.session_state.page="laporan"
        if st.button("ℹ️ Tentang", key="nav_tentang"): st.session_state.page="tentang"
        st.markdown("<hr>", unsafe_allow_html=True)
        if st.button("♻️ Reset Pesanan", key="reset"):
            st.session_state.pesanan={}
            st.session_state.nama_pelanggan=""
            st.session_state.total_bayar=0
            st.session_state.struk=""
            st.success("Pesanan direset.")
        st.markdown("<div style='font-size:12px;opacity:0.9;margin-top:8px'>Mas Ragil • Aplikasi Kasir 🍜</div>", unsafe_allow_html=True)
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
    t+="Terima kasih! Salam, Mas Ragil 🍜\n"
    return t

# -----------------------
# Halaman
# -----------------------
page = st.session_state.page
with main_col:
    if page=="home":
        st.header("🏠 Selamat Datang di Mie Ayam & Bakso Mas Ragil 🍜")
        st.write("Warung rumahan dengan cita rasa otentik. Pilih menu, hitung total, lalu bayar dan cetak struk.")
    elif page=="pesan":
        st.header("🍜 Pesan Menu")
        nama = st.text_input("Nama Pelanggan", value=st.session_state.nama_pelanggan, placeholder="Masukkan nama pelanggan")
        st.session_state.nama_pelanggan = nama

        # Menu Makanan
        st.subheader("🍽️ Menu Makanan")
        for item,harga in menu_makanan.items():
            col1,col2,col3,col4 = st.columns([3,1,1,2])
            with col1: st.write(f"**{item}** (Rp {harga:,})")
            with col2:
                if st.button("-", key=f"{item}-minus"):
                    st.session_state.pesanan[item] = max(0, st.session_state.pesanan.get(item,0)-1)
            with col3: st.write(f"Qty: {st.session_state.pesanan.get(item,0)}")
            with col4:
                if st.button("+", key=f"{item}-plus"):
                    st.session_state.pesanan[item] = st.session_state.pesanan.get(item,0)+1

        # Menu Minuman
        st.subheader("🥤 Menu Minuman")
        for item,harga in menu_minuman.items():
            col1,col2,col3,col4 = st.columns([3,1,1,2])
            with col1: st.write(f"**{item}** (Rp {harga:,})")
            with col2:
                if st.button("-", key=f"{item}-minus-minum"):
                    st.session_state.pesanan[item] = max(0, st.session_state.pesanan.get(item,0)-1)
            with col3: st.write(f"Qty: {st.session_state.pesanan.get(item,0)}")
            with col4:
                if st.button("+", key=f"{item}-plus-minum"):
                    st.session_state.pesanan[item] = st.session_state.pesanan.get(item,0)+1

        # Pesanan Saat Ini (Realistic Table)
        pesanan_aktif = {k:v for k,v in st.session_state.pesanan.items() if v>0}
        if pesanan_aktif:
            st.subheader("🛒 Pesanan Saat Ini")
            df_pesan = pd.DataFrame([
                {"Menu":k, "Qty":v, "Harga":menu_makanan.get(k,menu_minuman.get(k,0)),
                 "Subtotal":v*menu_makanan.get(k,menu_minuman.get(k,0))} 
                for k,v in pesanan_aktif.items()
            ])
            st.table(df_pesan)
            subtotal = df_pesan["Subtotal"].sum()
            st.info(f"Subtotal Sementara: Rp {subtotal:,}")
        else:
            st.info("Belum ada pesanan.")

st.markdown("---")
st.caption("© 2025 Mas Ragil — Aplikasi Kasir 🍜 | Versi Enhanced")
