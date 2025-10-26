# =====================================================
# 🍜 Kasir Mas Ragil — User App
# =====================================================
import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime

# -----------------------
# Konfigurasi
# -----------------------
st.set_page_config(page_title="Kasir Mas Ragil — User", page_icon="🍜", layout="wide")
DATA_FILE = "riwayat_penjualan.csv"
MENU_FILE = "menu.json"

# -----------------------
# Session Defaults
# -----------------------
if "pesanan" not in st.session_state:
    st.session_state.pesanan = {}
if "nama_pelanggan" not in st.session_state:
    st.session_state.nama_pelanggan = ""
if "total_bayar" not in st.session_state:
    st.session_state.total_bayar = 0

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
    with open(MENU_FILE,"w",encoding="utf-8") as f:
        json.dump({"makanan":menu_makanan,"minuman":menu_minuman}, f, ensure_ascii=False, indent=2)

# -----------------------
# Styling
# -----------------------
st.markdown("""
<style>
.stApp {background: linear-gradient(180deg,#071026,#0b1440); color:#e6eef8;}
.stButton>button {background: linear-gradient(90deg,#c62828,#9c1f1f); color:white; border:none; border-radius:6px; padding:8px 16px;}
.stButton>button:hover {transform:scale(1.05);}
</style>
""", unsafe_allow_html=True)

# -----------------------
# Halaman
# -----------------------
st.title("🍜 Kasir Mas Ragil — User")

# Nama pelanggan
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
            if st.button("-", key=f"{item}-minus"): 
                st.session_state.pesanan[item] = max(0, st.session_state.pesanan.get(item,0)-1)
        with col3:
            st.write(f"Qty: {st.session_state.pesanan.get(item,0)}")
        with col4:
            if st.button("+", key=f"{item}-plus"): 
                st.session_state.pesanan[item] = st.session_state.pesanan.get(item,0)+1

    st.subheader("🥤 Menu Minuman")
    for item,harga in menu_minuman.items():
        col1,col2,col3,col4 = st.columns([3,1,1,2])
        with col1: st.write(f"**{item}** (Rp {harga:,})")
        with col2:
            if st.button("-", key=f"{item}-minus-minum"): 
                st.session_state.pesanan[item] = max(0, st.session_state.pesanan.get(item,0)-1)
        with col3:
            st.write(f"Qty: {st.session_state.pesanan.get(item,0)}")
        with col4:
            if st.button("+", key=f"{item}-plus-minum"): 
                st.session_state.pesanan[item] = st.session_state.pesanan.get(item,0)+1

    # Keranjang
    pesanan_aktif = {k:v for k,v in st.session_state.pesanan.items() if v>0}
    if pesanan_aktif:
        st.subheader("🛒 Keranjang Pesanan")
        total = 0
        for k,v in pesanan_aktif.items():
            harga_satuan = menu_makanan.get(k, menu_minuman.get(k,0))
            subtotal = v*harga_satuan
            total += subtotal
            st.write(f"{k} x {v} = Rp {subtotal:,}")
        st.info(f"Total Bayar: Rp {total:,}")

        # Checkout
        if st.button("💳 Checkout"):
            # Simpan ke CSV
            record = {
                "timestamp":datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "nama":nama,
                "items":json.dumps(pesanan_aktif,ensure_ascii=False),
                "total":total
            }
            df = pd.DataFrame([record])
            if os.path.exists(DATA_FILE):
                df.to_csv(DATA_FILE, mode="a", header=False, index=False, encoding="utf-8-sig")
            else:
                df.to_csv(DATA_FILE, index=False, encoding="utf-8-sig")
            st.success("✅ Pesanan berhasil! Tunggu konfirmasi admin.")
            st.session_state.pesanan = {}

    else:
        st.info("Belum ada pesanan.")

# Reset pesanan
if st.button("♻️ Reset Pesanan"):
    st.session_state.pesanan = {}
    st.success("Pesanan direset.")

# Tentang
st.markdown("---")
st.subheader("ℹ️ Tentang Aplikasi")
st.write("Aplikasi Kasir Mie Ayam & Bakso Mas Ragil 🍜")
st.write("Dibuat dengan ❤️ oleh Mas Ragil.")
