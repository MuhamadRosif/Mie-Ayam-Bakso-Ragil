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
# App-level CSS (indigo dark theme + spacing so content starts below navbar)
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
    /* make sure top content sits below the navbar iframe */
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

    /* Tweak Streamlit default container widths to look nicer */
    .css-1d391kg {  /* container style class may differ by Streamlit version */
        max-width: 1100px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ===============================
# NAVBAR + SIDE PANEL (dark indigo) INSIDE COMPONENT
# - placed at top area (iframe) so main content is below it
# - uses navigateTop(page) to add ?page=... and reload
# ===============================
components.html(
    """
    <!DOCTYPE html>
    <html>
    <head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
      :root { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial; }
      body { margin:0; padding:0; background:transparent; color:inherit; }

      /* TOPBAR (fixed within this iframe area) */
      .topbar {
        height: 64px;
        display:flex;
        align-items:center;
        gap:16px;
        padding:12px 18px;
        background: linear-gradient(90deg,#9c27b0,#3f51b5); /* indigo-ish header behind red bar */
        border-radius:12px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.4);
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

      /* overlay inside this iframe (not covering entire parent page, but covers iframe area) */
      .overlay {
        position: fixed;
        inset: 0;
        background: rgba(0,0,0,0.45);
        display: none;
        z-index: 60;
      }
      .overlay.show { display:block; }

      /* side-panel (dark transparent theme) */
      .side-panel {
        position: fixed;
        top: 10px;
        right: -360px;
        width: 320px;
        max-width: 85%;
        height: calc(100% - 20px);
        z-index: 70;
        transition: right 0.32s cubic-bezier(.2,.9,.2,1);
        padding: 18px;
        box-sizing: border-box;
        border-radius: 12px;
        backdrop-filter: blur(6px);
        background: linear-gradient(180deg, rgba(6,8,20,0.92), rgba(12,14,30,0.88));
        color: #fff;
        box-shadow: -8px 0 32px rgba(0,0,0,0.6);
        overflow-y: auto;
      }
      .side-panel.open { right: 10px; } /* slightly inset so it looks like panel on edge */

      /* menu items */
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
      .menu-item.active { background: rgba(255,255,255,0.09); }

      @media (max-width:600px) {
        .side-panel { width:86%; right: -90%; }
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
        <button class="menu-item" onclick="navigateTop('home')">🏠 Beranda</button>
        <button class="menu-item" onclick="navigateTop('pesan')">🍜 Pesan Menu</button>
        <button class="menu-item" onclick="navigateTop('bayar')">💳 Pembayaran</button>
        <button class="menu-item" onclick="navigateTop('struk')">📄 Struk</button>
        <button class="menu-item" onclick="navigateTop('tentang')">ℹ️ Tentang</button>
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
      }
    }
    function closeMenu(){
      const panel = document.getElementById('sidepanel');
      const overlay = document.getElementById('overlay');
      panel.classList.remove('open');
      overlay.classList.remove('show');
      panel.setAttribute('aria-hidden','true');
    }

    /* navigateTop: set ?page=... on the top (or fallback to current) */
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
      // close panel
      closeMenu();
    }
    </script>
    </body>
    </html>
    """,
    height=220,  # keep header+panel control visible but leave space for main content below
    scrolling=True,
)

# ===============================
# Read page param
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
# Helper struk (original)
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
# - We put an extra top padding container so content appears below the navbar iframe
# ===============================
st.markdown('<div class="app-top-padding"></div>', unsafe_allow_html=True)

page = st.session_state.page

if page == "home":
    st.header("Selamat Datang di Mie Ayam & Bakso Mas Ragil 🍜")
    st.write("Warung rumahan dengan cita rasa otentik. Pilih menu, hitung total, lalu bayar dan cetak struk.")
    st.image(
        "https://images.unsplash.com/photo-1604908177522-3f9a9b2f4d9f?q=80&w=1200&auto=format&fit=crop&ixlib=rb-4.0.3",
        caption="Mie Ayam & Bakso — nikmati hangatnya!",
        use_container_width=True,
    )

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

st.markdown("---")
st.caption("© Rosif Al Khikam — Kelompok 5 Boii")
