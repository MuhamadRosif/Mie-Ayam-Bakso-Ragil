import streamlit as st
import json
import os
from datetime import datetime

MENU_FILE = "kasir_mas_ragil/menu.json"
DATA_FILE = "riwayat_penjualan.csv"

def run_user():
    # Session defaults
    if "user_login" not in st.session_state:
        st.session_state.user_login = False
    if "user_nama" not in st.session_state:
        st.session_state.user_nama = ""
    if "keranjang" not in st.session_state:
        st.session_state.keranjang = {}
    if "menu_makanan" not in st.session_state:
        st.session_state.menu_makanan = {}
    if "menu_minuman" not in st.session_state:
        st.session_state.menu_minuman = {}

    # Load menu
    if os.path.exists(MENU_FILE):
        with open(MENU_FILE,"r",encoding="utf-8") as f:
            data = json.load(f)
            st.session_state.menu_makanan = data.get("makanan",{})
            st.session_state.menu_minuman = data.get("minuman",{})
    else:
        st.info("Menu belum tersedia.")

    # Registrasi/Login
    if not st.session_state.user_login:
        st.subheader("👤 Registrasi / Login User")
        nama = st.text_input("Nama Anda", key="user_reg_name")
        if st.button("Masuk / Daftar"):
            if nama.strip():
                st.session_state.user_login = True
                st.session_state.user_nama = nama
                st.success(f"Selamat datang, {nama}!")
                st.rerun()
            else:
                st.warning("Masukkan nama Anda.")
        return

    st.title(f"🍜 Selamat datang {st.session_state.user_nama}!")
    st.subheader("🍽️ Pesan Menu")
    for item,harga in st.session_state.menu_makanan.items():
        col1,col2,col3,col4 = st.columns([3,1,1,2])
        with col1: st.write(f"**{item}** (Rp {harga:,})")
        with col2:
            if st.button("-", key=f"{item}-minus"): 
                st.session_state.keranjang[item] = max(0, st.session_state.keranjang.get(item,0)-1)
        with col3: st.write(f"Qty: {st.session_state.keranjang.get(item,0)}")
        with col4:
            if st.button("+", key=f"{item}-plus"): 
                st.session_state.keranjang[item] = st.session_state.keranjang.get(item,0)+1

    for item,harga in st.session_state.menu_minuman.items():
        col1,col2,col3,col4 = st.columns([3,1,1,2])
        with col1: st.write(f"**{item}** (Rp {harga:,})")
        with col2:
            if st.button("-", key=f"{item}-minus-minum"): 
                st.session_state.keranjang[item] = max(0, st.session_state.keranjang.get(item,0)-1)
        with col3: st.write(f"Qty: {st.session_state.keranjang.get(item,0)}")
        with col4:
            if st.button("+", key=f"{item}-plus-minum"): 
                st.session_state.keranjang[item] = st.session_state.keranjang.get(item,0)+1

    # Keranjang
    st.subheader("🛒 Keranjang")
    keranjang_aktif = {k:v for k,v in st.session_state.keranjang.items() if v>0}
    if keranjang_aktif:
        total = 0
        for k,v in keranjang_aktif.items():
            harga_satuan = st.session_state.menu_makanan.get(k, st.session_state.menu_minuman.get(k,0))
            st.write(f"{k} x {v} = Rp {v*harga_satuan:,}")
            total += v*harga_satuan
        st.info(f"Total Bayar: Rp {total:,}")
        uang = st.number_input("Uang Diterima", min_value=0, value=total, step=1000, key="uang_user")
        if st.button("💳 Bayar Sekarang"):
            if uang >= total:
                kembalian = uang - total
                st.success(f"✅ Pembayaran berhasil! Kembalian: Rp {kembalian:,}")
                save_transaksi(keranjang_aktif, total, st.session_state.user_nama, uang, kembalian)
                st.session_state.keranjang = {}
                st.rerun()
            else:
                st.error("Uang tidak cukup!")
    else:
        st.info("Keranjang kosong.")

def save_transaksi(items,total,nama,uang,kembalian):
    record = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "nama": nama,
        "items": json.dumps(items, ensure_ascii=False),
        "total": total,
        "bayar": uang,
        "kembalian": kembalian
    }
    import pandas as pd
    df = pd.DataFrame([record])
    if os.path.exists(DATA_FILE):
        df.to_csv(DATA_FILE, mode="a", header=False, index=False, encoding="utf-8-sig")
    else:
        df.to_csv(DATA_FILE, index=False, encoding="utf-8-sig")
