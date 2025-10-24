# app.py
import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime

# ===============================
# Page config
# ===============================
st.set_page_config(page_title="Kasir Mas Ragil", page_icon="🍜", layout="wide")

# ===============================
# Session state defaults (preserve original kasir logic)
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
# App-level CSS (indigo dark theme + spacing so content starts below navbar iframe)
# ===============================
st.markdown(
    """
    <style>
    /* body background / main theme */
    .stApp {
        background: linear-gradient(180deg,#0b1020,#0e1430);
        color: #e6eef8;
        min-height: 100vh;
    }
    /* make sure top content sits below the navbar component area */
    .app-top-padding {
        padding-top: 140px;  /* leave space for the navbar component area */
    }

    /* Nota / struk style (same as original but tuned for dark bg) */
    .nota {
        background-color:#1f2330;
        padding:18px;
        border-radius:10px;
        border:1px solid #2f3340;
        font-family: "Courier New", monospace;
        white-space: pre;
        color:#e6eef8;
    }

    /* Tweak Streamlit container width (class names may vary by Streamlit version) */
    .css-1d391kg {  /* fallback — if not matching, it's harmless */
        max-width: 1100px;
    }

    /* small visual tweaks for forms */
    .stTextInput>div>div>input, .stNumberInput>div>div>input {
        background: rgba(255,255,255,0.03);
        color: #e6eef8;
    }
    .stButton>button {
        background: linear-gradient(90deg,#c62828,#b71c1c);
        color: white;
        border-radius: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ===============================
# NAVBAR + SIDE PANEL (dark indigo) INSIDE COMPONENT
# - Panel includes menu items and JS to set active class reading ?page=
# ===============================
components.html(
    """
    <!doctype html>
    <html>
    <head>
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <style>
        body { margin:0; background:transparent; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial; }
        .topbar {
          height: 64px;
          display:flex;
          align-items:center;
          gap:16px;
          padding:12px 18px;
          background: linear-gradient(90deg,#b71c1c,#9c2a2a);
          border-radius:12px;
          box-shadow: 0 8px 30px rgba(0,0,0,0.35);
          color:white;
        }
        .hambutton {
          background: transparent;
          border:none;
          color: white;
          font-size:22px;
          cursor:pointer;
          padding:6px 10px;
          border-radius:8px;
        }
        .brand {
          font-weight:800;
          font-size:16px;
          color: #fff;
          text-align:center;
          flex:1;
        }

        .overlay {
          position: fixed;
          inset: 0;
          background: rgba(0,0,0,0.45);
          display:none;
          z-index: 9990;
        }
        .overlay.show { display:block; }

        .side-panel {
          position: fixed;
          top: 10px;
          right: -360px;
          width: 320px;
          max-width: 85%;
          height: calc(100% - 20px);
          z-index: 9991;
          transition: right 0.32s cubic-bezier(.2,.9,.2,1);
          padding: 18px;
          box-sizing: border-box;
          border-radius: 12px;
          backdrop-filter: blur(6px);
          background: linear-gradient(180deg, rgba(8,10,16,0.94), rgba(12,14,22,0.90));
          color: #fff;
          box-shadow: -8px 0 32px rgba(0,0,0,0.6);
          overflow-y: auto;
        }
        .side-panel.open { right: 10px; }

        .menu-item {
          display:block;
          width:100%;
          text-align:left;
          padding:11px 14px;
          margin:8px 0;
          border-radius:10px;
          background: rgba(255,255,255,0.03);
          color: #fff;
          font-weight:600;
          border:none;
          cursor:pointer;
        }
        .menu-item:hover { background: rgba(255,255,255,0.06); }
        .menu-item.active { background: rgba(255,255,255,0.09); color: #fff; }

        @media (max-width:600px) {
          .side-panel { width:86%; right:-90%; }
          .side-panel.open { right: 6%; }
        }
      </style>
    </head>
    <body>
      <div style="padding:12px;">
        <div class="topbar" role="banner">
          <button class="hambutton" aria-label="Toggle menu" onclick="toggleMenu()">☰</button>
          <div class="brand">🍜 Mie Ayam & Bakso — Mas Ragil</div>
        </div>
      </div>

      <div id="overlay" class="overlay" onclick="closeMenu()"></div>

      <nav id="sidepanel" class="side-panel" aria-hidden="true">
        <div style="font-weight:700;margin-bottom:8px;color:#f1f1f1">Menu Navigasi</div>
        <button class="menu-item" data-page="home" onclick="navigateTop('home')">🏠 Beranda</button>
        <button class="menu-item" data-page="pesan" onclick="navigateTop('pesan')">🍜 Pesan Menu</button>
        <button class="menu-item" data-page="bayar" onclick="navigateTop('bayar')">💳 Pembayaran</button>
        <button class="menu-item" data-page="struk" onclick="navigateTop('struk')">📄 Struk</button>
        <button class="menu-item" data-page="tentang" onclick="navigateTop('tentang')">ℹ️ Tentang</button>
        <hr style="border:none;border-top:1px solid rgba(255,255,255,0.06);margin:12px 0;">
        <div style="font-size:13px;opacity:0.9">Mas Ragil • Aplikasi Kasir</div>
      </nav>

      <script>
        function toggleMenu(){
          const panel = document.getElementById('sidepanel');
          const overlay = document.getElementById('overlay');
          if(panel.classList.contains('open')) {
            panel.classList.remove('open');
            overlay.classList.remove('show');
            panel.setAttribute('aria-hidden','true');
          } else {
            panel.classList.add('open');
            overlay.classList.add('show');
            panel.setAttribute('aria-hidden','false');
            // set active on load (in case page param present)
            setActiveByQuery();
          }
        }
        function closeMenu(){
          const panel = document.getElementById('sidepanel');
          const overlay = document.getElementById('overlay');
          panel.classList.remove('open');
          overlay.classList.remove('show');
          panel.setAttribute('aria-hidden','true');
        }

        function navigateTop(pageKey){
          try {
            const topUrl = new URL(window.top.location.href);
            topUrl.searchParams.set('page', pageKey);
            window.top.location.href = topUrl.toString();
          } catch(e) {
            const cur = new URL(window.location.href);
            cur.searchParams.set('page', pageKey);
            window.location.href = cur.toString();
          }
          closeMenu();
        }

        function setActiveByQuery(){
          // read page param from top if possible, else from current
          let search = "";
          try { search = window.top.location.search; } catch(e) { search = window.location.search; }
          const params = new URLSearchParams(search);
          const page = params.get('page') || 'home';
          const buttons = document.querySelectorAll('.menu-item[data-page]');
          buttons.forEach(b => {
            if(b.getAttribute('data-page') === page) b.classList.add('active');
            else b.classList.remove('active');
          });
        }

        // run on load to set active menu
        setActiveByQuery();
      </script>
    </body>
    </html>
    """,
    height=220,
    scrolling=True,
)

# ===============================
# Read page param and set session page
# ===============================
q = st.query_params
if "page" in q:
    st.session_state.page = q["page"][0]

# ===============================
# DATA MENU (original)
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
# HELPER STRUK (original)
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
# PAGE / KASIR CONTENT
# - Keep content below the navbar iframe by adding padding div
# ===============================
st.markdown('<div class="app-top-padding"></div>', unsafe_allow_html=True)

page = st.session_state.page

# ---------- HOME: show welcome + quick summary + option to go to Pesan ----------
if page == "home":
    st.header("Selamat Datang di Mie Ayam & Bakso Mas Ragil 🍜")
    st.write("Warung rumahan dengan cita rasa otentik. Pilih menu, hitung total, lalu bayar dan cetak struk.")

    st.markdown("---")
    st.subheader("Mulai Transaksi Cepat")
    st.write("Klik tombol di bawah ini untuk langsung menuju halaman pemesanan atau pembayaran.")
    colh1, colh2 = st.columns([1,1])
    with colh1:
        if st.button("➡️ Pesan Menu"):
            st.session_state.page = "pesan"
            st.experimental_set_query_params(page="pesan")
            st.experimental_rerun()
    with colh2:
        if st.button("➡️ Pembayaran"):
            st.session_state.page = "bayar"
            st.experimental_set_query_params(page="bayar")
            st.experimental_rerun()

# ---------- PESAN: pilih menu, simpan ke session_state.pesanan ----------
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
            # suggest to go to pembayaran
            if st.button("➡️ Lanjut ke Pembayaran"):
                st.session_state.page = "bayar"
                st.experimental_set_query_params(page="bayar")
                st.experimental_rerun()

# ---------- BAYAR: tampilkan total & proses pembayaran ----------
elif page == "bayar":
    st.header("💳 Pembayaran")
    if not st.session_state.sudah_dihitung:
        st.warning("Silakan hitung total di menu Pesan terlebih dahulu.")
        # quick link to Pesan
        if st.button("➡️ Pergi ke Pesan"):
            st.session_state.page = "pesan"
            st.experimental_set_query_params(page="pesan")
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
                # Reset order after payment (optional) - comment out if you want to keep
                # st.session_state.pesanan = {}
                # st.session_state.sudah_dihitung = False
                # st.session_state.total_bayar = 0

# ---------- STRUK: tampilkan struk yg terakhir dibuat ----------
elif page == "struk":
    st.header("📄 Struk Pembayaran")
    if st.session_state.struk:
        st.markdown(f'<div class="nota">{st.session_state.struk.replace(" ", "&nbsp;")}</div>', unsafe_allow_html=True)
        st.download_button("💾 Unduh Struk", st.session_state.struk, file_name="struk_mas_ragil.txt")
    else:
        st.info("Belum ada struk. Lakukan transaksi dulu.")

# ---------- TENTANG ----------
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
