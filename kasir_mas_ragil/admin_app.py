# =====================================================
# admin_app.py — Admin Kasir Mas Ragil
# =====================================================
import streamlit as st
import json
import os
from datetime import datetime

MENU_FILE = "kasir_mas_ragil/menu.json"
CHECKOUT_FILE = "kasir_mas_ragil/checkout.json"
LAPORAN_FILE = "kasir_mas_ragil/laporan.json"


# =====================================================
# Fungsi Utama
# =====================================================
def run_admin():
    st.title("🧑‍🍳 Admin - Rumah Makan Mas Ragil")

    # -----------------------
    # Session defaults
    # -----------------------
    if "admin_login" not in st.session_state:
        st.session_state.admin_login = False

    # -----------------------
    # Login Admin
    # -----------------------
    if not st.session_state.admin_login:
        st.markdown(
            """
            <style>
            div[data-testid="stForm"] {
                background-color: #0A2647;
                padding: 30px;
                border-radius: 15px;
                color: white;
                box-shadow: 0 0 10px rgba(0,0,0,0.3);
            }
            input {
                color: black !important;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        with st.form("admin_login_form"):
            st.markdown("### 🔑 Login Admin")
            username = st.text_input("Username", placeholder="Masukkan username admin")
            password = st.text_input("Password", type="password", placeholder="Masukkan password")
            submit = st.form_submit_button("Login")

            if submit:
                if username == "admin" and password == "admin123":
                    st.session_state.admin_login = True
                    st.success("Login berhasil! Selamat datang, Admin 👨‍💼")
                    st.rerun()
                else:
                    st.error("Username atau password salah.")
        return

    # -----------------------
    # Tombol Logout di sidebar toggle
    # -----------------------
    with st.sidebar:
        st.markdown("### 🔧 Menu Admin")
        menu = st.radio(
            "Pilih Halaman:",
            ["Pesanan", "Pembayaran", "Laporan", "Kelola Menu", "Logout"],
            label_visibility="collapsed"
        )

    # -----------------------
    # PESANAN
    # -----------------------
    if menu == "Pesanan":
        st.header("🧾 Daftar Pesanan User")
        if os.path.exists(CHECKOUT_FILE):
            with open(CHECKOUT_FILE, "r", encoding="utf-8") as f:
                data_checkout = json.load(f)

            if data_checkout:
                for i, data in enumerate(data_checkout):
                    with st.expander(f"{data['username']} - {data['timestamp']}"):
                        st.write("**Items:**")
                        for item, qty in data["items"].items():
                            st.write(f"- {item}: {qty}x (Rp {data['subtotal'][item]:,})")
                        st.info(f"Total Bayar: Rp {data['total_bayar']:,}")

                        if st.button(f"❌ Hapus Pesanan #{i+1}", key=f"hapus_pesanan_{i}"):
                            data_checkout.pop(i)
                            with open(CHECKOUT_FILE, "w", encoding="utf-8") as f:
                                json.dump(data_checkout, f, ensure_ascii=False, indent=2)
                            st.success("Pesanan berhasil dihapus.")
                            st.rerun()
            else:
                st.info("Belum ada pesanan.")
        else:
            st.info("Belum ada pesanan.")

    # -----------------------
    # PEMBAYARAN
    # -----------------------
    elif menu == "Pembayaran":
        st.header("💰 Pembayaran Pesanan")
        if os.path.exists(CHECKOUT_FILE):
            with open(CHECKOUT_FILE, "r", encoding="utf-8") as f:
                data_checkout = json.load(f)
        else:
            data_checkout = []

        if data_checkout:
            for i, data in enumerate(data_checkout):
                with st.expander(f"{data['username']} - Rp {data['total_bayar']:,}"):
                    st.write(f"Tanggal: {data['timestamp']}")
                    if "status" not in data:
                        data["status"] = "Belum Dibayar"

                    st.write(f"Status: **{data['status']}**")
                    if st.button(f"Tandai Sudah Dibayar #{i+1}", key=f"bayar_{i}"):
                        data_checkout[i]["status"] = "Sudah Dibayar"

                        # Tambahkan ke laporan
                        laporan_entry = {
                            "username": data["username"],
                            "total": data["total_bayar"],
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        }

                        if os.path.exists(LAPORAN_FILE):
                            with open(LAPORAN_FILE, "r", encoding="utf-8") as f:
                                laporan_data = json.load(f)
                        else:
                            laporan_data = []

                        laporan_data.append(laporan_entry)
                        with open(LAPORAN_FILE, "w", encoding="utf-8") as f:
                            json.dump(laporan_data, f, ensure_ascii=False, indent=2)

                        with open(CHECKOUT_FILE, "w", encoding="utf-8") as f:
                            json.dump(data_checkout, f, ensure_ascii=False, indent=2)
                        st.success("Pembayaran berhasil dicatat ke laporan.")
                        st.rerun()
        else:
            st.info("Belum ada data pembayaran.")

    # -----------------------
    # LAPORAN
    # -----------------------
    elif menu == "Laporan":
        st.header("📊 Laporan Penjualan")
        if os.path.exists(LAPORAN_FILE):
            with open(LAPORAN_FILE, "r", encoding="utf-8") as f:
                laporan_data = json.load(f)

            if laporan_data:
                total_semua = sum(l["total"] for l in laporan_data)
                st.success(f"Total Pendapatan: Rp {total_semua:,}")
                for i, lap in enumerate(laporan_data):
                    with st.expander(f"{lap['username']} - {lap['timestamp']}"):
                        st.write(f"Total: Rp {lap['total']:,}")
                        if st.button(f"🗑️ Hapus Laporan #{i+1}", key=f"hapus_laporan_{i}"):
                            laporan_data.pop(i)
                            with open(LAPORAN_FILE, "w", encoding="utf-8") as f:
                                json.dump(laporan_data, f, ensure_ascii=False, indent=2)
                            st.success("Laporan dihapus.")
                            st.rerun()
            else:
                st.info("Belum ada laporan.")
        else:
            st.info("Belum ada laporan.")

    # -----------------------
    # KELOLA MENU
    # -----------------------
    elif menu == "Kelola Menu":
        st.header("🍜 Kelola Menu")
        if os.path.exists(MENU_FILE):
            with open(MENU_FILE, "r", encoding="utf-8") as f:
                menu_data = json.load(f)
        else:
            menu_data = {"makanan": {}, "minuman": {}}

        tab1, tab2 = st.tabs(["Makanan", "Minuman"])

        # Makanan
        with tab1:
            for item, harga in menu_data["makanan"].items():
                col1, col2, col3 = st.columns([3, 2, 1])
                with col1: st.write(item)
                with col2: st.write(f"Rp {harga:,}")
                with col3:
                    if st.button("🗑️", key=f"hapus_makanan_{item}"):
                        menu_data["makanan"].pop(item)
                        with open(MENU_FILE, "w", encoding="utf-8") as f:
                            json.dump(menu_data, f, ensure_ascii=False, indent=2)
                        st.rerun()

            st.subheader("Tambah Menu Makanan")
            new_food = st.text_input("Nama Makanan Baru")
            new_price = st.number_input("Harga", min_value=0, step=1000)
            if st.button("Tambah Makanan"):
                if new_food.strip():
                    menu_data["makanan"][new_food] = int(new_price)
                    with open(MENU_FILE, "w", encoding="utf-8") as f:
                        json.dump(menu_data, f, ensure_ascii=False, indent=2)
                    st.success("Makanan ditambahkan!")
                    st.rerun()

        # Minuman
        with tab2:
            for item, harga in menu_data["minuman"].items():
                col1, col2, col3 = st.columns([3, 2, 1])
                with col1: st.write(item)
                with col2: st.write(f"Rp {harga:,}")
                with col3:
                    if st.button("🗑️", key=f"hapus_minuman_{item}"):
                        menu_data["minuman"].pop(item)
                        with open(MENU_FILE, "w", encoding="utf-8") as f:
                            json.dump(menu_data, f, ensure_ascii=False, indent=2)
                        st.rerun()

            st.subheader("Tambah Menu Minuman")
            new_drink = st.text_input("Nama Minuman Baru")
            new_price_d = st.number_input("Harga ", min_value=0, step=1000, key="price_d")
            if st.button("Tambah Minuman"):
                if new_drink.strip():
                    menu_data["minuman"][new_drink] = int(new_price_d)
                    with open(MENU_FILE, "w", encoding="utf-8") as f:
                        json.dump(menu_data, f, ensure_ascii=False, indent=2)
                    st.success("Minuman ditambahkan!")
                    st.rerun()

    # -----------------------
    # LOGOUT
    # -----------------------
    elif menu == "Logout":
        st.session_state.admin_login = False
        st.success("Anda telah logout.")
        st.rerun()
