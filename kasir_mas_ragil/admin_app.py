# admin_app.py — final: sidebar = navigasi, konten di body
import streamlit as st
import json, os
from datetime import datetime

MENU_FILE = "kasir_mas_ragil/menu.json"
CHECKOUT_FILE = "kasir_mas_ragil/checkout.json"
LAPORAN_FILE = "kasir_mas_ragil/laporan.json"

def _load_json(path, default):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                return default
    return default

def _save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# page param is provided by app.py (sidebar navigation). If None, default to Dashboard
def run_admin(page=None):
    if page is None:
        page = "Dashboard"

    # ensure admin login state (app.py handles login but double-check)
    if "admin_login" not in st.session_state:
        st.session_state.admin_login = True if (st.session_state.get("role") == "Admin") else False

    if not st.session_state.admin_login:
        st.warning("Silakan login sebagai Admin dulu.")
        return

    # style header for admin page
    st.markdown("<h2>👨‍💼 Dashboard Admin — Rumah Makan Mas Ragil</h2>", unsafe_allow_html=True)
    st.divider()

    # Load menu/checkouts/laporan safely
    menu_data = _load_json(MENU_FILE, {"makanan": {}, "minuman": {}})
    checkout = _load_json(CHECKOUT_FILE, [])
    laporan = _load_json(LAPORAN_FILE, [])

    # PAGE: Dashboard (summary)
    if page in ("Dashboard", "Beranda", "Home"):
        st.subheader("Ringkasan")
        total_orders = len(checkout)
        total_revenue = sum([entry.get("total_bayar", 0) for entry in laporan]) if laporan else 0
        col1, col2 = st.columns(2)
        col1.metric("Pesanan Menunggu", total_orders)
        col2.metric("Total Pendapatan (laporan)", f"Rp {total_revenue:,}")
        st.markdown("---")
        st.markdown("### Daftar Pesanan Masuk")
        if checkout:
            for i, c in enumerate(checkout):
                st.markdown(f"**{i+1}. {c['username']} — {c['timestamp']}**")
                for item, qty in c["items"].items():
                    harga = c.get("subtotal", {}).get(item, 0)
                    st.write(f"- {item} x{qty} (Rp {harga:,})")
                st.info(f"Total: Rp {c.get('total_bayar',0):,}")
                if st.button("❌ Hapus Pesanan Ini", key=f"del_checkout_{i}"):
                    checkout.pop(i)
                    _save_json(CHECKOUT_FILE, checkout)
                    st.success("Pesanan dihapus.")
                    st.experimental_rerun()
        else:
            st.info("Belum ada pesanan masuk.")

    # PAGE: Pesanan (menampilkan detail dan delete)
    elif page == "Pesanan":
        st.subheader("Daftar Pesanan")
        if checkout:
            for i, c in enumerate(checkout):
                with st.expander(f"{i+1}. {c['username']} — {c['timestamp']}"):
                    for item, qty in c["items"].items():
                        harga = c.get("subtotal", {}).get(item, 0)
                        st.write(f"- {item} x{qty} (Rp {harga:,})")
                    st.info(f"Total: Rp {c.get('total_bayar',0):,}")
                    if st.button("❌ Hapus Pesanan", key=f"hapus_{i}"):
                        checkout.pop(i)
                        _save_json(CHECKOUT_FILE, checkout)
                        st.success("Pesanan dihapus.")
                        st.experimental_rerun()
        else:
            st.info("Belum ada pesanan.")

    # PAGE: Pembayaran
    elif page == "Pembayaran":
        st.subheader("Proses Pembayaran")
        if checkout:
            for i, c in enumerate(checkout):
                st.markdown(f"**{i+1}. {c['username']} — {c['timestamp']}**")
                st.write(f"Total: Rp {c.get('total_bayar',0):,}")
                uang = st.number_input(f"Uang diterima ({c['username']})", min_value=0, value=c.get('total_bayar',0), step=1000, key=f"uang_{i}")
                if st.button("Konfirmasi Bayar", key=f"konf_{i}"):
                    if uang >= c.get('total_bayar',0):
                        kembalian = uang - c.get('total_bayar',0)
                        st.success(f"Pembayaran sukses. Kembalian Rp {kembalian:,}")
                        # add to laporan
                        laporan.append({
                            "username": c["username"],
                            "total": c.get("total_bayar",0),
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        })
                        _save_json(LAPORAN_FILE, laporan)
                        # remove checkout
                        checkout.pop(i)
                        _save_json(CHECKOUT_FILE, checkout)
                        st.experimental_rerun()
                    else:
                        st.error("Uang kurang.")
        else:
            st.info("Tidak ada pesanan untuk diproses.")

    # PAGE: Laporan
    elif page == "Laporan":
        st.subheader("Laporan Penjualan")
        if laporan:
            st.dataframe(laporan)
            if st.button("🗑️ Hapus Semua Laporan"):
                if os.path.exists(LAPORAN_FILE):
                    os.remove(LAPORAN_FILE)
                st.success("Semua laporan dihapus.")
                st.experimental_rerun()
        else:
            st.info("Belum ada laporan.")

    # PAGE: Kelola Menu
    elif page == "Kelola Menu":
        st.subheader("Kelola Menu")
        makanan = menu_data.get("makanan", {})
        minuman = menu_data.get("minuman", {})

        st.markdown("### Makanan")
        for name, price in list(makanan.items()):
            col1, col2, col3 = st.columns([3,2,1])
            with col1:
                st.write(name)
            with col2:
                st.write(f"Rp {price:,}")
            with col3:
                if st.button("🗑️ Hapus", key=f"hapus_m_{name}"):
                    makanan.pop(name, None)
                    menu_data["makanan"] = makanan
                    _save_json(MENU_FILE, menu_data)
                    st.success("Makanan dihapus.")
                    st.experimental_rerun()

        st.markdown("#### Tambah Makanan")
        new_name = st.text_input("Nama Makanan", key="nm1")
        new_price = st.number_input("Harga", min_value=0, step=1000, key="np1")
        if st.button("Tambah Makanan"):
            if new_name.strip():
                makanan[new_name.strip()] = int(new_price)
                menu_data["makanan"] = makanan
                _save_json(MENU_FILE, menu_data)
                st.success("Makanan ditambahkan.")
                st.experimental_rerun()

        st.markdown("### Minuman")
        for name, price in list(minuman.items()):
            col1, col2, col3 = st.columns([3,2,1])
            with col1:
                st.write(name)
            with col2:
                st.write(f"Rp {price:,}")
            with col3:
                if st.button("🗑️ Hapus", key=f"hapus_d_{name}"):
                    minuman.pop(name, None)
                    menu_data["minuman"] = minuman
                    _save_json(MENU_FILE, menu_data)
                    st.success("Minuman dihapus.")
                    st.experimental_rerun()

        st.markdown("#### Tambah Minuman")
        new_name_d = st.text_input("Nama Minuman", key="nm2")
        new_price_d = st.number_input("Harga", min_value=0, step=1000, key="np2")
        if st.button("Tambah Minuman"):
            if new_name_d.strip():
                minuman[new_name_d.strip()] = int(new_price_d)
                menu_data["minuman"] = minuman
                _save_json(MENU_FILE, menu_data)
                st.success("Minuman ditambahkan.")
                st.experimental_rerun()

    else:
        st.info("Pilih menu di sidebar untuk mulai.")
