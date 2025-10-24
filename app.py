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
# 🎨 Gaya & Tema Warna
# ===============================
st.markdown("""
    <style>
    body {
        background-color: #fff8e1;
    }
    .stTextArea textarea {
        font-family: 'Courier New', monospace;
        background-color: #fafafa;
        border-radius: 10px;
    }
    .stButton>button {
        background-color: #ffb300;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 8px 20px;
    }
    .stButton>button:hover {
        background-color: #ff8f00;
        color: #fff;
    }
    </style>
""", unsafe_allow_html=True)

# ===============================
# 🎯 Header Aplikasi
# ===============================
st.image("https://i.imgur.com/ZpVLK4t.png", width=120)
st.title("🍜 Kasir Mie Ayam & Bakso Mas Ragil")
st.caption("Sistem kasir modern berbasis web — dibuat dengan ❤️ pakai Streamlit")

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
# 💾 Inisialisasi session_state
# ===============================
if "pesanan" not in st.session_state:
    st.session_state.pesanan = {}
if "total_bayar" not in st.session_state:
    st.session_state.total_bayar = 0
if "struk" not in st.session_state:
    st.session_state.struk = ""
if "sudah_dihitung" not in st.session_state:
    st.session_state.sudah_dihitung = False

# ===============================
# 🧮 Input Pesanan
# ===============================
st.header("🧾 Pilih Pesanan Anda")

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

# ===============================
# 💰 Hitung Total
# ===============================
if st.button("💵 Hitung Total Pembayaran"):
    if not st.session_state.pesanan:
        st.warning("Belum ada pesanan yang dipilih.")
    else:
        total = sum(st.session_state.pesanan.values())
        diskon = int(0.1 * total) if total >= 50000 else 0
        total_bayar = total - diskon
        st.session_state.total_bayar = total_bayar
        st.session_state.sudah_dihitung = True

        # Buat struk awal
        struk = "===== STRUK PEMBAYARAN =====\n"
        for item, subtotal in st.session_state.pesanan.items():
            struk += f"{item:<20} Rp {subtotal:,}\n"
        struk += "\n"
        struk += f"Total Sebelum Diskon : Rp {total:,}\n"
        struk += f"Diskon (10%)         : Rp {diskon:,}\n"
        struk += f"Total Bayar          : Rp {total_bayar:,}\n"
        struk += "=============================\n"
        st.session_state.struk = struk

# ===============================
# 💳 Pembayaran
# ===============================
if st.session_state.sudah_dihitung:
    st.subheader("💳 Pembayaran")
    st.info(f"Total yang harus dibayar: **Rp {st.session_state.total_bayar:,}**")

    uang_bayar = st.number_input("Masukkan jumlah uang bayar:", min_value=0, step=1000, key="uang_bayar")

    if st.button("✅ Bayar Sekarang"):
        if uang_bayar <= 0:
            st.warning("Masukkan jumlah uang yang valid.")
        elif uang_bayar < st.session_state.total_bayar:
            st.error("❌ Uang tidak cukup untuk membayar.")
        else:
            kembalian = uang_bayar - st.session_state.total_bayar
            st.success(f"✅ Pembayaran berhasil!\nKembalian Anda: **Rp {kembalian:,}**")
            st.balloons()

            # Tambah ke struk
            st.session_state.struk += f"Uang Bayar           : Rp {uang_bayar:,}\n"
            st.session_state.struk += f"Kembalian            : Rp {kembalian:,}\n"
            st.session_state.struk += "=============================\nTerima kasih 🙏"

# ===============================
# 🧾 Tampilkan Struk Pembayaran
# ===============================
if st.session_state.struk:
    st.subheader("📄 Struk Pembayaran")
    st.text_area("Rincian Struk:", st.session_state.struk, height=240)
    st.download_button("💾 Unduh Struk", st.session_state.struk, file_name="struk_mie_ayam_mas_ragil.txt")

# ===============================
# 🔄 Tombol Reset Pesanan
# ===============================
st.write("---")
if st.button("🔄 Reset Pesanan"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.success("Pesanan berhasil direset! Silakan mulai pesanan baru 🍜")
    st.rerun()
