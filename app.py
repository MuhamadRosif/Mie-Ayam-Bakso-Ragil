# =====================================================
# 🍜 Kasir Mas Ragil — Versi Full Final + Backsound Musik
# =====================================================
import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime

# -----------------------
# Konfigurasi Aplikasi
# -----------------------
st.set_page_config(page_title="Kasir Mas Ragil", page_icon="🍜", layout="wide")
DATA_FILE = "riwayat_penjualan.csv"

# ===============================
# 🔊 Musik Backsound
# ===============================
# Taruh file "backsound.mp3" di folder yang sama dengan app.py
try:
    audio_file = open("asek.mp3", "rb")
    audio_bytes = audio_file.read()
    st.audio(audio_bytes, format="audio/mp3", loop=True, autoplay=True)
except FileNotFoundError:
    st.warning("🎵 File 'asek.mp3' belum ditemukan. Letakkan di folder yang sama dengan app.py.")

# -----------------------
# Login Admin
# -----------------------
if "login" not in st.session_state:
    st.session_state.login = False

ADMIN_USER = "admin"
ADMIN_PASS = "1234"

if not st.session_state.login:
    st.markdown("""
    <style>
    .stApp {background: linear-gradient(180deg,#071026,#0b1440); color:#e6eef8;}
    .login-card {background-color:#1b1b1b; padding:40px; border-radius:12px; width:360px; 
                 margin:120px auto; text-align:center; box-shadow:0 4px 20px rgba(0,0,0,0.4);}
    .stTextInput>div>div>input {background-color:#2b2b2b; color:#fff; border-radius:6px;}
    .stButton>button {background-color:#c62828; color:white; border:none; border-radius:6px; padding:8px 20px;}
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="login-card"><h3>🔐 Login Admin — Kasir Mas Ragil</h3>', unsafe_allow_html=True)
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
.stApp {background: linear-gradient(180deg,#071026,#0b1440); color:#e6eef8;}
.topbar {display:flex; align-items:center; gap:12px; padding:10px 18px; 
         background: linear-gradient(90deg,#b71c1c,#9c2a2a); color:white; 
         border-radius:8px; box-shadow:0 2px 10px rgba(0,0,0,0.3);}
.right-panel {background: linear-gradient(180deg,#0c0e16,#181b26); padding:14px; border-radius:10px;}
.menu-item {display:block; width:100%; padding:10px; border-radius:8px; background:#222; color:white; border:none;}
.menu-item:hover {background:#333;}
.nota {background-color:#141826; padding:18px; border-radius:10px; border:1px solid #2f3340; font-family:"Courier New", monospace;}
.stButton>button {background: linear-gradient(90deg,#c62828,#9c1f1f); color:white; border:none; border-radius:6px; padding:8px 16px;}
.stButton>button:hover {transform:scale(1.05);}
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
# Sidebar Navigasi
# -----------------------
if side_col is not None:
    with side_col:
        st.markdown('<div class="right-panel">', unsafe_allow_html=True)
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
        st.markdown("<div style='font-size:12px;opacity:0.7;'>© Mas Ragil 2025</div>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# -----------------------
# Data Menu
# -----------------------
menu_makanan = {"Mie Ayam":15000,"Bakso Urat":18000,"Mie Ayam Bakso":20000,"Bakso Telur":19000}
menu_minuman = {"Es Teh Manis":5000,"Es Jeruk":7000,"Teh Hangat":5000,"Jeruk Hangat":6000}

# -----------------------
# Fungsi Pendukung
# -----------------------
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
    t+=f"Sub Total : Rp {total_before:,}\n"
    t+=f"Diskon    : Rp {diskon:,}\n"
    t+=f"Total     : Rp {total_bayar:,}\n"
    if uang_bayar:
        t+=f"Bayar     : Rp {uang_bayar:,}\n"
        t+=f"Kembalian : Rp {kembalian:,}\n"
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
        st.write("Pilih menu, lakukan pembayaran, dan cetak struk pelanggan.")
        st.image("https://via.placeholder.com/800x400/071026/ffffff?text=Mie+Ayam+%26+Bakso+Mas+Ragil", use_container_width=True)
        if st.button("🚀 Mulai Transaksi Cepat"):
            st.session_state.page = "pesan"
            st.rerun()

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
            pesanan_aktif = {k:v for k,v in st.session_state.pesanan.items() if v>0}
            if pesanan_aktif:
                st.markdown("**📋 Pesanan Saat Ini:**")
                for k,v in pesanan_aktif.items():
                    harga_satuan = menu_makanan.get(k, menu_minuman.get(k,0))
                    st.write(f"{k} x {v} = Rp {v*harga_satuan:,}")
                subtotal = sum(menu_makanan.get(k,0)*v + menu_minuman.get(k,0)*v for k,v in pesanan_aktif.items())
                st.info(f"Subtotal: Rp {subtotal:,}")
            else:
                st.info("Belum ada pesanan.")

    elif page=="bayar":
        st.header("💳 Pembayaran")
        if not st.session_state.pesanan or sum(st.session_state.pesanan.values())==0:
            st.warning("Belum ada pesanan.")
        else:
            pesanan_aktif = {k:v for k,v in st.session_state.pesanan.items() if v>0}
            subtotal = sum(menu_makanan.get(k,0)*v + menu_minuman.get(k,0)*v for k,v in pesanan_aktif.items())
            diskon = int(subtotal*0.05) if subtotal>=100000 else 0
            total_bayar = subtotal - diskon
            st.write(f"Sub Total: Rp {subtotal:,}")
            st.write(f"Diskon: Rp {diskon:,}")
            st.write(f"Total Bayar: Rp {total_bayar:,}")
            uang = st.number_input("Uang Diterima", min_value=0, value=total_bayar, step=1000)
            if st.button("Bayar Sekarang"):
                if uang >= total_bayar:
                    kembalian = uang - total_bayar
                    st.success(f"✅ Pembayaran berhasil! Kembalian: Rp {kembalian:,}")
                    pesanan_subtotal = {k:v*(menu_makanan.get(k, menu_minuman.get(k,0))) for k,v in pesanan_aktif.items()}
                    struk = build_struk(st.session_state.nama_pelanggan,pesanan_subtotal,subtotal,diskon,total_bayar,uang,kembalian)
                    st.session_state.struk = struk
                    save_transaction(datetime.now().strftime('%Y-%m-%d %H:%M:%S'),st.session_state.nama_pelanggan,pesanan_aktif,subtotal,diskon,total_bayar,uang,kembalian)
                    st.session_state.pesanan = {}
                    st.session_state.page = "struk"
                    st.rerun()
                else:
                    st.error("Uang diterima kurang!")

    elif page=="struk":
        st.header("📄 Struk Pembayaran")
        if st.session_state.struk:
            st.markdown('<div class="nota">', unsafe_allow_html=True)
            st.text(st.session_state.struk)
            st.markdown('</div>', unsafe_allow_html=True)
            if st.button("💾 Simpan Struk"):
                with open("struk_terakhir.txt","w",encoding="utf-8") as f:
                    f.write(st.session_state.struk)
                st.success("Struk disimpan.")
        else:
            st.warning("Belum ada struk.")

    elif page=="laporan":
        st.header("📈 Laporan Penjualan")
        if os.path.exists(DATA_FILE):
            df = pd.read_csv(DATA_FILE, encoding="utf-8-sig")
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['total'] = df['total'].astype(int)
            st.dataframe(df[['timestamp','nama','subtotal','diskon','total','bayar','kembalian']])
            daily_revenue = df.groupby(df['timestamp'].dt.date)['total'].sum()
            st.bar_chart(daily_revenue)
        else:
            st.info("Belum ada transaksi.")

    elif page=="tentang":
        st.header("ℹ️ Tentang Aplikasi")
        st.write("Aplikasi Kasir Mie Ayam & Bakso Mas Ragil 🍜")
        st.write("Dilengkapi: Login admin, pembayaran, laporan, struk, reset, dan backsound musik akustik.")
        st.write("Dibuat dengan ❤️ oleh Mas Ragil.")

st.markdown("---")
st.caption("© 2025 Mas Ragil — Aplikasi Kasir 🍜 | Versi Full + Musik Akustik")
