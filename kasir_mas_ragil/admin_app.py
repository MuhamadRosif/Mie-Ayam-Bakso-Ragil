import streamlit as st
import json, os, pandas as pd

MENU_FILE = "menu.json"
CHECKOUT_FILE = "checkout.json"

# ======================
# Load & Save Functions
# ======================
def load_json(file, default):
    return json.load(open(file)) if os.path.exists(file) else default

def save_json(file, data):
    json.dump(data, open(file, "w"), indent=2)

menu_data = load_json(MENU_FILE, {})
checkout_data = load_json(CHECKOUT_FILE, [])

# ======================
# UI Theme (Premium)
# ======================
st.set_page_config(page_title="Kasir Restoran", layout="wide")

st.markdown("""
<style>

body {
    background: #f8f4ea;
}

.block-container {
    padding-top: 2rem;
}

.card {
    padding: 18px;
    border-radius: 15px;
    background: white;
    box-shadow: 0 3px 12px rgba(0,0,0,0.08);
    margin-bottom: 10px;
}

.menu-card {
    padding: 15px;
    border-radius: 15px;
    background: #fffdf5;
    border: 1px solid #e8decf;
    box-shadow: 0 4px 10px rgba(0,0,0,0.03);
    transition: 0.2s;
    cursor: pointer;
}

.menu-card:hover {
    transform: scale(1.02);
    background: #fff7e6;
}

h1, h2, h3 {
    font-weight: 700;
    color: #5a3825;
}

.add-btn {
    background: #e4b660;
    color: white;
    padding: 8px 14px;
    border-radius: 8px;
    border: none;
}

.add-btn:hover {
    background: #d09c45;
}

</style>
""", unsafe_allow_html=True)

# ======================
# Login Page
# ======================
def login_page():
    st.title("🔐 Login Kasir Restoran")

    st.write("Masukkan akun untuk masuk:")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login ✅", use_container_width=True):
        if username == "admin" and password == "12345":   # << GANTI DISINI
            st.session_state.logged = True
            st.success("Login berhasil 🎉")
            st.rerun()
        else:
            st.error("Username / Password salah!")

if "logged" not in st.session_state:
    st.session_state.logged = False

if not st.session_state.logged:
    login_page()
    st.stop()

# ======================
# Dashboard Header
# ======================
col1, col2 = st.columns([5,1])
with col1:
    st.title("🍜 Kasir Mie Ayam Bakso Ragil - Premium UI")
with col2:
    if st.button("Logout", type="primary"):
        st.session_state.logged = False
        st.rerun()

# ======================
# Content Layout
# ======================
menu_tab, cart_tab = st.columns([3.5,1.5])

with menu_tab:
    st.subheader("📋 Menu Makanan & Minuman")

    for kategori, items in menu_data.items():
        st.markdown(f"### 🥘 {kategori.title()}")

        cols = st.columns(2)
        i = 0
        for nama, harga in items.items():
            with cols[i % 2]:
                st.markdown(f"""
                <div class="menu-card">
                    <h4>{nama}</h4>
                    <p>Rp {harga:,}</p>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"Tambah {nama}", key=nama):
                    checkout_data.append({"nama": nama, "harga": harga, "jumlah": 1})
                    save_json(CHECKOUT_FILE, checkout_data)
                    st.rerun()
            i += 1

with cart_tab:
    st.subheader("🛒 Keranjang")
    if not checkout_data:
        st.info("Belum ada pesanan")
    else:
        total = 0
        for item in checkout_data:
            total += item["harga"] * item["jumlah"]
            st.write(f"**{item['nama']}** x{item['jumlah']} - Rp {item['harga']*item['jumlah']:,}")

        st.markdown(f"### Total: **Rp {total:,}**")

        nama = st.text_input("Nama Pembeli")

        if st.button("✅ Bayar & Cetak Struk"):
            struk = f"Struk - {nama or 'Pelanggan'}\n" + "="*30 + "\n"
            for item in checkout_data:
                struk += f"{item['nama']} x{item['jumlah']} = Rp {item['harga']*item['jumlah']:,}\n"
            struk += "="*30 + f"\nTotal: Rp {total:,}"

            filename = "struk.txt"
            open(filename, "w").write(struk)
            st.download_button("⬇ Download Struk", open(filename, "rb"), filename)

            checkout_data = []
            save_json(CHECKOUT_FILE, checkout_data)
            st.success("Pembayaran berhasil ✅")
            st.rerun()

        if st.button("🗑️ Hapus semua"):
            checkout_data = []
            save_json(CHECKOUT_FILE, checkout_data)
            st.rerun()
