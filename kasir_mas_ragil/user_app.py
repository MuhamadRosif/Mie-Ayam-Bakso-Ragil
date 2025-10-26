import streamlit as st
import json, os
from datetime import datetime

# ==========================================================
# File Paths
# ==========================================================
MENU_FILE = "kasir_mas_ragil/menu.json"
CHECKOUT_FILE = "kasir_mas_ragil/checkout.json"
USERS_FILE = "kasir_mas_ragil/users.json"
RIWAYAT_FILE = "kasir_mas_ragil/riwayat.json"

# ==========================================================
# User App
# ==========================================================
def run_user():
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] {
            background-color: #0B2447;
            color: white;
        }
        [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
            color: white !important;
        }
        .stButton>button {
            background-color: #19376D;
            color: white;
            border-radius: 8px;
            transition: all 0.3s;
        }
        .stButton>button:hover {
            background-color: #1E56A0;
            transform: scale(1.05);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # -----------------------
    # Session defaults
    # -----------------------
    if "user_login" not in st.session_state:
        st.session_state.user_login = False
    if "username" not in st.session_state:
        st.session_state.username = ""
    if "keranjang" not in st.session_state:
        st.session_state.keranjang = {}

    # -----------------------
    # Load users
    # -----------------------
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            users_data = json.load(f)
    else:
        users_data = {}

    # -----------------------
    # Login / Registrasi
    # -----------------------
    if not st.session_state.user_login:
        st.title("👤 Login / Registrasi Pengguna")

        tab1, tab2 = st.tabs(["🔑 Login", "📝 Registrasi"])

        with tab1:
            login_username = st.text_input("Username", key="login_user")
            login_password = st.text_input("Password", type="password", key="login_pass")
            if st.button("Masuk"):
                if login_username in users_data and users_data[login_username] == login_password:
                    st.session_state.user_login = True
                    st.session_state.username = login_username
                    st.success(f"Selamat datang, {login_username}! 🍜")
                    st.rerun()
                else:
                    st.error("Username atau password salah.")

        with tab2:
            reg_username = st.text_input("Buat Username", key="reg_user")
            reg_password = st.text_input("Buat Password", type="password", key="reg_pass")
            if st.button("Daftar"):
                if reg_username.strip() and reg_password.strip():
                    if reg_username in users_data:
                        st.warning("Username sudah digunakan.")
                    else:
                        users_data[reg_username] = reg_password
                        with open(USERS_FILE, "w", encoding="utf-8") as f:
                            json.dump(users_data, f, ensure_ascii=False, indent=2)
                        st.success("Registrasi berhasil! Silakan login.")
                        st.rerun()
                else:
                    st.warning("Isi semua kolom terlebih dahulu.")
        return

    # -----------------------
    # Sidebar Menu
    # -----------------------
    st.sidebar.title(f"🍜 Halo, {st.session_state.username}")
    page = st.sidebar.radio(
        "Navigasi",
        ["Beranda", "Menu Makanan", "Menu Minuman", "Keranjang", "Riwayat", "Tentang", "Logout"],
    )

    # Tombol Logout
    if page == "Logout":
        st.session_state.user_login = False
        st.session_state.username = ""
        st.session_state.keranjang = {}
        st.success("Logout berhasil.")
        st.rerun()

    # -----------------------
    # Load Menu
    # -----------------------
    if os.path.exists(MENU_FILE):
        with open(MENU_FILE, "r", encoding="utf-8") as f:
            menu_data = json.load(f)
            menu_makanan = menu_data.get("makanan", {})
            menu_minuman = menu_data.get("minuman", {})
    else:
        menu_makanan, menu_minuman = {}, {}

    # -----------------------
    # Beranda
    # -----------------------
    if page == "Beranda":
        st.title("🏠 Rumah Makan Mas Ragil")
        st.markdown(
            """
            Selamat datang di **Rumah Makan Mas Ragil**!  
            Tempat terbaik untuk menikmati **Mie Ayam dan Bakso** dengan cita rasa khas. 🍜  
            Silakan pilih menu di samping untuk memulai pemesanan.
            """
        )

    # -----------------------
    # Menu Makanan
    # -----------------------
    elif page == "Menu Makanan":
        st.header("🍽️ Menu Makanan")
        for item, harga in menu_makanan.items():
            col1, col2, col3, col4 = st.columns([3, 1, 1, 2])
            with col1:
                st.write(f"**{item}** — Rp {harga:,}")
            with col2:
                if st.button("-", key=f"{item}-minus"):
                    st.session_state.keranjang[item] = max(0, st.session_state.keranjang.get(item, 0) - 1)
            with col3:
                st.write(f"Qty: {st.session_state.keranjang.get(item, 0)}")
            with col4:
                if st.button("+", key=f"{item}-plus"):
                    st.session_state.keranjang[item] = st.session_state.keranjang.get(item, 0) + 1

    # -----------------------
    # Menu Minuman
    # -----------------------
    elif page == "Menu Minuman":
        st.header("🥤 Menu Minuman")
        for item, harga in menu_minuman.items():
            col1, col2, col3, col4 = st.columns([3, 1, 1, 2])
            with col1:
                st.write(f"**{item}** — Rp {harga:,}")
            with col2:
                if st.button("-", key=f"{item}-minus-minum"):
                    st.session_state.keranjang[item] = max(0, st.session_state.keranjang.get(item, 0) - 1)
            with col3:
                st.write(f"Qty: {st.session_state.keranjang.get(item, 0)}")
            with col4:
                if st.button("+", key=f"{item}-plus-minum"):
                    st.session_state.keranjang[item] = st.session_state.keranjang.get(item, 0) + 1

    # -----------------------
    # Keranjang
    # -----------------------
    elif page == "Keranjang":
        st.header("🛒 Keranjang Anda")

        keranjang_aktif = {k: v for k, v in st.session_state.keranjang.items() if v > 0}

        if keranjang_aktif:
            total_bayar = 0
            for k, v in keranjang_aktif.items():
                harga = menu_makanan.get(k, menu_minuman.get(k, 0))
                subtotal = v * harga
                total_bayar += subtotal
                st.write(f"- {k} x {v} = Rp {subtotal:,}")

            st.success(f"Total Bayar: Rp {total_bayar:,}")

            if st.button("🧾 Checkout Sekarang"):
                data_checkout = []
                if os.path.exists(CHECKOUT_FILE):
                    with open(CHECKOUT_FILE, "r", encoding="utf-8") as f:
                        data_checkout = json.load(f)

                data_checkout.append({
                    "username": st.session_state.username,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "items": keranjang_aktif,
                    "total_bayar": total_bayar
                })

                with open(CHECKOUT_FILE, "w", encoding="utf-8") as f:
                    json.dump(data_checkout, f, ensure_ascii=False, indent=2)

                # Simpan riwayat
                riwayat = []
                if os.path.exists(RIWAYAT_FILE):
                    with open(RIWAYAT_FILE, "r", encoding="utf-8") as f:
                        riwayat = json.load(f)
                riwayat.append({
                    "username": st.session_state.username,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "items": keranjang_aktif,
                    "total_bayar": total_bayar
                })
                with open(RIWAYAT_FILE, "w", encoding="utf-8") as f:
                    json.dump(riwayat, f, ensure_ascii=False, indent=2)

                st.success("✅ Pesanan berhasil dikirim, silakan tunggu proses pembayaran.")
                st.session_state.keranjang = {}
                st.rerun()

            if st.button("❌ Hapus Keranjang"):
                st.session_state.keranjang = {}
                st.warning("Keranjang dikosongkan.")
        else:
            st.info("Keranjang masih kosong.")

    # -----------------------
    # Riwayat
    # -----------------------
    elif page == "Riwayat":
        st.header("📜 Riwayat Pesanan Anda")

        if os.path.exists(RIWAYAT_FILE):
            with open(RIWAYAT_FILE, "r", encoding="utf-8") as f:
                riwayat = json.load(f)

            user_riwayat = [r for r in riwayat if r["username"] == st.session_state.username]

            if user_riwayat:
                for r in user_riwayat:
                    st.markdown(f"**{r['timestamp']}** — Total Rp {r['total_bayar']:,}")
                    for item, qty in r["items"].items():
                        st.write(f"- {item} x {qty}")
            else:
                st.info("Belum ada riwayat pesanan.")
        else:
            st.info("Belum ada riwayat tersimpan.")

    # -----------------------
    # Tentang
    # -----------------------
    elif page == "Tentang":
        st.header("ℹ️ Tentang Aplikasi")
        st.markdown(
            """
            Aplikasi ini dibuat untuk memudahkan pelanggan Rumah Makan Mas Ragil  
            dalam memesan makanan dan minuman secara digital.  
            Dibangun dengan **Python + Streamlit** oleh pengembang yang cinta rasa Nusantara. 🇮🇩  
            """
        )
