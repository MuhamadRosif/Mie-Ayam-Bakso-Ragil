import streamlit as st
import json, os
from datetime import datetime

# ==========================================================
# File Paths
# ==========================================================
CHECKOUT_FILE = "kasir_mas_ragil/checkout.json"
MENU_FILE = "kasir_mas_ragil/menu.json"
LAPORAN_FILE = "kasir_mas_ragil/laporan.json"

# ==========================================================
# Admin App
# ==========================================================
def run_admin():
    st.markdown(
        """
        <style>
        /* Styling untuk sidebar toggle */
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
    # Login Admin
    # -----------------------
    if "admin_login" not in st.session_state:
        st.session_state.admin_login = False

    ADMIN_USER = "admin"
    ADMIN_PASS = "admin123"

    if not st.session_state.admin_login:
        st.title("👑 Login Admin")
        st.write("Masuk untuk mengelola pesanan dan menu.")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Masuk"):
            if username == ADMIN_USER and password == ADMIN_PASS:
                st.session_state.admin_login = True
                st.success("Login berhasil ✅")
                st.rerun()
            else:
                st.error("Username atau password salah.")
        return

    # -----------------------
    # Sidebar Menu
    # -----------------------
    st.sidebar.title("⚙️ Menu Admin")
    page = st.sidebar.radio(
        "Navigasi",
        ["Pesanan User", "Pembayaran", "Laporan", "Kelola Menu", "Logout"],
    )

    # Tombol logout
    if page == "Logout":
        st.session_state.admin_login = False
        st.success("Anda telah logout.")
        st.rerun()

    # -----------------------
    # Muat menu
    # -----------------------
    if os.path.exists(MENU_FILE):
        with open(MENU_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        makanan = data.get("makanan", {})
        minuman = data.get("minuman", {})
    else:
        makanan, minuman = {}, {}

    # -----------------------
    # Halaman Pesanan User
    # -----------------------
    if page == "Pesanan User":
        st.header("📋 Pesanan User")
        if os.path.exists(CHECKOUT_FILE):
            with open(CHECKOUT_FILE, "r", encoding="utf-8") as f:
                checkout = json.load(f)

            if checkout:
                for idx, co in enumerate(checkout):
                    st.markdown(f"### {co['username']} — {co['timestamp']}")
                    for item, qty in co["items"].items():
                        st.write(f"- {item} x {qty}")
                    st.info(f"Total: Rp {co['total_bayar']:,}")

                    if st.button(f"❌ Hapus Pesanan ({co['username']})", key=f"hapus-{idx}"):
                        checkout.pop(idx)
                        with open(CHECKOUT_FILE, "w", encoding="utf-8") as f:
                            json.dump(checkout, f, ensure_ascii=False, indent=2)
                        st.success("Pesanan dihapus.")
                        st.rerun()
            else:
                st.info("Belum ada pesanan.")
        else:
            st.info("Belum ada data pesanan.")

    # -----------------------
    # Halaman Pembayaran
    # -----------------------
    elif page == "Pembayaran":
        st.header("💳 Proses Pembayaran")
        if os.path.exists(CHECKOUT_FILE):
            with open(CHECKOUT_FILE, "r", encoding="utf-8") as f:
                checkout = json.load(f)

            if checkout:
                for idx, co in enumerate(checkout):
                    st.markdown(f"### {co['username']} — {co['timestamp']}")
                    total = co["total_bayar"]
                    uang = st.number_input(
                        f"Uang diterima ({co['username']})",
                        min_value=0,
                        value=total,
                        step=1000,
                        key=f"uang-{idx}",
                    )

                    if st.button(f"Bayar {co['username']}", key=f"bayar-{idx}"):
                        if uang >= total:
                            kembalian = uang - total
                            st.success(f"✅ Pembayaran berhasil. Kembalian Rp {kembalian:,}")

                            # Simpan ke laporan
                            laporan = []
                            if os.path.exists(LAPORAN_FILE):
                                with open(LAPORAN_FILE, "r", encoding="utf-8") as f:
                                    laporan = json.load(f)
                            laporan.append(co)
                            with open(LAPORAN_FILE, "w", encoding="utf-8") as f:
                                json.dump(laporan, f, ensure_ascii=False, indent=2)

                            # Hapus dari checkout
                            checkout.pop(idx)
                            with open(CHECKOUT_FILE, "w", encoding="utf-8") as f:
                                json.dump(checkout, f, ensure_ascii=False, indent=2)
                            st.rerun()
                        else:
                            st.error("Uang kurang!")
            else:
                st.info("Belum ada pesanan untuk dibayar.")
        else:
            st.info("Belum ada pesanan.")

    # -----------------------
    # Halaman Laporan
    # -----------------------
    elif page == "Laporan":
        st.header("📊 Laporan Penjualan")
        if os.path.exists(LAPORAN_FILE):
            with open(LAPORAN_FILE, "r", encoding="utf-8") as f:
                laporan = json.load(f)

            if laporan:
                st.dataframe(laporan)
                if st.button("🗑️ Hapus Semua Laporan"):
                    os.remove(LAPORAN_FILE)
                    st.success("Semua laporan telah dihapus.")
                    st.rerun()
            else:
                st.info("Belum ada laporan.")
        else:
            st.info("Belum ada laporan.")

    # -----------------------
    # Halaman Kelola Menu
    # -----------------------
    elif page == "Kelola Menu":
        st.header("🍽️ Kelola Menu")

        st.subheader("Makanan")
        for item, harga in makanan.copy().items():
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                nama_baru = st.text_input(f"{item}", value=item, key=f"m-{item}")
            with col2:
                harga_baru = st.number_input(f"Harga {item}", value=harga, step=1000, key=f"h-{item}")
            with col3:
                if st.button("💾 Update", key=f"up-{item}"):
                    makanan[nama_baru] = harga_baru
                    if nama_baru != item:
                        del makanan[item]
                    with open(MENU_FILE, "w", encoding="utf-8") as f:
                        json.dump({"makanan": makanan, "minuman": minuman}, f, ensure_ascii=False, indent=2)
                    st.success(f"{nama_baru} diperbarui.")
                    st.rerun()
                if st.button("❌ Hapus", key=f"delm-{item}"):
                    del makanan[item]
                    with open(MENU_FILE, "w", encoding="utf-8") as f:
                        json.dump({"makanan": makanan, "minuman": minuman}, f, ensure_ascii=False, indent=2)
                    st.success(f"{item} dihapus.")
                    st.rerun()

        st.divider()
        st.subheader("Tambah Menu Baru")
        nama_baru = st.text_input("Nama Menu")
        harga_baru = st.number_input("Harga", min_value=0, step=1000)
        kategori = st.selectbox("Kategori", ["Makanan", "Minuman"])

        if st.button("➕ Tambah"):
            if nama_baru and harga_baru > 0:
                if kategori == "Makanan":
                    makanan[nama_baru] = harga_baru
                else:
                    minuman[nama_baru] = harga_baru
                with open(MENU_FILE, "w", encoding="utf-8") as f:
                    json.dump({"makanan": makanan, "minuman": minuman}, f, ensure_ascii=False, indent=2)
                st.success("Menu baru ditambahkan.")
                st.rerun()
            else:
                st.warning("Isi nama dan harga terlebih dahulu.")
