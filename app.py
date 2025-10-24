import streamlit as st
from datetime import datetime

# ===============================
# Page config
# ===============================
st.set_page_config(page_title="Kasir Mas Ragil", page_icon="🍜", layout="wide")

# ===============================
# Session state defaults
# ===============================
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

# ===============================
# CSS + UI
# ===============================
st.markdown("""
<style>
/* ===== NAVBAR ===== */
.topbar {
    background: linear-gradient(90deg,#c62828,#b71c1c);
    color: white;
    padding: 10px 16px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 2px 6px rgba(0,0,0,0.12);
    position: sticky;
    top: 0;
    z-index: 1000;
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

/* ===== OVERLAY ===== */
.overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0,0,0,0.5);
    display: none;
    z-index: 998;
}
.overlay.show {
    display: block;
}

/* ===== PANEL PUTIH KANAN ===== */
.side-panel {
    position: fixed;
    top: 0;
    right: -320px;
    width: 280px;
    height: 100%;
    background: rgba(255, 255, 255, 0.97);
    border-radius: 12px 0 0 12px;
    padding: 16px;
    transition: right 0.3s ease;
    z-index: 999;
    overflow:auto;
    box-shadow: -2px 2px 8px rgba(0,0,0,0.2);
}
.side-panel.open {
    right: 0;
}
.menu-item {
    display:block;
    padding:12px 16px;
    margin:6px 0;
    border-radius:8px;
    color:#c62828;
    font-weight:600;
    text-decoration:none;
    background:#f5f5f5;
    border:none;
    width:100%;
    text-align:left;
    transition: background 0.2s ease;
}
.menu-item:hover{
    background: rgba(198, 40, 40, 0.1);
}
.menu-item.active{
    background: rgba(198, 40, 40, 0.2);
}

/* ===== STRUK ===== */
.nota {
    background-color:#fffbea;
    padding:18px;
    border-radius:10px;
    border:1px solid #e6d9a7;
    font-family: "Courier New", monospace;
    white-space: pre;
    color:#222;
}

/* DARK MODE SUPPORT */
@media (prefers-color-scheme: dark) {
    .side-panel { background: rgba(20,20,20,0.97); color:white; }
    .menu-item { background:#222; color:#fff; }
    .menu-item:hover { background:#333; }
    .menu-item.active { background:#800000; }
}
</style>
""", unsafe_allow_html=True)

# ===============================
# TOPBAR
# ===============================
st.markdown(f"""
<div class="topbar">
    <button class="hamburger" onclick="toggleMenu()">≡</button>
    <div class="brand">🍜 Mie Ayam & Bakso — Mas Ragil</div>
</div>

<div id="overlay" class="overlay" onclick="closeMenu()"></div>
<div id="sidepanel" class="side-panel">
    <button class="menu-item {'active' if st.session_state.page=='home' else ''}" onclick="window.location.href='?page=home'">🏠 Beranda</button>
    <button class="menu-item {'active' if st.session_state.page=='pesan' else ''}" onclick="window.location.href='?page=pesan'">🍜 Pesan Menu</button>
    <button class="menu-item {'active' if st.session_state.page=='bayar' else ''}" onclick="window.location.href='?page=bayar'">💳 Pembayaran</button>
    <button class="menu-item {'active' if st.session_state.page=='struk' else ''}" onclick="window.location.href='?page=struk'">📄 Struk</button>
    <button class="menu-item {'active' if st.session_state.page=='tentang' else ''}" onclick="window.location.href='?page=tentang'">ℹ️ Tentang</button>
</div>

<script>
function toggleMenu() {{
  const panel = document.getElementById("sidepanel");
  const overlay = document.getElementById("overlay");
  panel.classList.toggle("open");
  overlay.classList.toggle("show");
}}
function closeMenu() {{
  document.getElementById("sidepanel").classList.remove("open");
  document.getElementById("overlay").classList.remove("show");
}}
</script>
""", unsafe_allow_html=True)

# ===============================
# HANDLE PAGE PARAMETER
# ===============================
query_params = st.query_params
if "page" in query_params:
    st.session_state.page = query_params["page"][0]

# ===============================
# DATA MENU
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
# STRUK BUILDER
# ===============================
def build_struk(nama, pesanan_dict, total_before, diskon, total_bayar, uang_bayar=None, kembalian=None):
    t = "===== STRUK PEMBAYARAN =====\\n"
    t += f"Tanggal : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\n"
    t += f"Nama    : {nama}\\n"
    t += "-----------------------------\\n"
    for it, subtotal in pesanan_dict.items():
        t += f"{it:<20} Rp {subtotal:,}\\n"
    t += "-----------------------------\\n"
    t += f"Sub Total           : Rp {total_before:,}\\n"
    t += f"Diskon              : Rp {diskon:,}\\n"
    t += f"Total Bayar         : Rp {total_bayar:,}\\n"
    if uang_bayar is not None:
        t += f"Uang Diterima       : Rp {uang_bayar:,}\\n"
        t += f"Kembalian           : Rp {kembalian:,}\\n"
    t += "============================\\n"
    t += "Terima kasih! Salam, Mas Ragil\\n"
    return t

# ===============================
# HALAMAN
# ===============================
page = st.session_state.page

if page == "home":
    st.header("Selamat Datang di Mie Ayam & Bakso Mas Ragil 🍜")
    st.write("Warung rumahan dengan cita rasa otentik. Pilih menu, hitung total, lalu bayar dan cetak struk.")
    st.image("https://images.unsplash.com/photo-1604908177522-3f9a9b2f4d9f?q=80&w=1200&auto=format&fit=crop&ixlib=rb-4.0.3", caption="Mie Ayam & Bakso — nikmati hangatnya!", use_container_width=True)

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
                st.markdown(f'<div class="nota">{st.session_state.struk.replace(" ", "&nbsp;")}</div>', unsafe_allow_html=True)
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
    - Klik luar panel = auto close
    - Struk bisa ditampilkan & diunduh
    """)

st.markdown("---")
st.caption("© Rosif Al Khikam — Kelompok 5 Boii")
 
