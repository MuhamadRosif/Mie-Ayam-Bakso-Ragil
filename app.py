import streamlit as st

# ===============================
# 🧾 Konfigurasi Halaman
# ===============================
st.set_page_config(
    page_title="Kasir Mie Ayam & Bakso Mas Ragil",
    page_icon="🍜",
    layout="centered"
)

# ===============================
# 💾 Session State
# ===============================
if "page" not in st.session_state:
    st.session_state.page = "home"
if "pesanan" not in st.session_state:
    st.session_state.pesanan = {}
if "total_bayar" not in st.session_state:
    st.session_state.total_bayar = 0
if "struk" not in st.session_state:
    st.session_state.struk = ""
if "sudah_dihitung" not in st.session_state:
    st.session_state.sudah_dihitung = False
if "nama_pelanggan" not in st.session_state:
    st.session_state.nama_pelanggan = ""

# ===============================
# 🎨 NAVBAR ATAS (dengan ikon ≡)
# ===============================
st.markdown("""
    <style>
    .navbar {
        background-color: #c62828;
        padding: 12px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .judul {
        color: white;
        font-weight: bold;
        font-size: 20px;
        text-align: center;
        width: 100%;
    }
    .menu-btn {
        font-size: 26px;
        color: white;
        cursor: pointer;
        margin-right: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# header bar dengan tombol garis 3
col1, col2, col3 = st.columns([1, 6, 1])
with col1:
    menu_open = st.button("≡")
with col2:
    st.markdown('<div class="judul">🍜 Kasir Mie Ayam & Bakso Mas Ragil</div>', unsafe_allow_html=True)

st.markdown("---")

# ===============================
# 🌐 SIDEBAR (navigasi)
# ===============================
if menu_open:
    st.sidebar.title("📂 Menu Navigasi")
    halaman = st.sidebar.radio(
        "Pilih Halaman:",
        ["🏠 Beranda", "🍜 Pesan Menu", "💳 Pembayaran", "📄 Struk", "ℹ️ Tentang"]
    )
    if halaman == "🏠 Beranda":
        st.session_state.page = "home"
    elif halaman == "🍜 Pesan Menu":
        st.session_state.page = "pesan"
    elif halaman == "💳 Pembayaran":
        st.session_state.page = "bayar"
    elif halaman == "📄 Struk":
        st.session_state.page = "struk"
    elif halaman == "ℹ️ Tentang":
        st.session_state.page = "tentang"

# ===============================
# 📋 Daftar Menu
# ===============================
menu_makanan = {
    "Mie Ayam": 15000,
    "Bakso Urat": 18000,
    "Mie Ayam Bakso": 20000,
    "Bakso Telur": 19000
}

menu_minuman = {
    "Es Teh Manis": 5000,
    "Es Jeruk": 7000,
    "Teh Hangat": 5000,
    "Jeruk Hangat": 6000
}

# ===============================
# 🏠 HALAMAN BERANDA
# ===============================
if st.session_state.page == "home":
    st.title("Selamat Datang di 🍜 Mas Ragil")
    st.info("Gunakan tombol ≡ di kiri atas untuk membuka menu navigasi.")
    st.image("https://upload.wikimedia.org/wikipedia/commons/f/f6/Mie_ayam_jamur.jpg",
             caption="Mie Ayam & Bakso Mas Ragil - Lezat & Nikmat", use_container_width=True)

# ===============================
# 🍜 HALAMAN PESAN MENU
# ===============================
elif st.session_state.page == "pesan":
    st.header("🧾 Pilih Pesanan Anda")
    st.session_state.nama_pelanggan = st.text_input("🧍 Nama Pelanggan", st.session_state.nama_pelanggan)

    tab1, tab2 = st.tabs(["🍜 Makanan", "🥤 Minuman"])

    with tab1:
        st.subheader("🍜 Pilih Makanan")
        for item, harga in menu_makanan.items():
            qty = st.number_input(f"{item} (Rp {harga:,})", min_value=0, max_value=20, step=1, key=item)
            if qty > 0:
                st.session_state.pesanan[item] = harga * qty
            elif item in st.session_state.pesanan:
                del st.session_state.pesanan[item]

    with tab2:
        st.subheader("🥤 Pilih Minuman")
        for item, harga in menu_minuman.items():
            qty = st.number_input(f"{item} (Rp {harga:,})", min_value=0, max_value=20, step=1, key=item)
            if qty > 0:
                st.session_state.pesanan[item] = harga * qty
            elif item in st.session_state.pesanan:
                del st.session_state.pesanan[item]

    if st.button("💵 Hitung Total Pembayaran"):
        if not st.session_state.nama_pelanggan:
            st.warning("Masukkan nama pelanggan terlebih dahulu.")
        elif not st.session_state.pesanan:
            st.warning("Belum ada pesanan yang dipilih.")
        else:
            total = sum(st.session_state.pesanan.values())
            diskon = int(0.1 * total) if total >= 50000 else 0
            total_bayar = total - diskon
            st.session_state.total_bayar = total_bayar
            st.session_state.sudah_dihitung = True

            struk = "===== STRUK PEMBAYARAN =====\n"
            struk += f"Nama Pelanggan : {st.session_state.nama_pelanggan}\n"
            struk += "-----------------------------\n"
            for item, subtotal in st.session_state.pesanan.items():
                struk += f"{item:<20} Rp {subtotal:,}\n"
            struk += "\n"
            struk += f"Total Sebelum Diskon : Rp {total:,}\n"
            struk += f"Diskon (10%)         : Rp {diskon:,}\n"
            struk += f"Total Bayar          : Rp {total_bayar:,}\n"
            struk += "=============================\n"
            st.session_state.struk = struk
            st.success("✅ Total sudah dihitung! Silakan lanjut ke 💳 Pembayaran.")

# ===============================
# 💳 HALAMAN PEMBAYARAN
# ===============================
elif st.session_state.page == "bayar":
    st.header("💳 Pembayaran")

    if not st.session_state.sudah_dihitung:
        st.warning("Silakan hitung total terlebih dahulu di menu Pesan.")
    else:
        st.info(f"Total yang harus dibayar: **Rp {st.session_state.total_bayar:,}**")
        uang_bayar = st.number_input("Masukkan jumlah uang bayar:", min_value=0, step=1000, key="uang_bayar")

        if st.button("✅ Bayar Sekarang"):
            if uang_bayar < st.session_state.total_bayar:
                st.error("❌ Uang tidak cukup.")
            else:
                kembalian = uang_bayar - st.session_state.total_bayar
                st.success(f"✅ Pembayaran berhasil! Kembalian Anda: Rp {kembalian:,}")
                st.balloons()
                st.session_state.struk += f"Uang Bayar           : Rp {uang_bayar:,}\n"
                st.session_state.struk += f"Kembalian            : Rp {kembalian:,}\n"
                st.session_state.struk += "=============================\nTerima kasih 🙏"

# ===============================
# 📄 HALAMAN STRUK
# ===============================
elif st.session_state.page == "struk":
    st.header("📄 Struk Pembayaran")
    if st.session_state.struk:
        st.markdown(
            f"""
            <div style="
                background-color:#fffbea;
                padding:20px;
                border-radius:10px;
                border:1px solid #ddd;
                font-family:monospace;
                white-space:pre;
                color:#333;">
            {st.session_state.struk}
            </div>
            """,
            unsafe_allow_html=True
        )
        st.download_button("💾 Unduh Struk", st.session_state.struk, file_name="Struk_MieAyamMasRagil.txt")
    else:
        st.info("Belum ada struk. Silakan lakukan pembayaran terlebih dahulu.")

# ===============================
# ℹ️ HALAMAN TENTANG
# ===============================
elif st.session_state.page == "tentang":
    st.header("ℹ️ Tentang Aplikasi")
    st.write("""
    Aplikasi kasir ini dibuat untuk mempermudah transaksi di warung **Mie Ayam & Bakso Mas Ragil** 🍜  
    Dibangun dengan framework **Streamlit**, ringan, cepat, dan bisa dijalankan langsung di browser.

    **Fitur:**
    - Navigasi dengan tombol garis tiga (≡)
    - Input nama pelanggan  
    - Pemesanan makanan & minuman  
    - Diskon otomatis 10% di atas Rp 50.000  
    - Pembayaran & hitung kembalian  
    - Cetak & unduh struk digital  

    _Dibuat dengan ❤️ oleh Tim Kasir Mas Ragil_
    """)
