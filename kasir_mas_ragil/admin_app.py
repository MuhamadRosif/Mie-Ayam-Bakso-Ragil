import streamlit as st
import json, os, pandas as pd

# File paths
MENU_FILE = "menu.json"
CHECKOUT_FILE = "checkout.json"

# Load/Save JSON
def load_json(file):
    if not os.path.exists(file):
        return {}
    with open(file, "r") as f:
        return json.load(f)

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)

menu_data = load_json(MENU_FILE)
checkout_data = load_json(CHECKOUT_FILE)

# ===== LOGIN CONFIG =====
USERS = {"admin": "123", "user": "123"}

# ===== LOGIN UI =====
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None

if not st.session_state.logged_in:
    st.markdown("""
        <style>
        body { background: #0d1117; }
        .login-box {
            max-width: 380px; margin: auto; margin-top: 120px; 
            background: rgba(255,183,77,0.18); padding: 30px;
            border-radius: 20px; backdrop-filter: blur(12px);
            border: 1px solid rgba(255,200,100,0.3);
            box-shadow: 0 0 20px rgba(255,170,0,0.4);
            text-align:center;
        }
        .title { font-size:24px; color:white; font-weight:600; }
        .emoji { font-size:55px; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    st.markdown('<div class="emoji">🍜</div>', unsafe_allow_html=True)
    st.markdown('<div class="title">Mie Ayam Bakso Mas Ragil</div>', unsafe_allow_html=True)

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Masuk ✅", use_container_width=True):
        if username in USERS and USERS[username] == password:
            st.session_state.logged_in = True
            st.session_state.role = username
            st.success("Login berhasil!")
            st.rerun()
        else:
            st.error("❌ Username atau Password salah!")

    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ===== ROLE ROUTING =====

# ---------------------------
# ADMIN PAGE
# ---------------------------
if st.session_state.role == "admin":
    st.sidebar.success("Login sebagai ADMIN 👑")
    if st.sidebar.button("Logout 🚪"):
        st.session_state.logged_in = False
        st.rerun()

    menu = st.sidebar.radio("Menu Admin", ["📊 Laporan Penjualan", "🍜 Kelola Menu", "🧾 Data Pesanan", "💵 Pembayaran"])

    # ======= LAPORAN =======
    if menu == "📊 Laporan Penjualan":
        st.title("📊 Laporan Penjualan")
        if not checkout_data:
            st.info("Belum ada transaksi.")
        else:
            df = pd.DataFrame(checkout_data)
            df["subtotal"] = df["harga"] * df["jumlah"]
            st.dataframe(df)
            st.markdown(f"### Total Pendapatan: **Rp {df['subtotal'].sum():,}**")

    # ======= KELOLA MENU =======
    elif menu == "🍜 Kelola Menu":
        st.title("🍜 Kelola Menu")

        menu_df = []
        for kategori, items in menu_data.items():
            for nama, harga in items.items():
                menu_df.append({"Kategori": kategori, "Nama": nama, "Harga": harga})
        st.dataframe(pd.DataFrame(menu_df), use_container_width=True)

        st.subheader("Tambah Menu")
        kategori = st.selectbox("Kategori Menu", ["makanan", "minuman"])
        nama = st.text_input("Nama Menu")
        harga = st.number_input("Harga", min_value=0, step=1000)

        if st.button("Simpan Menu ✅"):
            if nama and harga > 0:
                menu_data[kategori][nama] = harga
                save_json(MENU_FILE, menu_data)
                st.success("Menu Berhasil Ditambah!")
                st.rerun()
            else:
                st.warning("Nama dan Harga harus diisi!")

    # ======= DATA PESANAN =======
    elif menu == "🧾 Data Pesanan":
        st.title("🧾 Data Pesanan Pelanggan")
        if not checkout_data:
            st.info("Belum ada pesanan.")
        else:
            df = pd.DataFrame(checkout_data)
            st.dataframe(df)
            if st.button("Hapus Semua Pesanan 🧹"):
                save_json(CHECKOUT_FILE, [])
                st.rerun()

    # ======= PEMBAYARAN =======
    elif menu == "💵 Pembayaran":
        st.title("💵 Proses Pembayaran")
        if not checkout_data:
            st.info("Belum ada pesanan untuk dibayar.")
        else:
            df = pd.DataFrame(checkout_data)
            df["Total"] = df["harga"] * df["jumlah"]
            st.dataframe(df)

            nama_pembeli = st.text_input("Nama Pembeli")
            total = df["Total"].sum()

            if st.button("Cetak Struk ✅"):
                txt = f"Struk Pembelian - {nama_pembeli or 'Pelanggan'}\n" + "="*40 + "\n"
                for _, r in df.iterrows():
                    txt += f"{r['nama']} x{r['jumlah']} = Rp {r['Total']}\n"
                txt += "="*40 + f"\nTotal: Rp {total}\n"

                file = "struk.txt"
                with open(file, "w") as f: f.write(txt)
                st.download_button("Download Struk 📄", open(file,"rb"), file_name=file)
                save_json(CHECKOUT_FILE, [])
                st.success("Pembayaran berhasil!")

# ---------------------------
# USER PAGE
# ---------------------------
if st.session_state.role == "user":
    st.sidebar.success("Login sebagai PELANGGAN 🧑‍🍳")
    if st.sidebar.button("Logout 🚪"):
        st.session_state.logged_in = False
        st.rerun()

    st.title("🍜 Menu Mas Ragil")

    for kategori, daftar in menu_data.items():
        st.subheader(f"📌 {kategori.upper()}")
        for nama, harga in daftar.items():
            col1, col2, col3 = st.columns([3,2,1])
            col1.write(f"**{nama}**")
            col2.write(f"Rp {harga:,}")
            if col3.button("Pesan", key=nama):
                checkout_data.append({"nama": nama, "harga": harga, "jumlah": 1})
                save_json(CHECKOUT_FILE, checkout_data)
                st.success(f"{nama} ditambahkan!")

    if st.button("Checkout 🛒"):
        st.switch_page("👑 Admin")
