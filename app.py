import json, os, streamlit as st
import pandas as pd

MENU_FILE = "menu.json"
CHECKOUT_FILE = "checkout.json"

# ---------------------- Helper Functions ----------------------
def load_json(file):
    if os.path.exists(file):
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {} if file == MENU_FILE else []

def save_json(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

menu_data = load_json(MENU_FILE)
checkout_data = load_json(CHECKOUT_FILE)

# ---------------------- Streamlit Setup ----------------------
st.set_page_config(page_title="Mie Ayam Bakso Mas Ragil", page_icon="🍜", layout="centered")

st.markdown("""
<style>
body {
    background: url('https://images.unsplash.com/photo-1606755962773-0e2d7efc4b5b') no-repeat center center fixed;
    background-size: cover;
    font-family: 'Poppins', sans-serif;
}
.overlay {background: rgba(0,0,0,0.6); position:fixed; top:0; left:0; width:100%; height:100%; z-index:0;}
.login-card {
    position:relative; z-index:1; max-width:390px; margin:5rem auto; padding:2.5rem;
    background:rgba(255,183,77,0.18); backdrop-filter:blur(14px); border-radius:25px;
    box-shadow:0 0 25px rgba(255,150,0,0.3); text-align:center; color:#fff;
}
h2 {color:#ffcc00; text-shadow:0 0 15px rgba(255,200,50,0.6);}
.stButton>button {
    width:100%; height:45px; border-radius:12px; border:none;
    background:linear-gradient(270deg,#ff6b00,#ffb300); font-weight:700; cursor:pointer;
}
</style>
""", unsafe_allow_html=True)

# ---------------------- Login System ----------------------
if "role" not in st.session_state: st.session_state.role = None

def login_page():
    st.markdown("<div class='overlay'></div>", unsafe_allow_html=True)
    st.markdown("<div class='login-card'>", unsafe_allow_html=True)

    st.markdown("<h2>Mie Ayam Bakso Mas Ragil 🍜</h2>", unsafe_allow_html=True)

    role = st.selectbox("Masuk sebagai", ["Pelanggan", "Admin"])
    user = st.text_input("Username")
    pw = st.text_input("Password", type="password")

    if st.button("MASUK"):
        if role == "Admin" and user=="admin" and pw=="123":
            st.session_state.role = "admin"; st.rerun()
        elif role == "Pelanggan" and user=="user" and pw=="123":
            st.session_state.role = "user"; st.rerun()
        else:
            st.error("Login salah!")

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------- User Page ----------------------
def run_user():
    st.title("📋 Menu & Pesan")

    for kategori, items in menu_data.items():
        st.subheader(kategori.upper())
        for nama, harga in items.items():
            col1, col2, col3 = st.columns([3,1,1])
            col1.write(nama)
            col2.write(f"Rp {harga:,}")
            qty = col3.number_input("", 0, 10, key=nama)
            if qty>0:
                checkout_data.append({"nama": nama, "harga": harga, "jumlah": qty})
                save_json(CHECKOUT_FILE, checkout_data)
                st.success(f"Ditambahkan: {nama} x{qty}")

    if st.button("Selesai Pesan"):
        st.success("Pesanan dikirim ke kasir ✅")

# ---------------------- Admin Page ----------------------
def run_admin():
    st.sidebar.title("Admin Menu")
    menu = st.sidebar.radio("Menu", ["Laporan Penjualan", "Kelola Menu", "Pembayaran"])

    if menu=="Laporan Penjualan":
        st.title("📊 Laporan Penjualan")
        if not checkout_data: st.info("Belum ada transaksi.")
        else:
            df = pd.DataFrame(checkout_data)
            df["total"] = df["harga"]*df["jumlah"]
            st.dataframe(df)
            st.success(f"Total Pendapatan: Rp {df['total'].sum():,}")

    if menu=="Kelola Menu":
        st.title("🍽 Tambah Menu")
        kategori = st.selectbox("Kategori", menu_data.keys())
        nama = st.text_input("Nama Menu")
        harga = st.number_input("Harga", 1000)
        if st.button("Simpan Menu"):
            menu_data[kategori][nama]=harga
            save_json(MENU_FILE, menu_data)
            st.success("Menu ditambahkan")

    if menu=="Pembayaran":
        st.title("💵 Pembayaran")
        if not checkout_data: st.info("Belum ada pesanan")
        else:
            total = sum(i["harga"]*i["jumlah"] for i in checkout_data)
            st.write(f"Total bayar: **Rp {total:,}**")
            if st.button("Selesaikan Pembayaran"):
                save_json(CHECKOUT_FILE, [])
                st.success("Pembayaran sukses!")

# ---------------------- Router ----------------------
if st.session_state.role=="admin":
    st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"role":None}))
    run_admin()
elif st.session_state.role=="user":
    st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"role":None}))
    run_user()
else:
    login_page()

    padding: 3rem 2rem 2rem;
    background: rgba(255, 183, 77, 0.18);
    backdrop-filter: blur(14px);
    border-radius: 25px;
    box-shadow: 0 0 25px rgba(255, 150, 0, 0.3);
    text-align: center;
    color: #fff;
}
.header h2 {
    font-weight: 700;
    color: #ffcc00;
    text-shadow: 0 0 15px rgba(255,200,50,0.6);
}
.stTextInput>div>div>input {
    background-color: rgba(255,255,255,0.15);
    color: white !important;
    border-radius: 10px;
}
.stButton>button {
    width: 100%;
    height: 45px;
    border-radius: 12px;
    border: none;
    background: linear-gradient(270deg, #ff6b00, #ffb300);
    font-weight: 700;
    cursor: pointer;
}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ====== SESSION LOGIN ======
if "role" not in st.session_state:
    st.session_state.role = None

# ====== LOGIN PAGE ======
def login_page():
    st.markdown("<div class='overlay'></div>", unsafe_allow_html=True)
    st.markdown("<div class='login-card'>", unsafe_allow_html=True)

    st.markdown("<h2>Selamat Datang di<br>Mie Ayam Bakso Mas Ragil 🍜</h2>", unsafe_allow_html=True)

    role = st.selectbox("Masuk sebagai", ["Pelanggan", "Admin"])
    username = st.text_input("Email / ID Pengguna")
    password = st.text_input("Password", type="password")
    
    login = st.button("MASUK")

    if login:
        if role == "Admin":
            if username == "admin" and password == "123":
                st.session_state.role = "admin"
                st.rerun()
            else:
                st.error("ID atau password admin salah!")
        else:
            if username == "user" and password == "123":
                st.session_state.role = "user"
                st.rerun()
            else:
                st.error("Email atau password pelanggan salah!")

    st.markdown("</div>", unsafe_allow_html=True)

# ====== ROUTING ======
if st.session_state.role == "admin":
    st.sidebar.button("🚪 Logout", on_click=lambda: st.session_state.update({"role": None}))
    run_admin()

elif st.session_state.role == "user":
    st.sidebar.button("🚪 Logout", on_click=lambda: st.session_state.update({"role": None}))
    run_user()

else:
    login_page()
