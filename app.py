# app.py
import streamlit as st
from datetime import datetime

# ===============================
# Page config
# ===============================
st.set_page_config(page_title="Kasir Mas Ragil", page_icon="🍜", layout="wide")

# ===============================
# Session state defaults
# ===============================
if "menu_open" not in st.session_state:
    st.session_state.menu_open = False
if "page" not in st.session_state:
    st.session_state.page = "home"
if "pesanan" not in st.session_state:
    st.session_state.pesanan = {}
if "nama_pelanggan" not in st.session_state:
    st.session_state.nama_pelanggan = ""
if "total_bayar" not in st.session_state:
    st.session_state.total_bayar = 0
if "sudah_dihitung" not in st.session_state:
    st.session_state.sudah_dihitung = False
if "struk" not in st.session_state:
    st.session_state.struk = ""

# ===============================
# CSS (responsive + sidebar slide)
# ===============================
st.markdown(
    """
    <style>
    /* navbar */
    .topbar{
        background: linear-gradient(90deg,#c62828,#b71c1c);
        color: white;
        padding:10px 16px;
        border-radius:8px;
        display:flex;
        align-items:center;
        justify-content:space-between;
        box-shadow: 0 2px 6px rgba(0,0,0,0.12);
    }
    .hamburger{
        font-size:22px;
        font-weight:bold;
        background:transparent;
        color:white;
        border:none;
        cursor:pointer;
        padding:6px 10px;
        border-radius:6px;
    }
    .brand {
        font-weight:800;
        font-size:18px;
        text-align:center;
        color:white;
        flex:1;
    }

    /* slide panel */
    .side-panel {
        position: fixed;
        top: 60px;
        left: 12px;
        width: 280px;
        max-width: 80%;
        height: calc(100% - 80px);
        background: #fff;
        border-radius: 10px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.12);
        padding: 14px;
        transform: translateX(-340px);
        transition: transform 0.28s ease;
        z-index: 9999;
        overflow:auto;
    }
    .side-panel.open {
        transform: translateX(0);
    }
    .menu-item {
        display:block;
        padding:10px 12px;
        margin:6px 0;
        border-radius:8px;
        color:#c62828;
        font-weight:600;
        text-decoration:none;
    }
    .menu-item:hover{
        background:#fff0f0;
    }

    /* responsive adjustments */
    @media (max-width: 640px) {
        .brand { font-size:16px; }
        .side-panel { left: 8px; width: 86%; }
    }

    /* struk style */
    .nota {
        background-color:#fffbea;
        padding:18px;
        border-radius:10px;
        border:1px solid #e6d9a7;
        font-family: "Courier New", monospace;
        white-space: pre;
        color:#222;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ===============================
# Top bar HTML
# ===============================
col1, col2 = st.columns([1, 9])
with col1:
    # Hamburger button -> toggle
    if st.button("≡", key="hamb"):
        st.session_state.menu_open = not st.session_state.menu_open
with col2:
    st.markdown(
        '<div class="topbar"><div style="width:36px"></div><div class="brand">🍜 Mie Ayam & Bakso — Mas Ragil</div></div>',
        unsafe_allow_html=True,
    )

# ===============================
# Slide-out sidebar (rendered via CSS class toggle)
# ===============================
panel_class = "side-panel open" if st.session_state.menu_open else "side-panel"
st.markdown(
    f"""
    <div class="{panel_class}">
        <h3 style="color:#c62828; margin-top:0">Menu Navigasi</h3>
        <a href="#" class="menu-item" onclick="document.title='home'">🏠 Beranda</a>
        <a href="#" class="menu-item" onclick="document.title='pesan'">🍜 Pesan Menu</a>
        <a href="#" class="menu-item" onclick="document.title='bayar'">💳 Pembayaran</a>
        <a href="#" class="menu-item" onclick="document.title='struk'">📄 Struk</a>
        <a href="#" class="menu-item" onclick="document.title='tentang'">ℹ️ Tentang</a>
        <hr/>
        <div style="font-size:12px;color:#666">Tip: klik ikon ≡ lagi untuk tutup.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# NOTE:
# The above menu links use href="#" and onclick to change document.title as a mild hack
# to let users click — we still control navigation server-side using Streamlit buttons below.
# This avoids needing custom JS to call Streamlit.

# ===============================
# Navigation row (in-page) - fallback for accessibility
# ===============================
nav_col1, nav_col2, nav_col3, nav_col4, nav_col5 = st.columns([1,1,1,1,1])
if nav_col1.button("🏠 Beranda"):
    st.session_state.page = "home"
if nav_col2.button("🍜 Pesan Menu"):
    st.session_state.page = "pesan"
if nav_col3.button("💳 Pembayaran"):
    st.session_state.page = "bayar"
if nav_col4.button("📄 Struk"):
    st.session_state.page = "struk"
if nav_col5.button("ℹ️ Tentang"):
    st.session_state.page = "tentang"

st.markdown("---")

# ===============================
# Data menu
# ===============================
menu_makanan = {
    "Mie Ayam": 15000,
    "Bakso Urat": 18000,
    "Mie Ayam Bakso": 20000,
    "Bakso Telur": 19000,
}
menu_minuman = {
    "Es Teh Manis": 5000,
    "Es Jeruk": 7000,
    "Teh Hangat": 5000,
    "Jeruk Hangat": 6000,
}

# ===============================
# Helper: build struk text
# ===============================
def build_struk(nama, pesanan_dict, total_before, diskon, total_bayar, uang_bayar=None, kembalian=None):
    t = "===== STRUK PEMBAYARAN =====\n"
    t += f"Tanggal : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    t += f"Nama    : {nama}\n"
    t += "-----------------------------\n"
    for it, subtotal in pesanan_dict.items():
        t += f"{it:<20} Rp {subtotal:,}\n"
    t += "-----------------------------\n"
    t += f"Sub Total           : Rp {total_before:,}\n"
    t += f"Diskon              : Rp {diskon:,}\n"
    t += f"Total Bayar         : Rp {total_bayar:,}\n"
    if uang_bayar is not None:
        t += f"Uang Diterima       : Rp {uang_bayar:,}\n"
        t += f"Kembalian           : Rp {kembalian:,}\n"
    t += "=============================\n"
    t += "Terima kasih! Salam, Mas Ragil\n"
    return t

# ===============================
# PAGES
# ===============================
page = st.session_state.page

# --- HOME ---
if page == "home":
    st.header("Selamat Datang di Mie Ayam & Bakso Mas Ragil 🍜")
    st.write("Warung rumahan dengan cita rasa otentik. Pilih menu, hitung total, lalu bayar dan cetak struk.")
    # high quality image from Unsplash (royalty-free)
    st.image(
        "https://images.unsplash.com/photo-1604908177522-3f9a9b2f4d9f?q=80&w=1200&auto=format&fit=crop&ixlib=rb-4.0.3&s=8c71b1a1a7f2e3e8f6c1a8f0e8b2f9c4",
        caption="Mie Ayam & Bakso — nikmati hangatnya!",
        use_container_width=True,
    )

# --- PESAN MENU ---
elif page == "pesan":
    st.header("🍜 Pesan Menu")
    st.session_state.nama_pelanggan = st.text_input("Nama Pelanggan", st.session_state.nama_pelanggan)
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Makanan")
        for item, price in menu_makanan.items():
            qty = st.number_input(f"{item} (Rp {price:,})", min_value=0, max_value=20, step=1, key=f"m_{item}")
            if qty > 0:
                st.session_state.pesanan[item] = price * qty
            elif item in st.session_state.pesanan:
                del st.session_state.pesanan[item]
    with c2:
        st.subheader("Minuman")
        for item, price in menu_minuman.items():
            qty = st.number_input(f"{item} (Rp {price:,})", min_value=0, max_value=20, step=1, key=f"d_{item}")
            if qty > 0:
                st.session_state.pesanan[item] = price * qty
            elif item in st.session_state.pesanan:
                del st.session_state.pesanan[item]

    st.markdown("---")
    st.write("Daftar Pesanan Saat Ini:")
    if st.session_state.pesanan:
        for it, s in st.session_state.pesanan.items():
            st.write(f"- {it}: Rp {s:,}")
    else:
        st.info("Belum ada pesanan.")

    if st.button("💵 Hitung Total"):
        if not st.session_state.nama_pelanggan:
            st.warning("Masukkan nama pelanggan dulu.")
        elif not st.session_state.pesanan:
            st.warning("Belum ada pesanan.")
        else:
            sub_total = sum(st.session_state.pesanan.values())
            diskon = int(0.1 * sub_total) if sub_total >= 50000 else 0
            total_bayar = sub_total - diskon
            st.session_state.total_bayar = total_bayar
            st.session_state.sudah_dihitung = True
            # build struk (partial)
            st.session_state.struk = build_struk(
                st.session_state.nama_pelanggan,
                st.session_state.pesanan,
                sub_total,
                diskon,
                total_bayar,
            )
            st.success("Total dihitung. Lanjut ke Pembayaran.")

# --- PEMBAYARAN ---
elif page == "bayar":
    st.header("💳 Pembayaran")
    if not st.session_state.sudah_dihitung:
        st.warning("Silakan hitung total di menu Pesan terlebih dahulu.")
    else:
        st.info(f"Total yang harus dibayar: Rp {st.session_state.total_bayar:,}")
        uang = st.number_input("Masukkan uang bayar:", min_value=0, step=1000, key="pay_input")
        if st.button("✅ Bayar Sekarang"):
            if uang < st.session_state.total_bayar:
                st.error("Uang tidak cukup.")
            else:
                kembalian = uang - st.session_state.total_bayar
                # finalize struk
                # Recompute sub_total and diskon to include in final struk
                sub_total = sum(st.session_state.pesanan.values())
                diskon = int(0.1 * sub_total) if sub_total >= 50000 else 0
                st.session_state.struk = build_struk(
                    st.session_state.nama_pelanggan,
                    st.session_state.pesanan,
                    sub_total,
                    diskon,
                    st.session_state.total_bayar,
                    uang_bayar=uang,
                    kembalian=kembalian,
                )
                st.success(f"Pembayaran berhasil — Kembalian: Rp {kembalian:,}")
                st.balloons()
                # show nota right away
                st.markdown(
                    f'<div class="nota">{st.session_state.struk.replace(" ", "&nbsp;")}</div>',
                    unsafe_allow_html=True,
                )
                st.download_button("💾 Unduh Struk", st.session_state.struk, file_name="struk_mas_ragil.txt")
                # reset flags if you want to start new (optional)
                # st.session_state.pesanan = {}
                # st.session_state.sudah_dihitung = False

# --- STRUK ---
elif page == "struk":
    st.header("📄 Struk Pembayaran")
    if st.session_state.struk:
        st.markdown(
            f'<div class="nota">{st.session_state.struk.replace(" ", "&nbsp;")}</div>',
            unsafe_allow_html=True,
        )
        st.download_button("💾 Unduh Struk", st.session_state.struk, file_name="struk_mas_ragil.txt")
    else:
        st.info("Belum ada struk. Lakukan transaksi dulu.")

# --- TENTANG ---
elif page == "tentang":
    st.header("ℹ️ Tentang")
    st.write(
        """
        Aplikasi kasir sederhana untuk usaha Mie Ayam & Bakso Mas Ragil.
        - Responsive UI (mobile-friendly)
        - Navbar + hamburger (≡) yang membuka sidebar
        - Struk pembayaran bisa ditampilkan & diunduh
        """
    )

# ===============================
# Small footer
# ===============================
st.markdown("---")
st.caption("© Rosif Al Khikam — Kelompok 5 Boii")
