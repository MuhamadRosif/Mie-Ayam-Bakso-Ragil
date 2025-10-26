import streamlit as st
import json, os
from datetime import datetime

MENU_FILE = "kasir_mas_ragil/menu.json"
CHECKOUT_FILE = "kasir_mas_ragil/checkout.json"
USERS_FILE = "kasir_mas_ragil/users.json"

def run_user():
    if "user_login" not in st.session_state:
        st.session_state.user_login=False
    if "username" not in st.session_state:
        st.session_state.username=""
    if "keranjang" not in st.session_state:
        st.session_state.keranjang={}
    if "menu_open" not in st.session_state:
        st.session_state.menu_open=True

    # Load users
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE,"r",encoding="utf-8") as f:
            users_data=json.load(f)
    else:
        users_data={}

    # Login / Registrasi
    if not st.session_state.user_login:
        st.subheader("🔑 Login / Registrasi User")
        col1,col2=st.columns(2)
        with col1:
            st.markdown("### Login")
            login_username = st.text_input("Username Login", key="login_user")
            login_password = st.text_input("Password Login", type="password", key="login_pass")
            if st.button("Login"):
                if login_username in users_data and users_data[login_username] == login_password:
                    st.session_state.user_login=True
                    st.session_state.username=login_username
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
                        with open(USERS_FILE,"w",encoding="utf-8") as f:
                            json.dump(users_data,f,ensure_ascii=False,indent=2)
                        st.success("Registrasi berhasil! Silahkan login.")
                        st.rerun()
                else:
                    st.warning("Isi username dan password.")
        return

    # Toggle sidebar
    toggle_col1,toggle_col2=st.columns([9,1])
    with toggle_col2:
        if st.button("☰"):
            st.session_state.menu_open = not st.session_state.menu_open

    # Sidebar menu
    if st.session_state.menu_open:
        st.sidebar.title(f"👤 {st.session_state.username}")
        page = st.sidebar.selectbox("Menu User", ["Beranda","Menu","Keranjang","Riwayat","Tentang"])
        if st.sidebar.button("🚪 Logout"):
            st.session_state.user_login=False
            st.session_state.username=""
            st.session_state.keranjang={}
            st.success("Logout berhasil!")
            st.experimental_rerun()
    else:
        page = "Beranda"

    st.title(f"🍜 User Dashboard — {st.session_state.username}")

    # Load menu
    if os.path.exists(MENU_FILE):
        with open(MENU_FILE,"r",encoding="utf-8") as f:
            menu_data=json.load(f)
            menu_makanan=menu_data.get("makanan",{})
            menu_minuman=menu_data.get("minuman",{})
    else:
        menu_makanan={}
        menu_minuman={}

    # --- Halaman User ---
    if page=="Beranda":
        st.subheader("Selamat datang di Kasir Mas Ragil!")
        st.write("Silahkan pilih menu di sidebar untuk mulai pesan.")

    elif page=="Tentang":
        st.subheader("Tentang Kasir Mas Ragil")
        st.write("Aplikasi kasir sederhana untuk makanan dan minuman. Dibuat menggunakan Streamlit.")

    elif page=="Menu":
        st.subheader("🍽️ Menu Makanan")
        for item,harga in menu_makanan.items():
            col1,col2,col3,col4=st.columns([3,1,1,2])
            with col1: st.write(f"**{item}** (Rp {harga:,})")
            with col2:
                if st.button("-", key=f"{item}-minus"): st.session_state.keranjang[item]=max(0,st.session_state.keranjang.get(item,0)-1)
            with col3: st.write(f"Qty: {st.session_state.keranjang.get(item,0)}")
            with col4:
                if st.button("+", key=f"{item}-plus"): st.session_state.keranjang[item]=st.session_state.keranjang.get(item,0)+1

        st.subheader("🥤 Menu Minuman")
        for item,harga in menu_minuman.items():
            col1,col2,col3,col4=st.columns([3,1,1,2])
            with col1: st.write(f"**{item}** (Rp {harga:,})")
            with col2:
                if st.button("-", key=f"{item}-minus-minum"): st.session_state.keranjang[item]=max(0,st.session_state.keranjang.get(item,0)-1)
            with col3: st.write(f"Qty: {st.session_state.keranjang.get(item,0)}")
            with col4:
                if st.button("+", key=f"{item}-plus-minum"): st.session_state.keranjang[item]=st.session_state.keranjang.get(item,0)+1

    elif page=="Keranjang":
        keranjang_aktif={k:v for k,v in st.session_state.keranjang.items() if v>0}
        if keranjang_aktif:
            st.subheader("🛒 Keranjang Saat Ini")
            total_bayar=0
            for k,v in keranjang_aktif.items():
                harga_satuan = menu_makanan.get(k,menu_minuman.get(k,0))
                subtotal = v*harga_satuan
                total_bayar+=subtotal
                st.write(f"{k} x {v} = Rp {subtotal:,}")
            st.info(f"Total: Rp {total_bayar:,}")

            if st.button("📝 Checkout"):
                if os.path.exists(CHECKOUT_FILE):
                    with open(CHECKOUT_FILE,"r",encoding="utf-8") as f:
                        data_checkout=json.load(f)
                else:
                    data_checkout=[]
                data_checkout.append({
                    "username":st.session_state.username,
                    "timestamp":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "items":keranjang_aktif,
                    "total":total_bayar
                })
                with open(CHECKOUT_FILE,"w",encoding="utf-8") as f:
                    json.dump(data_checkout,f,ensure_ascii=False,indent=2)
                st.success("✅ Pesanan berhasil di-checkout!")
                st.session_state.keranjang={}
                st.experimental_rerun()
            if st.button("❌ Hapus Keranjang"):
                st.session_state.keranjang={}
                st.success("Keranjang dihapus.")
        else:
            st.info("Belum ada item di keranjang.")

    elif page=="Riwayat":
        st.subheader("📜 Riwayat Pesanan")
        if os.path.exists(CHECKOUT_FILE):
            with open(CHECKOUT_FILE,"r",encoding="utf-8") as f:
                data_checkout=json.load(f)
            user_history=[c for c in data_checkout if c["username"]==st.session_state.username]
            if user_history:
                for co in user_history:
                    st.markdown(f"**{co['timestamp']}**")
                    for item,qty in co["items"].items():
                        st.write(f"{item} x {qty}")
                    st.write(f"Total: Rp {co['total']:,}")
            else:
                st.info("Belum ada riwayat pesanan.")
        else:
            st.info("Belum ada riwayat pesanan.")
