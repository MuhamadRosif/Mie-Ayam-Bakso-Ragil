# app.py (stable Streamlit-only version)
import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Kasir Mas Ragil", page_icon="🍜", layout="wide")

# -----------------------
# Defaults
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
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# -----------------------
# CSS (dark indigo + right-panel look)
# -----------------------
st.markdown("""
<style>
/* app background */
.stApp {
  background: linear-gradient(180deg,#0b1020,#0e1430);
  color: #e6eef8;
}

/* topbar */
.topbar {
  display:flex;
  align-items:center;
  gap:12px;
  padding:10px 18px;
  background: linear-gradient(90deg,#b71c1c,#9c2a2a);
  color:white;
  border-radius:8px;
}

/* right panel look */
.right-panel {
  background: linear-gradient(180deg, rgba(8,10,16,0.94), rgba(12,14,22,0.90));
  padding: 14px;
  border-radius: 10px;
  box-shadow: -6px 6px 30px rgba(0,0,0,0.5);
  color: #fff;
}

/* menu item */
.menu-item {
  display:block;
  width:100%;
  text-align:left;
  padding:10px 12px;
  margin:8px 0;
  border-radius:8px;
  background: rgba(255,255,255,0.03);
  color: #fff;
  font-weight:600;
  border: none;
}

/* nota */
.nota {
  background-color:#1f2330;
  padding:18px;
  border-radius:10px;
  border:1px solid #2f3340;
  font-family: "Courier New", monospace;
  white-space: pre;
  color:#e6eef8;
}
</style>
""", unsafe_allow_html=True)

# -----------------------
# Topbar (hamburger + brand)
# -----------------------
col_tb1, col_tb2 = st.columns([1, 11])
with col_tb1:
    if st.button("≡", key="hamb_btn"):
        st.session_state.menu_open = not st.session_state.menu_open
with col_tb2:
    st.markdown('<div class="topbar"><div style="font-weight:800">🍜 Mie Ayam & Bakso — Mas Ragil</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# -----------------------
# Layout: main + optional right panel
# -----------------------
if st.session_state.menu_open:
    main_col, side_col = st.columns([7, 3])
else:
    main_col = st.columns([1])[0]
    side_col = None

# -----------------------
# Right panel content (menu) if open
# -----------------------
if side_col is not None:
    with side_col:
        st.markdown('<div class="right-panel">', unsafe_allow_html=True)
        st.markdown("<div style='font-weight:700;margin-bottom:8px'>Menu Navigasi</div>", unsafe_allow_html=True)
        # Use Streamlit buttons to change page
        if st.button("🏠 Beranda", key="btn_home"):
            st.session_state.page = "home"
        if st.button("🍜 Pesan Menu", key="btn_pesan"):
            st.session_state.page = "pesan"
        if st.button("💳 Pembayaran", key="btn_bayar"):
            st.session_state.page = "bayar"
        if st.button("📄 Struk", key="btn_struk"):
            st.session_state.page = "struk"
        if st.button("ℹ️ Tentang", key="btn_tentang"):
            st.session_state.page = "tentang"
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("<div style='font-size:12px;opacity:0.9'>Mas Ragil • Aplikasi Kasir</div>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# -----------------------
# Data menu (same as original)
# -----------------------
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

# -----------------------
# Struk builder (same)
# -----------------------
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

# -----------------------
# Pages (home/pesan/bayar/struk/tentang)
# -----------------------
page = st.session_state.page

with main_col:
    if page == "home":
        st.header("Selamat Datang di Mie Ayam & Bakso Mas Ragil 🍜")
        st.write("Warung rumahan dengan cita rasa otentik. Pilih menu, hitung total, lalu bayar dan cetak struk.")
        st.markdown("---")
        st.subheader("Mulai Transaksi Cepat")
        colh1, colh2 = st.columns(2)
        with colh1:
            if st.button("➡️ Pesan Menu (langsung)", key="quick_pesan"):
                st.session_state.page = "pesan"
                st.experimental_rerun()
        with colh2:
            if st.button("➡️ Pembayaran (langsung)", key="quick_bayar"):
                st.session_state.page = "bayar"
                st.experimental_rerun()

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
                st.session_state.struk = build_struk(
                    st.session_state.nama_pelanggan,
                    st.session_state.pesanan,
                    sub_total,
                    diskon,
                    total_bayar,
                )
                st.success("Total dihitung. Lanjut ke Pembayaran.")
                if st.button("➡️ Lanjut ke Pembayaran"):
                    st.session_state.page = "bayar"
                    st.experimental_rerun()

    elif page == "bayar":
        st.header("💳 Pembayaran")
        if not st.session_state.sudah_dihitung:
            st.warning("Silakan hitung total di menu Pesan terlebih dahulu.")
            if st.button("➡️ Pergi ke Pesan"):
                st.session_state.page = "pesan"
                st.experimental_rerun()
        else:
            st.info(f"Total yang harus dibayar: Rp {st.session_state.total_bayar:,}")
            uang = st.number_input("Masukkan uang bayar:", min_value=0, step=1000, key="pay_input")
            if st.button("✅ Bayar Sekarang"):
                if uang < st.session_state.total_bayar:
                    st.error("Uang tidak cukup.")
                else:
                    kembalian = uang - st.session_state.total_bayar
                    sub_total = sum(st.session_state.pesanan.values()) if st.session_state.pesanan else 0
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
                    st.markdown(f'<div style="margin-top:12px;" class="nota">{st.session_state.struk.replace(" ", "&nbsp;")}</div>', unsafe_allow_html=True)
                    st.download_button("💾 Unduh Struk", st.session_state.struk, file_name="struk_mas_ragil.txt")

    elif page == "struk":
        st.header("📄 Struk Pembayaran")
        if st.session_state.struk:
            st.markdown(f'<div class="nota">{st.session_state.struk.replace(" ", "&nbsp;")}</div>', unsafe_allow_html=True)
            st.download_button("💾 Unduh Struk", st.session_state.struk, file_name="struk_mas_ragil.txt")
        else:
            st.info("Belum ada struk. Lakukan transaksi dulu.")

    elif page == "tentang":
        st.header("ℹ️ Tentang")
        st.write("""
        Aplikasi kasir sederhana untuk usaha Mie Ayam & Bakso Mas Ragil.
        - Responsive UI (mobile-friendly)
        - Navbar + tombol (≡) membuka panel kanan
        - Panel kanan tema gelap transparan (auto-close saat klik luar)
        - Struk pembayaran bisa ditampilkan & diunduh
        """)

# Footer
st.markdown("---")
st.caption("© Rosif Al Khikam — Kelompok 5 Boii")
