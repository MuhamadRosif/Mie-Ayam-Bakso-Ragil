import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Warung Mas Ragil", page_icon="🍜", layout="wide")

# ---------------- Session State ----------------
if "cart" not in st.session_state:
    st.session_state.cart = []

if "buyers" not in st.session_state:
    st.session_state.buyers = {}

if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

# ---------------- Sidebar Admin ----------------
st.sidebar.title("Admin Panel")

if not st.session_state.admin_logged_in:
    with st.sidebar.expander("🔐 Admin Login", expanded=False):
        username = st.text_input("Username", key="admin_user")
        password = st.text_input("Password", type="password", key="admin_pass")
        
        if st.button("Masuk Admin", key="btn_login"):
            if username == "admin" and password == "123":
                st.session_state.admin_logged_in = True
                st.success("✅ Login admin berhasil!")
                st.rerun()
            else:
                st.error("❌ Username / Password salah!")

# Setelah login → tampilkan menu admin
if st.session_state.admin_logged_in:
    admin_menu = st.sidebar.radio(
        "Menu Admin", 
        ["Data Menu", "Data Pesanan", "Pembayaran", "Laporan", "Pengaturan Toko"]
    )

    if st.sidebar.button("🚪 Logout"):
        st.session_state.admin_logged_in = False
        st.sidebar.success("✅ Logout berhasil")
        st.rerun()
else:
    admin_menu = None

# ---------------- Customer Page ----------------
st.title("🍜 Warung Mie Ayam & Bakso Mas Ragil")

st.subheader("📋 Menu")

menu = {
    "Makanan": {
        "Mie Ayam": 15000,
        "Bakso": 15000,
        "Mie Ayam Bakso": 20000
    },
    "Minuman": {
        "Teh Manis": 5000,
        "Jeruk": 6000,
        "Es Campur": 10000
    }
}

# Nama pembeli wajib
buyer_name = st.text_input("👤 Masukkan Nama Pembeli (wajib)")

for category, items in menu.items():
    st.markdown(f"### 🍽️ {category}")
    cols = st.columns(3)
    for i, (item, price) in enumerate(items.items()):
        with cols[i % 3]:
            st.write(f"**{item}** - Rp {price:,}".replace(",", "."))
            if st.button(f"Tambah {item}", key=item):
                if buyer_name.strip() == "":
                    st.error("⚠️ Masukkan nama pembeli dulu!")
                else:
                    st.session_state.cart.append({"name": buyer_name, "item": item, "price": price})

# ---------------- Keranjang ----------------
st.subheader("🛒 Keranjang")

if not st.session_state.cart:
    st.info("Belum ada pesanan")
else:
    df = pd.DataFrame(st.session_state.cart)
    grouped = df.groupby("item").agg({"price":"sum","name":"count"}).rename(columns={"name":"qty"})
    grouped["subtotal"] = grouped["price"]
    st.table(grouped[["qty","subtotal"]])

    subtotal = sum(x["price"] for x in st.session_state.cart)
    ppn = int(subtotal * 0.11)
    diskon = int(subtotal * 0.02)
    total = subtotal + ppn - diskon

    st.write(f"**Subtotal:** Rp {subtotal:,}".replace(",", "."))
    st.write(f"**PPN (11%):** Rp {ppn:,}".replace(",", "."))
    st.write(f"**Diskon (2%):** -Rp {diskon:,}".replace(",", "."))
    st.write(f"**Total:** Rp {total:,}".replace(",", "."))

    cash = st.number_input("💵 Tunai", min_value=0, step=1000)
    if cash > 0:
        change = cash - total
        st.write(f"**Kembalian:** Rp {change:,}".replace(",", "."))

    if st.button("✅ Bayar & Cetak Struk"):
        if cash < total:
            st.error("⚠️ Uang kurang!")
        else:
            st.success("✅ Pembayaran sukses!")

            # tampil struk
            st.write("---")
            st.text("        🍜 WARUNG MAS RAGIL")
            st.text("================================")
            st.text(f"Nama: {buyer_name}")
            st.text(f"Tanggal: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")
            st.text("--------------------------------")
            for row in st.session_state.cart:
                st.text(f"{row['item']} - Rp {row['price']:,}".replace(",", "."))
            st.text("--------------------------------")
            st.text(f"Subtotal         Rp {subtotal:,}".replace(",", "."))
            st.text(f"PPN 11%          Rp {ppn:,}".replace(",", "."))
            st.text(f"Diskon 2%       -Rp {diskon:,}".replace(",", "."))
            st.text(f"TOTAL            Rp {total:,}".replace(",", "."))
            st.text(f"Tunai            Rp {cash:,}".replace(",", "."))
            st.text(f"Kembalian        Rp {change:,}".replace(",", "."))
            st.text("--------------------------------")
            st.text("Terima kasih 🙏😊")

            st.session_state.cart = []

