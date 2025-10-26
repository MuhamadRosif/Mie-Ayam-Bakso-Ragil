# user_app.py — final: sinkron tema, sidebar navigasi, konten di body
import streamlit as st
import json, os
from datetime import datetime

MENU_FILE = "kasir_mas_ragil/menu.json"
CHECKOUT_FILE = "kasir_mas_ragil/checkout.json"
USERS_FILE = "kasir_mas_ragil/users.json"
RIWAYAT_FILE = "kasir_mas_ragil/riwayat.json"

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

def run_user(page=None):
    if page is None:
        page = "Beranda"

    # session defaults
    if "user_login" not in st.session_state:
        st.session_state.user_login = True if (st.session_state.get("role") == "User") else False
    if "username" not in st.session_state:
        st.session_state.username = st.session_state.get("username","")

    # load storage
    menu_data = _load_json(MENU_FILE, {"makanan": {"Mie Ayam":15000, "Bakso":18000}, "minuman": {"Es Teh":5000}})
    users = _load_json(USERS_FILE, {})

    # if not logged as user, show info (app.py handles login)
    if not st.session_state.user_login:
        st.warning("Silakan login sebagai User dulu.")
        return

    st.header(f"🍜 Selamat datang, {st.session_state.username}")

    # load cart
    if "keranjang" not in st.session_state:
        st.session_state.keranjang = {}

    menu_makanan = menu_data.get("makanan", {})
    menu_minuman = menu_data.get("minuman", {})

    # BERANDA
    if page == "Beranda":
        st.subheader("Beranda")
        st.write("Selamat datang di Rumah Makan Mas Ragil. Pilih menu untuk memesan.")

    # MENU MAKANAN
    elif page == "Menu Makanan":
        st.subheader("Menu Makanan")
        for item, harga in menu_makanan.items():
            col1, col2, col3, col4 = st.columns([3,1,1,1])
            with col1: st.write(f"**{item}** — Rp {harga:,}")
            with col2:
                if st.button("-", key=f"{item}-minus"):
                    st.session_state.keranjang[item] = max(0, st.session_state.keranjang.get(item,0)-1)
            with col3:
                st.write(f"Qty: {st.session_state.keranjang.get(item,0)}")
            with col4:
                if st.button("+", key=f"{item}-plus"):
                    st.session_state.keranjang[item] = st.session_state.keranjang.get(item,0)+1

    # MENU MINUMAN
    elif page == "Menu Minuman":
        st.subheader("Menu Minuman")
        for item, harga in menu_minuman.items():
            col1, col2, col3, col4 = st.columns([3,1,1,1])
            with col1: st.write(f"**{item}** — Rp {harga:,}")
            with col2:
                if st.button("-", key=f"{item}-minus-d"):
                    st.session_state.keranjang[item] = max(0, st.session_state.keranjang.get(item,0)-1)
            with col3:
                st.write(f"Qty: {st.session_state.keranjang.get(item,0)}")
            with col4:
                if st.button("+", key=f"{item}-plus-d"):
                    st.session_state.keranjang[item] = st.session_state.keranjang.get(item,0)+1

    # KERANJANG
    elif page == "Keranjang":
        st.subheader("🛒 Keranjang Anda")
        keranjang_aktif = {k:v for k,v in st.session_state.keranjang.items() if v>0}
        if keranjang_aktif:
            total = 0
            for k,v in keranjang_aktif.items():
                price = menu_makanan.get(k, menu_minuman.get(k,0))
                subtotal = v*price
                st.write(f"- {k} x{v} = Rp {subtotal:,}")
                total += subtotal
            st.info(f"Total: Rp {total:,}")
            if st.button("Checkout"):
                checkout = _load_json(CHECKOUT_FILE, [])
                checkout.append({
                    "username": st.session_state.username,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "items": keranjang_aktif,
                    "subtotal": {k: menu_makanan.get(k, menu_minuman.get(k,0)) for k in keranjang_aktif},
                    "total_bayar": total
                })
                _save_json(CHECKOUT_FILE, checkout)
                # add riwayat
                riwayat = _load_json(RIWAYAT_FILE, [])
                riwayat.append({
                    "username": st.session_state.username,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "items": keranjang_aktif,
                    "total_bayar": total
                })
                _save_json(RIWAYAT_FILE, riwayat)
                st.success("Pesanan berhasil dibuat.")
                st.session_state.keranjang = {}
                st.experimental_rerun()
            if st.button("Kosongkan Keranjang"):
                st.session_state.keranjang = {}
                st.warning("Keranjang dikosongkan.")
        else:
            st.info("Keranjang kosong. Tambahkan menu di halaman Menu.")

    # RIWAYAT
    elif page == "Riwayat":
        st.subheader("Riwayat Pesanan")
        riwayat = _load_json(RIWAYAT_FILE, [])
        user_hist = [r for r in riwayat if r.get("username")==st.session_state.username]
        if user_hist:
            for r in user_hist:
                with st.expander(f"{r['timestamp']} — Rp {r['total_bayar']:,}"):
                    for it, q in r["items"].items():
                        st.write(f"- {it} x{q}")
        else:
            st.info("Belum ada riwayat pesanan.")

    # TENTANG
    elif page == "Tentang":
        st.subheader("Tentang")
        st.write("Aplikasi kasir sederhana Rumah Makan Mas Ragil — built with Streamlit.")

    else:
        st.info("Pilih menu di sidebar untuk mulai.")
