# app.py
import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime
import time
import threading

# -----------------------
# Config
# -----------------------
st.set_page_config(page_title="Kasir Mas Ragil", page_icon="🍜", layout="wide")
DATA_FILE = "riwayat_penjualan.csv"

# -----------------------
# Typing header effect di biru atas
# -----------------------
header_placeholder = st.empty()
teks_header = "🌟 Kelompok 5 🌟   "

def typing_header():
    while True:
        display_text = ""
        for char in teks_header:
            display_text += char
            header_placeholder.markdown(f"""
            <div style="
                background-color:#0e3ca5;
                color:white;
                font-weight:bold;
                font-size:22px;
                padding:8px;
                text-align:center;
                font-family:monospace;
            ">{display_text}</div>
            """, unsafe_allow_html=True)
            time.sleep(0.1)

threading.Thread(target=typing_header, daemon=True).start()

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
    .login-box {
        background: linear-gradient(180deg, #101226, #0b1330);
        padding: 40px;
        border-radius: 12px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.5);
        color: #e6eef8;
        max-width: 420px;
        margin: 40px auto;
        text-align: center;
        position: relative;
    }
    .stTextInput>div>div>input { background: rgba(255,255,255,0.03); color: #e6eef8; }
    .stButton>button { background: linear-gradient(90deg,#c62828,#b71c1c); color: white; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='login-box'>", unsafe_allow_html=True)
    st.markdown("## 🔐 Login Admin — Kasir Mas Ragil", unsafe_allow_html=True)
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    col1, col2 = st.columns([1,1])
    with col1:
        if st.button("Masuk"):
            if username == ADMIN_USER and password == ADMIN_PASS:
                st.session_state.login = True
                st.success("Login berhasil — Selamat datang, admin!")
                st.experimental_rerun()
            else:
                st.error("Username atau password salah.")
    with col2:
        if st.button("Batal"):
            st.stop()
    st.markdown("</div>", unsafe_allow_html=True)
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
    "sudah_dihitung": False,
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

st.markdown("<br>", unsafe_allow_html=True)

# -----------------------
# Layout & Right Panel
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
            st.session_state.sudah_dihitung=False
            st.session_state.struk=""
            st.success("Pesanan direset.")
        st.markdown("<div style='font-size:12px;opacity:0.9;margin-top:8px'>Mas Ragil • Aplikasi Kasir • Kelompok 5</div>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# -----------------------
# Menu Data
# -----------------------
menu_makanan={"Mie Ayam":15000,"Bakso Urat":18000,"Mie Ayam Bakso":20000,"Bakso Telur":19000}
menu_minuman={"Es Teh Manis":5000,"Es Jeruk":7000,"Teh Hangat":5000,"Jeruk Hangat":6000}

# -----------------------
# Helpers
# -----------------------
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
page=st.session_state.page
with main_col:
    if page=="home":
        st.header("Selamat Datang di Mie Ayam & Bakso Mas Ragil 🍜")
        st.write("Warung rumahan dengan cita rasa otentik. Pilih menu, hitung total, lalu bayar dan cetak struk.")
        st.image("https://images.unsplash.com/photo-1604908177522-3f9a9b2f4d9f?q=80&w=1200&auto=format&fit=crop", use_container_width=True)
        st.markdown("---")
        st.subheader("Mulai Transaksi Cepat")
        c1,c2=st.columns(2)
        with c1:
            if st.button("➡️ Pesan Menu (langsung)"):
                st.session_state.page="pesan"
                st.experimental_rerun()
        with c2:
            if st.button("➡️ Pembayaran (langsung)"):
                st.session_state.page="bayar"
                st.experimental_rerun()

    elif page=="pesan":
        st.header("🍜 Pesan Menu")
        st.session_state.nama_pelanggan = st.text_input("Nama Pelanggan", st.session_state.nama_pelanggan)
        c1,c2=st.columns(2)
        with c1:
            st.subheader("Makanan")
            for item,price in menu_makanan.items():
                qty=st.number_input(f"{item} (Rp {price:,})", min_value=0,max_value=20,step=1,key=f"m_{item}")
                if qty>0:
                    st.session_state.pesanan[item]=price*qty
                elif item in st.session_state.pesanan:
                    del st.session_state.pesanan[item]
        with c2:
            st.subheader("Minuman")
            for item,price in menu_minuman.items():
                qty=st.number_input(f"{item} (Rp {price:,})", min_value=0,max_value=20,step=1,key=f"d_{item}")
                if qty>0:
                    st.session_state.pesanan[item]=price*qty
                elif item in st.session_state.pesanan:
                    del st.session_state.pesanan[item]

        st.markdown("---")
        c3,c4=st.columns([2,1])
        with c3:
            if st.button("💵 Hitung Total"):
                if not st.session_state.nama_pelanggan:
                    st.warning("Masukkan nama pelanggan dulu.")
                elif not st.session_state.pesanan:
                    st.warning("Belum ada pesanan.")
                else:
                    sub_total=sum(st.session_state.pesanan.values())
                    diskon=int(0.1*sub_total) if sub_total>=50000 else 0
                    total_bayar=sub_total-diskon
                    st.session_state.total_bayar=total_bayar
                    st.session_state.sudah_dihitung=True
                    st.session_state.struk=build_struk(
                        st.session_state.nama_pelanggan,
                        st.session_state.pesanan,
                        sub_total,
                        diskon,
                        total_bayar
                    )
                    st.success("Total dihitung. Lanjut ke Pembayaran.")
        with c4:
            if st.button("🔄 Reset Pesanan"):
                st.session_state.pesanan={}
                st.session_state.total_bayar=0
                st.session_state.sudah_dihitung=False
                st.session_state.struk=""
                st.success("Pesanan direset.")

    elif page=="bayar":
        st.header("💳 Pembayaran")
        if not st.session_state.sudah_dihitung:
            st.warning("Silakan hitung total di menu Pesan terlebih dahulu.")
            if st.button("➡️ Pergi ke Pesan"):
                st.session_state.page="pesan"
                st.experimental_rerun()
        else:
            st.info(f"Total yang harus dibayar: Rp {st.session_state.total_bayar:,}")
            uang=st.number_input("Masukkan uang bayar:", min_value=0, step=1000, key="pay_input")
            if st.button("✅ Bayar Sekarang"):
                if uang<st.session_state.total_bayar:
                    st.error("Uang tidak cukup.")
                else:
                    kembalian=uang-st.session_state.total_bayar
                    sub_total=sum(st.session_state.pesanan.values()) if st.session_state.pesanan else 0
                    diskon=int(0.1*sub_total) if sub_total>=50000 else 0
                    st.session_state.struk=build_struk(
                        st.session_state.nama_pelanggan,
                        st.session_state.pesanan,
                        sub_total,
                        diskon,
                        st.session_state.total_bayar,
                        uang_bayar=uang,
                        kembalian=kembalian
                    )
                    save_transaction(
                        timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        nama=st.session_state.nama_pelanggan,
                        items_dict=st.session_state.pesanan,
                        subtotal=sub_total,
                        diskon=diskon,
                        total=st.session_state.total_bayar,
                        bayar=uang,
                        kembalian=kembalian
                    )
                    st.success(f"Pembayaran berhasil — Kembalian: Rp {kembalian:,}")
                    st.balloons()
                    st.markdown(f'<div class="nota">{st.session_state.struk.replace(" ","&nbsp;")}</div>', unsafe_allow_html=True)
                    st.download_button("💾 Unduh Struk", st.session_state.struk, file_name="struk_mas_ragil.txt")
                    st.session_state.pesanan={}
                    st.session_state.total_bayar=0
                    st.session_state.sudah_dihitung=False

    elif page=="struk":
        st.header("📄 Struk Pembayaran")
        if st.session_state.struk:
            st.markdown(f'<div class="nota">{st.session_state.struk.replace(" ","&nbsp;")}</div>', unsafe_allow_html=True)
            st.download_button("💾 Unduh Struk", st.session_state.struk, file_name="struk_mas_ragil.txt")
        else:
            st.info("Belum ada struk. Lakukan transaksi dulu.")

    elif page=="laporan":
        st.header("📈 Laporan Penjualan")
        if os.path.exists(DATA_FILE):
            df=pd.read_csv(DATA_FILE)
            df['items_parsed']=df['items'].apply(lambda x: json.loads(x) if pd.notna(x) and x!='' else {})
            df['date']=pd.to_datetime(df['timestamp']).dt.date
            rev=df.groupby('date')['total'].sum().reset_index()
            rev.columns=['Tanggal','Total Pendapatan']
            st.subheader("Pendapatan per Hari")
            st.bar_chart(rev.set_index('Tanggal'))
            st.subheader("Riwayat Transaksi (terbaru)")
            st.dataframe(df.sort_values('timestamp',ascending=False).head(50))
            all_items={}
            for d in df['items_parsed']:
                for k,v in d.items():
                    all_items[k]=all_items.get(k,0)+v//(menu_makanan.get(k,1) if menu_makanan.get(k) else 1)
            if all_items:
                top=pd.DataFrame(list(all_items.items()),columns=['Menu','Jumlah (estimasi)']).sort_values('Jumlah (estimasi)',ascending=False)
                st.subheader("Menu Paling Sering Dipesan (estimasi)")
                st.bar_chart(top.set_index('Menu'))
            else:
                st.info("Belum ada data menu untuk dihitung.")
        else:
            st.info("Belum ada riwayat transaksi. Lakukan pembayaran untuk mulai menyimpan riwayat.")

    elif page=="tentang":
        st.header("ℹ️ Tentang")
        st.write("""
        Aplikasi kasir Mas Ragil — versi lengkap:
        - Login Admin (admin / 1234)
        - UI indigo-dark, panel kanan navigasi
        - Fitur Pesan → Hitung → Bayar → Cetak Struk
        - Riwayat transaksi otomatis tersimpan (riwayat_penjualan.csv)
        - Halaman Laporan: pendapatan per hari, riwayat, top menu (estimasi)
        """)

st.markdown("---")
st.caption("© Rosif Al Khikam — Kelompok 5 Boii")
