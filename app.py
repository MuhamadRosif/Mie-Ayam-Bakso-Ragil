import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime

st.set_page_config(page_title="Kasir Mas Ragil", page_icon="🍜", layout="wide")

# ====== STYLING ======
st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg,#0b1020,#1a1a3d);
    color: #f0f0f0;
}
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

# ====== NAVBAR + PANEL ======
components.html("""
<html>
<head>
<style>
body {margin:0; background:transparent;}
.navbar {
    position:fixed; top:0; left:0; right:0;
    height:60px; background:#b71c1c; color:white;
    display:flex; align-items:center; padding:0 15px;
    font-weight:bold; font-family:sans-serif;
    z-index:100;
}
.menu-btn {
    background:none; border:none; color:white; font-size:24px; cursor:pointer;
}
.overlay {
    position:fixed; inset:0; background:rgba(0,0,0,0.4); display:none; z-index:90;
}
.sidepanel {
    position:fixed; top:0; right:-260px; width:250px; height:100%;
    background:rgba(20,20,30,0.97); color:white; padding:20px;
    transition:right 0.3s ease; z-index:99;
    backdrop-filter:blur(6px);
}
.sidepanel.open { right:0; }
.menu-item {
    display:block; width:100%; margin:10px 0; padding:10px;
    border:none; border-radius:8px; background:rgba(255,255,255,0.08);
    color:white; text-align:left; font-weight:600; cursor:pointer;
}
.menu-item:hover {background:rgba(255,255,255,0.15);}
</style>
</head>
<body>
<div class="navbar">
  <button class="menu-btn" onclick="togglePanel()">☰</button>
  <div style="flex:1;text-align:center;">🍜 Mie Ayam & Bakso — Mas Ragil</div>
</div>

<div id="overlay" class="overlay" onclick="closePanel()"></div>
<div id="panel" class="sidepanel">
  <button class="menu-item" onclick="navigateTop('home')">🏠 Beranda</button>
  <button class="menu-item" onclick="navigateTop('tentang')">ℹ️ Tentang</button>
</div>

<script>
function togglePanel(){
  const p=document.getElementById("panel");
  const o=document.getElementById("overlay");
  p.classList.toggle("open");
  o.style.display = p.classList.contains("open") ? "block":"none";
}
function closePanel(){
  document.getElementById("panel").classList.remove("open");
  document.getElementById("overlay").style.display="none";
}
function navigateTop(page){
  const u=new URL(window.top.location.href);
  u.searchParams.set("page",page);
  window.top.location.href=u.toString();
}
</script>
</body>
</html>
""", height=80)

# ====== QUERY PARAM ======
page = st.query_params.get("page", ["home"])[0]

# ====== DATA MENU ======
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

# ====== STRUK FUNCTION ======
def buat_struk(nama, pesanan, total, diskon, total_bayar, uang=None, kembali=None):
    s = "===== STRUK PEMBAYARAN =====\n"
    s += f"Tanggal : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    s += f"Nama    : {nama}\n"
    s += "-----------------------------\n"
    for i, sub in pesanan.items():
        s += f"{i:<20} Rp {sub:,}\n"
    s += "-----------------------------\n"
    s += f"Subtotal   : Rp {total:,}\n"
    s += f"Diskon     : Rp {diskon:,}\n"
    s += f"Total Bayar: Rp {total_bayar:,}\n"
    if uang: 
        s += f"Uang Bayar : Rp {uang:,}\nKembalian  : Rp {kembali:,}\n"
    s += "=============================\nTerima kasih! Salam, Mas Ragil."
    return s

# ====== PAGE HOME (TAMPILAN KASIR) ======
if page == "home":
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.title("Selamat Datang di Mie Ayam & Bakso Mas Ragil 🍜")
    st.write("Warung rumahan dengan cita rasa otentik. Pilih menu, hitung total, lalu bayar dan cetak struk.")
    
    st.subheader("🧾 Pemesanan")
    nama = st.text_input("Nama Pelanggan")
    pesanan = {}

    c1, c2 = st.columns(2)
    with c1:
        st.write("**Makanan**")
        for m, h in menu_makanan.items():
            j = st.number_input(f"{m} (Rp {h:,})", 0, 20, 0, key=m)
            if j > 0:
                pesanan[m] = h*j
    with c2:
        st.write("**Minuman**")
        for m, h in menu_minuman.items():
            j = st.number_input(f"{m} (Rp {h:,})", 0, 20, 0, key=m)
            if j > 0:
                pesanan[m] = h*j

    if st.button("💰 Hitung Total"):
        if not nama:
            st.warning("Masukkan nama pelanggan!")
        elif not pesanan:
            st.warning("Belum ada pesanan.")
        else:
            subtotal = sum(pesanan.values())
            diskon = int(0.1 * subtotal) if subtotal >= 50000 else 0
            total_bayar = subtotal - diskon
            st.success(f"Total: Rp {total_bayar:,}")

            uang = st.number_input("Masukkan uang bayar", min_value=0, step=1000)
            if uang:
                if uang < total_bayar:
                    st.error("Uang tidak cukup!")
                else:
                    kembali = uang - total_bayar
                    struk = buat_struk(nama, pesanan, subtotal, diskon, total_bayar, uang, kembali)
                    st.markdown(f"<div class='nota'>{struk}</div>", unsafe_allow_html=True)
                    st.download_button("💾 Unduh Struk", struk, file_name="struk_masragil.txt")

elif page == "tentang":
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.header("ℹ️ Tentang Aplikasi")
    st.write("""
    Aplikasi kasir Mie Ayam & Bakso Mas Ragil dibuat untuk membantu pencatatan pesanan dan pembayaran.
    
    Fitur:
    - Pesan menu makanan & minuman  
    - Hitung otomatis + diskon  
    - Cetak & unduh struk  
    - Tampilan gelap elegan dengan navbar interaktif  
    """)

st.markdown("<br><hr><center>© Rosif Al Khikam — Kelompok 5 Boii</center>", unsafe_allow_html=True)
