import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import qrcode
from io import BytesIO

st.set_page_config(page_title="Mie Ayam Bakso Ragil", layout="wide")

# =============================== STORAGE =====================================
if "checkout" not in st.session_state:
    st.session_state.checkout = []
if "sales" not in st.session_state:
    st.session_state.sales = []
if "kasir" not in st.session_state:
    st.session_state.kasir = "Kasir Ragil"
if "buyer" not in st.session_state:
    st.session_state.buyer = ""

# =============================== MENU DATA ===================================
menu_list = [
    {"nama": "Mie Ayam", "harga": 15000},
    {"nama": "Bakso", "harga": 18000},
    {"nama": "Mie Ayam Bakso", "harga": 20000},
    {"nama": "Es Teh", "harga": 5000},
]

# ===================== NAVIGATION =====================
page = st.sidebar.radio("Menu", ["Order", "Pembayaran", "Admin"])

# =============================== ORDER PAGE =================================
if page == "Order":
    st.title("🍜 Mie Ayam Bakso Ragil")
    name = st.text_input("Nama Pembeli:", st.session_state.buyer)
    st.session_state.buyer = name

    for item in menu_list:
        qty = st.number_input(f"{item['nama']} (Rp{item['harga']:,})", 0, 50)
        if qty > 0:
            st.session_state.checkout.append({
                "nama": item["nama"],
                "harga": item["harga"],
                "jumlah": qty
            })

    if st.button("Tambahkan Ke Checkout"):
        st.success("✅ Ditambahkan!")

    st.write("### Keranjang")
    st.write(pd.DataFrame(st.session_state.checkout))

# ============================== PEMBAYARAN PAGE =============================
elif page == "Pembayaran":
    st.title("💳 Pembayaran")

    checkout = st.session_state.checkout
    if not checkout:
        st.info("Belum ada pesanan.")
    else:
        df = pd.DataFrame(checkout)
        df["Total"] = df["harga"] * df["jumlah"]
        st.table(df)

        total = df["Total"].sum()
        st.subheader(f"Total Bayar: **Rp{total:,}**")

        tunai = st.number_input("Tunai", 0)
        kembali = tunai - total

        if tunai > 0:
            st.write(f"Kembalian: **Rp{kembali:,}**")

        cashier = st.text_input("Nama Kasir", st.session_state.kasir)
        st.session_state.kasir = cashier

        if st.button("Simpan & Cetak Struk"):
            # Waktu WIB
            tz = pytz.timezone("Asia/Jakarta")
            waktu = datetime.now(tz)
            tanggal = waktu.strftime("%d-%m-%Y")
            jam = waktu.strftime("%H:%M:%S")

            # Simpan transaksi
            st.session_state.sales.append({
                "date": tanggal,
                "time": jam,
                "buyer": st.session_state.buyer,
                "kasir": cashier,
                "total": total
            })

            # ===== STRUK =====
            struk = f"""
PT. SUMBER ALFARIA TRIJAYA, TBK
MELIA WALK
JL. MH. THAMRIN NO.9, CIKOKOL, TANGERANG
NPWP: 01.336.238.9-054.000
---------------------------------------
            BUKTI PEMBELIAN
---------------------------------------
Tanggal: {tanggal}
Jam    : {jam} WIB
Kasir  : {cashier}
Pembeli: {st.session_state.buyer}

---------------------------------------
Item                Qty   Total
"""

            for item in checkout:
                struk += f"{item['nama']:<18} {item['jumlah']:<3} Rp{item['harga']*item['jumlah']:,}\n"

            struk += f"""
---------------------------------------
TOTAL BAYAR : Rp{total:,}
TUNAI       : Rp{tunai:,}
KEMBALI     : Rp{kembali:,}
---------------------------------------
Terima kasih!
Simpan struk ini sebagai bukti resmi
---------------------------------------
"""

            st.text(struk)

            # ========== QR ==============
            qr = qrcode.make("Hai ini hikam")
            buf = BytesIO()
            qr.save(buf)
            st.image(buf.getvalue(), width=180)

            # Download file
            st.download_button("📥 Download Struk", struk, "struk.txt")

            # Javascript Auto Print Browser
            st.markdown(
                """<script>window.print()</script>""",
                unsafe_allow_html=True
            )

            st.success("✅ Struk ditampilkan & siap dicetak!")

            st.session_state.checkout = []

# =============================== ADMIN PAGE ================================
elif page == "Admin":
    st.title("⚙️ Admin Panel")

    st.write("### Data Penjualan")
    df = pd.DataFrame(st.session_state.sales)
    st.table(df)

    if st.button("Hapus Semua Transaksi"):
        st.session_state.sales = []
        st.success("✅ Semua data terhapus")
