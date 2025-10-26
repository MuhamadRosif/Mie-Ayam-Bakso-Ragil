import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

MENU_FILE = "menu.json"
DATA_FILE = "riwayat_penjualan.csv"

st.set_page_config(page_title="User Kasir Mas Ragil", page_icon="🍜", layout="wide")

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
        menu_data = json.load(f)
else:
    st.error("Menu belum tersedia. Hubungi admin!")
    st.stop()

# -----------------------
# Halaman User
# -----------------------
st.header("🍜 Kasir Mie Ayam & Bakso — User")

nama = st.text_input("Nama Anda", value=st.session_state.nama_pelanggan)
st.session_state.nama_pelanggan = nama

if not nama.strip():
    st.warning("Masukkan nama Anda untuk memesan")
    st.stop()

st.subheader("🍽️ Menu Makanan")
for item,harga in menu_data["makanan"].items():
    col1,col2,col3,col4 = st.columns([3,1,1,2])
    with col1: st.write(f"**{item}** (Rp {harga:,})")
    with col2:
        if st.button("-", key=f"{item}-minus"): st.session_state.pesanan[item] = max(0, st.session_state.pesanan.get(item,0)-1)
    with col3: st.write(f"Qty: {st.session_state.pesanan.get(item,0)}")
    with col4:
        if st.button("+", key=f"{item}-plus"): st.session_state.pesanan[item] = st.session_state.pesanan.get(item,0)+1

st.subheader("🥤 Menu Minuman")
for item,harga in menu_data["minuman"].items():
    col1,col2,col3,col4 = st.columns([3,1,1,2])
    with col1: st.write(f"**{item}** (Rp {harga:,})")
    with col2:
        if st.button("-", key=f"{item}-minus-minum"): st.session_state.pesanan[item] = max(0, st.session_state.pesanan.get(item,0)-1)
    with col3: st.write(f"Qty: {st.session_state.pesanan.get(item,0)}")
    with col4:
        if st.button("+", key=f"{item}-plus-minum"): st.session_state.pesanan[item] = st.session_state.pesanan.get(item,0)+1

# -----------------------
# Keranjang
# -----------------------
pesanan_aktif = {k:v for k,v in st.session_state.pesanan.items() if v>0}
if pesanan_aktif:
    st.markdown("### 🛒 Keranjang Anda:")
    total = 0
    for k,v in pesanan_aktif.items():
        harga_satuan = menu_data["makanan"].get(k, menu_data["minuman"].get(k,0))
        subtotal = v*harga_satuan
        st.write(f"{k} x {v} = Rp {subtotal:,}")
        total += subtotal
    st.info(f"Total Pesanan: Rp {total:,}")
    if st.button("✅ Checkout"):
        diskon = int(total*0.05) if total>=100000 else 0
        total_bayar = total-diskon
        record = {
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "nama": nama,
            "items": json.dumps(pesanan_aktif, ensure_ascii=False),
            "subtotal": total,
            "diskon": diskon,
            "total": total_bayar,
            "bayar":"",
            "kembalian":""
        }
        df = pd.DataFrame([record])
        if os.path.exists(DATA_FILE):
            df.to_csv(DATA_FILE,mode="a",header=False,index=False,encoding="utf-8-sig")
        else:
            df.to_csv(DATA_FILE,index=False,encoding="utf-8-sig")
        st.success(f"✅ Pesanan berhasil dikirim ke admin. Total: Rp {total_bayar:,}")
        st.session_state.pesanan = {}
