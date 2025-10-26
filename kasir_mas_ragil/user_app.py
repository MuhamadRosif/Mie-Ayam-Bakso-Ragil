# =====================================================
# 🍜 Kasir Mas Ragil — User App
# =====================================================
import streamlit as st
import json
from datetime import datetime
import os

# -----------------------
# Konfigurasi Aplikasi
# -----------------------
st.set_page_config(page_title="Kasir Mas Ragil — User", page_icon="🍜", layout="wide")
MENU_FILE = "menu.json"
DATA_FILE = "riwayat_penjualan.csv"

# -----------------------
# Default Session
# -----------------------
defaults = {
    "pesanan": {},
    "nama_pelanggan": "",
    "page": "home"
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
    with open(MENU_FILE,"w",encoding="utf-8") as f:
        json.dump({"makanan":menu_makanan,"minuman":menu_minuman},f,ensure_ascii=False, indent=2)

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
.nota {background-color:#141826; padding:18px; border-radius:10px; border:1px solid #2f3340; font-family:"Courier New", monospace;}
.stButton>button {background: linear-gradient(90deg,#c62828,#9c1f1f); color:white; border:none; border-radius:6px; padding:8px 16px;}
.stButton>button:hover {transform:scale(1.05);}
</style>
""", unsafe_allow_html=True)

# -----------------------
# Topbar
# -----------------------
col_tb1, col_tb2, col_tb3 = st.columns([1,10,2])
with col_tb2:
    st.markdown('<div class="topbar"><div style="font-weight:800">🍜 Kasir Mas Ragil — User</div></div>', unsafe_allow_html=True)
with col_tb3:
    if st.button("♻️ Reset Pesanan"):
        st.session_state.pesanan={}
        st.session_state.nama_pelanggan=""
        st.success("Keranjang direset.")

# -----------------------
# Layout
# -----------------------
main_col = st.columns([1])[0]

# -----------------------
# Halaman
# -----------------------
page = st.session_state.page
with main_col:
    if page=="home":
        st.header("🏠 Selamat Datang di Mie Ayam & Bakso Mas Ragil 🍜")
        st.write("Pilih menu dan tambahkan ke keranjangmu.")
        st.image("https://via.placeholder.com/800x400/071026/ffffff?text=Mie+Ayam+%26+Bakso+Mas+Ragil", width=800)
        if st.button("🚀 Mulai Pesan"):
            st.session_state.page="pesan"
            st.experimental_rerun()

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

            pesanan_aktif = {k:v for k,v in st.session_state.pesanan.items() if v>0}
            if pesanan_aktif:
                st.markdown("**🛒 Keranjang:**")
                total = 0
                for k,v in pesanan_aktif.items():
                    harga_satuan = menu_makanan.get(k, menu_minuman.get(k,0))
                    st.write(f"{k} x {v} = Rp {v*harga_satuan:,}")
                    total += v*harga_satuan
                st.info(f"Total Pesanan: Rp {total:,}")
                if st.button("💳 Checkout"):
                    # Simpan otomatis ke CSV (untuk admin)
                    record={"timestamp":datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            "nama":st.session_state.nama_pelanggan,
                            "items":json.dumps(pesanan_aktif, ensure_ascii=False),
                            "subtotal":total,
                            "diskon":0,
                            "total":total,
                            "bayar":total,
                            "kembalian":0}
                    import pandas as pd
                    df=pd.DataFrame([record])
                    if os.path.exists(DATA_FILE):
                        df.to_csv(DATA_FILE,mode="a",header=False,index=False,encoding="utf-8-sig")
                    else:
                        df.to_csv(DATA_FILE,index=False,encoding="utf-8-sig")
                    st.success("✅ Pesanan dikirim ke admin!")
                    st.session_state.pesanan={}
                    st.session_state.page="home"
                    st.experimental_rerun()
            else:
                st.info("Belum ada item di keranjang.")

    # ------------------- TENTANG -------------------
    elif page=="tentang":
        st.header("ℹ️ Tentang Aplikasi")
        st.write("Aplikasi Kasir Mie Ayam & Bakso Mas Ragil 🍜 untuk pelanggan/user.")
        st.write("Hanya bisa pesan menu dan checkout, sementara admin yang memproses pembayaran.")
        st.write("Dibuat dengan ❤️ oleh Mas Ragil.")

st.markdown("---")
st.caption("© 2025 Mas Ragil — User App 🍜")
