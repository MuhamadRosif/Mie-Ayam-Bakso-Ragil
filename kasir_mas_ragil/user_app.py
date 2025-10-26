import streamlit as st
import json, os

MENU_FILE = "kasir_mas_ragil/menu.json"
KERANJANG_FILE = "kasir_mas_ragil/keranjang.json"

def load_menu():
    if os.path.exists(MENU_FILE):
        with open(MENU_FILE,"r",encoding="utf-8") as f:
            data = json.load(f)
            return data.get("makanan",{}), data.get("minuman",{})
    return {}, {}

def load_keranjang():
    if os.path.exists(KERANJANG_FILE):
        with open(KERANJANG_FILE,"r",encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_keranjang(keranjang):
    with open(KERANJANG_FILE,"w",encoding="utf-8") as f:
        json.dump(keranjang,f,ensure_ascii=False,indent=2)

def run_user():
    st.markdown("""
    <style>
    .stApp {background: linear-gradient(180deg,#071026,#0b1440); color:#e6eef8;}
    .menu-card {background:#1b1b1b; padding:12px; border-radius:10px; box-shadow:0 2px 8px rgba(0,0,0,0.4); margin-bottom:10px;}
    .stButton>button {background: linear-gradient(90deg,#c62828,#9c1f1f); color:white; border:none; border-radius:6px; padding:6px 16px;}
    .stButton>button:hover {transform:scale(1.05);}
    </style>
    """, unsafe_allow_html=True)

    st.title("🍜 Kasir Mas Ragil — User")

    # ----------------------- SESSION -----------------------
    if "user_logged_in" not in st.session_state:
        st.session_state.user_logged_in = False
    if "username" not in st.session_state:
        st.session_state.username = ""

    # ----------------------- REGISTRASI -----------------------
    if not st.session_state.user_logged_in:
        st.subheader("📝 Registrasi / Login User")
        username = st.text_input("Username", key="reg_user")
        if st.button("Masuk / Daftar"):
            if username.strip():
                st.session_state.username = username.strip()
                st.session_state.user_logged_in = True
                st.success(f"Selamat datang, {st.session_state.username}!")
                st.rerun()
            else:
                st.warning("Masukkan username")
        return

    # ----------------------- LOAD DATA -----------------------
    makanan, minuman = load_menu()
    keranjang_all = load_keranjang()
    user_keranjang = keranjang_all.get(st.session_state.username, {})

    # ----------------------- MENU -----------------------
    st.subheader("🍽️ Menu Makanan")
    for item,harga in makanan.items():
        with st.container():
            st.markdown(f'<div class="menu-card"><b>{item}</b> — Rp {harga:,}</div>', unsafe_allow_html=True)
            col1,col2,col3 = st.columns([1,1,1])
            with col1:
                if st.button("-", key=f"{item}-minus"):
                    user_keranjang[item] = max(0, user_keranjang.get(item,0)-1)
            with col2:
                st.write(f"Qty: {user_keranjang.get(item,0)}")
            with col3:
                if st.button("+", key=f"{item}-plus"):
                    user_keranjang[item] = user_keranjang.get(item,0)+1

    st.subheader("🥤 Menu Minuman")
    for item,harga in minuman.items():
        with st.container():
            st.markdown(f'<div class="menu-card"><b>{item}</b> — Rp {harga:,}</div>', unsafe_allow_html=True)
            col1,col2,col3 = st.columns([1,1,1])
            with col1:
                if st.button("-", key=f"{item}-minus-minum"):
                    user_keranjang[item] = max(0, user_keranjang.get(item,0)-1)
            with col2:
                st.write(f"Qty: {user_keranjang.get(item,0)}")
            with col3:
                if st.button("+", key=f"{item}-plus-minum"):
                    user_keranjang[item] = user_keranjang.get(item,0)+1

    # ----------------------- KERANJANG -----------------------
    user_keranjang = {k:v for k,v in user_keranjang.items() if v>0}
    if user_keranjang:
        st.subheader("🛒 Keranjang Anda")
        total = 0
        for k,v in user_keranjang.items():
            harga_satuan = makanan.get(k,minuman.get(k,0))
            total += v*harga_satuan
            st.write(f"{k} x {v} = Rp {v*harga_satuan:,}")
        st.info(f"Total Pesanan (akan dibayar di Admin): Rp {total:,}")
    else:
        st.info("Keranjang kosong.")

    # ----------------------- SIMPAN KERANJANG -----------------------
    keranjang_all[st.session_state.username] = user_keranjang
    save_keranjang(keranjang_all)

    # ----------------------- RESET -----------------------
    if st.button("♻️ Reset Keranjang"):
        user_keranjang = {}
        keranjang_all[st.session_state.username] = {}
        save_keranjang(keranjang_all)
        st.success("Keranjang direset!")
        st.rerun()
