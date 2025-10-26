# =====================================================
# admin_app.py — Admin Kasir Mas Ragil (Final)
# =====================================================
import streamlit as st
import json, os
from datetime import datetime

MENU_FILE = "kasir_mas_ragil/menu.json"
CHECKOUT_FILE = "kasir_mas_ragil/checkout.json"

# =============================
# ADMIN LOGIN
# =============================
def admin_login_page():
    st.markdown("""
        <style>
            .login-box {
                background-color: #0b1e3f;
                padding: 40px;
                border-radius: 20px;
                color: white;
                width: 380px;
                margin: 120px auto;
                text-align: center;
                box-shadow: 0 4px 15px rgba(0,0,0,0.3);
            }
            input, button {
                border-radius: 8px !important;
            }
            .stButton>button {
                background-color: #1976d2;
                color: white;
                font-weight: bold;
                width: 100%;
            }
            .stButton>button:hover {
                background-color: #1258a6 !important;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="login-box"><h2>🔐 Login Admin</h2>', unsafe_allow_html=True)
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Masuk"):
        if username == "admin" and password == "admin123":
            st.session_state.admin_login = True
            st.success("Login berhasil! Selamat datang, Admin 👨‍💼")
            st.rerun()
        else:
            st.error("Username atau password salah.")
    st.markdown("</div>", unsafe_allow_html=True)


# =============================
# DASHBOARD ADMIN
# =============================
def run_admin():
    if "admin_login" not in st.session_state:
        st.session_state.admin_login = False

    if not st.session_state.admin_login:
        admin_login_page()
        return

    # ====== Sidebar Toggle ======
    st.sidebar.markdown(
        """
        <style>
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0b1e3f, #1e88e5);
            color: white;
        }
        [data-testid="stSidebar"] h2, [data-testid="stSidebar"] p, [data-testid="stSidebar"] label {
            color: white !important;
        }
        .stRadio>div>label {
            color: white !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    menu = ["📦 Pesanan", "💳 Pembayaran", "📊 Laporan", "🍜 Kelola Menu", "🚪 Logout"]
    page = st.sidebar.radio("Navigasi Admin", menu)

    st.title("👨‍💼 Dashboard Admin — Rumah Makan Mas Ragil")
    st.divider()

    # =============================
    # MENU PESANAN
    # =============================
    if page == "📦 Pesanan":
        st.header("📦 Daftar Pesanan Masuk")
        if os.path.exists(CHECKOUT_FILE):
            with open(CHECKOUT_FILE, "r", encoding="utf-8") as f:
                data_checkout = json.load(f)

            if data_checkout:
                for i, pesanan in enumerate(data_checkout):
                    with st.container():
                        st.markdown("---")
                        st.write(f"👤 **User:** {pesanan['username']}")
                        st.write(f"🕒 **Waktu:** {pesanan['timestamp']}")
                        st.write("📋 **Detail Pesanan:**")
                        for item, qty in pesanan["items"].items():
                            st.write(f"- {item} x{qty} (Rp {pesanan['subtotal'][item]:,})")
                        st.write(f"💰 **Total:** Rp {pesanan['total_bayar']:,}")

                        if st.button("❌ Hapus Pesanan Ini", key=f"hapus_{i}"):
                            data_checkout.pop(i)
                            with open(CHECKOUT_FILE, "w", encoding="utf-8") as f:
                                json.dump(data_checkout, f, ensure_ascii=False, indent=2)
                            st.success("Pesanan berhasil dihapus.")
                            st.rerun()
            else:
                st.info("Belum ada pesanan masuk.")
        else:
            st.info("Belum ada data pesanan.")

    # =============================
    # PEMBAYARAN
    # =============================
    elif page == "💳 Pembayaran":
        st.header("💳 Proses Pembayaran")
        if os.path.exists(CHECKOUT_FILE):
            with open(CHECKOUT_FILE, "r", encoding="utf-8") as f:
                data_checkout = json.load(f)
            if data_checkout:
                for i, pesanan in enumerate(data_checkout):
                    with st.container():
                        st.markdown("---")
                        st.write(f"👤 {pesanan['username']} — {pesanan['timestamp']}")
                        total = pesanan['total_bayar']
                        uang = st.number_input(f"Uang diterima ({pesanan['username']})", min_value=0, value=total, step=1000, key=f"uang_{i}")
                        if st.button(f"💰 Bayar ({pesanan['username']})", key=f"bayar_{i}"):
                            if uang >= total:
                                kembalian = uang - total
                                st.success(f"✅ Pembayaran berhasil. Kembalian: Rp {kembalian:,}")
                                data_checkout.pop(i)
                                with open(CHECKOUT_FILE, "w", encoding="utf-8") as f:
                                    json.dump(data_checkout, f, ensure_ascii=False, indent=2)
                                st.rerun()
                            else:
                                st.error("❌ Uang kurang!")
            else:
                st.info("Belum ada pesanan yang harus dibayar.")
        else:
            st.info("Belum ada data pembayaran.")

    # =============================
    # LAPORAN
    # =============================
    elif page == "📊 Laporan":
        st.header("📊 Laporan Penjualan")
        if os.path.exists(CHECKOUT_FILE):
            with open(CHECKOUT_FILE, "r", encoding="utf-8") as f:
                laporan = json.load(f)
            if laporan:
                st.dataframe(laporan)
                if st.button("🗑️ Hapus Semua Laporan"):
                    os.remove(CHECKOUT_FILE)
                    st.success("Laporan dihapus semua.")
                    st.rerun()
            else:
                st.info("Belum ada data laporan.")
        else:
            st.info("Belum ada laporan penjualan.")

    # =============================
    # KELOLA MENU
    # =============================
    elif page == "🍜 Kelola Menu":
        st.header("🍜 Kelola Menu Makanan & Minuman")

        if os.path.exists(MENU_FILE):
            with open(MENU_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                makanan = data.get("makanan", {})
                minuman = data.get("minuman", {})
        else:
            makanan = {"Mie Ayam": 15000, "Bakso": 18000}
            minuman = {"Es Teh": 5000, "Es Jeruk": 7000}

        st.subheader("🍲 Makanan")
        for item, harga in makanan.copy().items():
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                nama_baru = st.text_input(f"{item}", value=item, key=f"m_{item}")
            with col2:
                harga_baru = st.number_input(f"Harga {item}", value=harga, step=1000, key=f"h_{item}")
            with col3:
                if st.button("💾 Update", key=f"up_{item}"):
                    makanan[nama_baru] = harga_baru
                    if nama_baru != item:
                        del makanan[item]
                    with open(MENU_FILE, "w", encoding="utf-8") as f:
                        json.dump({"makanan": makanan, "minuman": minuman}, f, ensure_ascii=False, indent=2)
                    st.success(f"{nama_baru} diperbarui.")
                    st.rerun()
                if st.button("❌ Hapus", key=f"delm_{item}"):
                    del makanan[item]
                    with open(MENU_FILE, "w", encoding="utf-8") as f:
                        json.dump({"makanan": makanan, "minuman": minuman}, f, ensure_ascii=False, indent=2)
                    st.success(f"{item} dihapus.")
                    st.rerun()

        st.subheader("🥤 Minuman")
        for item, harga in minuman.copy().items():
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                nama_baru = st.text_input(f"{item}", value=item, key=f"min_{item}")
            with col2:
                harga_baru = st.number_input(f"Harga {item}", value=harga, step=1000, key=f"hm_{item}")
            with col3:
                if st.button("💾 Update ", key=f"upm_{item}"):
                    minuman[nama_baru] = harga_baru
                    if nama_baru != item:
                        del minuman[item]
                    with open(MENU_FILE, "w", encoding="utf-8") as f:
                        json.dump({"makanan": makanan, "minuman": minuman}, f, ensure_ascii=False, indent=2)
                    st.success(f"{nama_baru} diperbarui.")
                    st.rerun()
                if st.button("❌ Hapus ", key=f"delmin_{item}"):
                    del minuman[item]
                    with open(MENU_FILE, "w", encoding="utf-8") as f:
                        json.dump({"makanan": makanan, "minuman": minuman}, f, ensure_ascii=False, indent=2)
                    st.success(f"{item} dihapus.")
                    st.rerun()

        st.subheader("➕ Tambah Menu Baru")
        new_name = st.text_input("Nama Menu Baru")
        new_price = st.number_input("Harga", min_value=0, step=1000)
        jenis = st.radio("Jenis", ["Makanan", "Minuman"], horizontal=True)
        if st.button("Tambah Menu"):
            if new_name.strip():
                if jenis == "Makanan":
                    makanan[new_name] = new_price
                else:
                    minuman[new_name] = new_price
                with open(MENU_FILE, "w", encoding="utf-8") as f:
                    json.dump({"makanan": makanan, "minuman": minuman}, f, ensure_ascii=False, indent=2)
                st.success("Menu baru ditambahkan.")
                st.rerun()
            else:
                st.warning("Nama menu tidak boleh kosong.")

    # =============================
    # LOGOUT
    # =============================
    elif page == "🚪 Logout":
        st.session_state.admin_login = False
        st.success("Logout berhasil.")
        st.rerun()
