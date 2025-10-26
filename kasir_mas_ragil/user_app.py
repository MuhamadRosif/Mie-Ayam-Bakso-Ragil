# =====================================================
# user_app.py — User Kasir Mas Ragil
# =====================================================
import streamlit as st
import json
import os
from datetime import datetime

MENU_FILE = "kasir_mas_ragil/menu.json"
CHECKOUT_FILE = "kasir_mas_ragil/checkout.json"
USERS_FILE = "kasir_mas_ragil/users.json"

def run_user():
    st.title("🍜 Kasir Mas Ragil — User")

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
    # Registrasi / Login
    # -----------------------
    if not st.session_state.user_login:
        st.subheader("🔑 Login / Registrasi User")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Login")
            login_username = st.text_input("Username Login", key="login_user")
            login_password = st.text_input("Password Login", type="password", key="login_pass")
            if st.button("Login"):
                if login_username in users_data and users_data[login_username] == login_password:
                    st.session_state.user_login = True
                    st.session_state.username = login_username
                    st.success(f"Login berhasil! Selamat datang, {login_username}")
                    st.rerun()
                else:
                    st.error("Username atau password salah.")

        with col2:
            st.markdown("### Registrasi")
            reg_username = st.text_input("Username Baru", key="reg_user")
            reg_password = st.text_input("Password Baru", type="password", key="reg_pass")
            if st.button("Daftar"):
                if reg_username.strip() and reg_password.strip():
                    if reg_username in users_data:
                        st.warning("Username sudah terdaftar.")
                    else:
                        users_data[reg_username] = reg_password
                        with open(USERS_FILE, "w", encoding="utf-8") as f:
                            json.dump(users_data, f, ensure_ascii=False, indent=2)
                        st.success("Registrasi berhasil! Silahkan login.")
                        st.rerun()
                else:
                    st.warning("Isi username dan password.")

        return

    # -----------------------
    # Load menu
    # -----------------------
    if os.path.exists(MENU_FILE):
        with open(MENU_FILE, "r", encoding="utf-8") as f:
            menu_data = json.load(f)
            menu_makanan = menu_data.get("makanan", {})
            menu_minuman = menu_data.get("minuman", {})
    else:
        menu_makanan = {}
        menu_minuman = {}

    # -----------------------
    # Logout
    # -----------------------
    if st.button("🚪 Logout"):
        st.session_state.user_login = False
        st.session_state.username = ""
        st.session_state.keranjang = {}
        st.success("Logout berhasil!")
        st.rerun()

    # -----------------------
    # Menu Pesan
    # -----------------------
    st.header(f"🍽️ Selamat Datang, {st.session_state.username}!")
    st.subheader("Menu Makanan")
    for item, harga in menu_makanan.items():
        col1, col2, col3, col4 = st.columns([3,1,1,2])
        with col1: st.write(f"**{item}** (Rp {harga:,})")
        with col2:
            if st.button("-", key=f"{item}-minus"): st.session_state.keranjang[item] = max(0, st.session_state.keranjang.get(item,0)-1)
        with col3: st.write(f"Qty: {st.session_state.keranjang.get(item,0)}")
        with col4:
            if st.button("+", key=f"{item}-plus"): st.session_state.keranjang[item] = st.session_state.keranjang.get(item,0)+1

    st.subheader("Menu Minuman")
    for item, harga in menu_minuman.items():
        col1, col2, col3, col4 = st.columns([3,1,1,2])
        with col1: st.write(f"**{item}** (Rp {harga:,})")
        with col2:
            if st.button("-", key=f"{item}-minus-minum"): st.session_state.keranjang[item] = max(0, st.session_state.keranjang.get(item,0)-1)
        with col3: st.write(f"Qty: {st.session_state.keranjang.get(item,0)}")
        with col4:
            if st.button("+", key=f"{item}-plus-minum"): st.session_state.keranjang[item] = st.session_state.keranjang.get(item,0)+1

    # -----------------------
    # Keranjang
    # -----------------------
    keranjang_aktif = {k:v for k,v in st.session_state.keranjang.items() if v>0}
    if keranjang_aktif:
        st.markdown("### 🛒 Keranjang Saat Ini:")
        total_bayar = 0
        subtotal_dict = {}
        for k,v in keranjang_aktif.items():
            harga_satuan = menu_makanan.get(k, menu_minuman.get(k,0))
            subtotal = v * harga_satuan
            subtotal_dict[k] = subtotal
            total_bayar += subtotal
            st.write(f"{k} x {v} = Rp {subtotal:,}")
        st.info(f"Total: Rp {total_bayar:,}")

        if st.button("📝 Checkout"):
            # Simpan ke checkout.json
            if os.path.exists(CHECKOUT_FILE):
                with open(CHECKOUT_FILE, "r", encoding="utf-8") as f:
                    data_checkout = json.load(f)
            else:
                data_checkout = []

            data_checkout.append({
                "username": st.session_state.username,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "items": keranjang_aktif,
                "subtotal": subtotal_dict,
                "total_bayar": total_bayar
            })

            with open(CHECKOUT_FILE, "w", encoding="utf-8") as f:
                json.dump(data_checkout, f, ensure_ascii=False, indent=2)

            st.success("✅ Pesanan berhasil di-checkout! Silahkan admin proses pembayaran.")
            st.session_state.keranjang = {}
            st.experimental_rerun()
        if st.button("❌ Hapus Keranjang"):
            st.session_state.keranjang = {}
            st.success("Keranjang dihapus.")
    else:
        st.info("Belum ada item di keranjang.")
