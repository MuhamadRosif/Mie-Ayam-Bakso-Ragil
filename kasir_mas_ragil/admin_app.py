import streamlit as st
import json, os
from datetime import datetime

ADMIN_USER = "admin"
ADMIN_PASS = "1234"
MENU_FILE = "kasir_mas_ragil/menu.json"
KERANJANG_FILE = "kasir_mas_ragil/keranjang.json"
RIWAYAT_FILE = "kasir_mas_ragil/riwayat_penjualan.csv"

def load_menu():
    if os.path.exists(MENU_FILE):
        with open(MENU_FILE,"r",encoding="utf-8") as f:
            data = json.load(f)
            return data.get("makanan",{}), data.get("minuman",{})
    return {}, {}

def load_keranjang_all():
    if os.path.exists(KERANJANG_FILE):
        with open(KERANJANG_FILE,"r",encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_riwayat(transaksi):
    import pandas as pd
    df = pd.DataFrame([transaksi])
    if os.path.exists(RIWAYAT_FILE):
        df.to_csv(RIWAYAT_FILE, mode="a", header=False, index=False, encoding="utf-8-sig")
    else:
        df.to_csv(RIWAYAT_FILE, index=False, encoding="utf-8-sig")

def run_admin():
    st.markdown("""
    <style>
    .stApp {background: linear-gradient(180deg,#071026,#0b1440); color:#e6eef8;}
    .stButton>button {background: linear-gradient(90deg,#c62828,#9c1f1f); color:white; border:none; border-radius:6px; padding:6px 16px;}
    .stButton>button:hover {transform:scale(1.05);}
    </style>
    """, unsafe_allow_html=True)

    if "admin_logged_in" not in st.session_state:
        st.session_state.admin_logged_in = False

    if not st.session_state.admin_logged_in:
        st.subheader("🔐 Login Admin")
        username = st.text_input("Username", key="admin_user")
        password = st.text_input("Password", type="password", key="admin_pass")
        if st.button("Masuk"):
            if username==ADMIN_USER and password==ADMIN_PASS:
                st.session_state.admin_logged_in = True
                st.success("Admin login berhasil!")
                st.rerun()
            else:
                st.error("Username / password salah.")
        return

    st.title("🍜 Kasir Mas Ragil — Admin")

    # ----------------------- LOAD DATA -----------------------
    makanan, minuman = load_menu()
    keranjang_all = load_keranjang_all()

    # ----------------------- TAMPILKAN KERANJANG USER -----------------------
    st.subheader("🛒 Semua Pesanan User")
    for user, items in keranjang_all.items():
        if not items: continue
        st.markdown(f"### {user}")
        total = 0
        for k,v in items.items():
            harga = makanan.get(k, minuman.get(k,0))
            total += v*harga
            st.write(f"{k} x {v} = Rp {v*harga:,}")
        st.info(f"Total: Rp {total:,}")

        uang = st.number_input(f"Uang diterima {user}", min_value=0, value=total, step=1000, key=f"uang-{user}")
        if st.button(f"Bayar {user}", key=f"bayar-{user}"):
            st.success(f"Pembayaran {user} berhasil! Kembalian: Rp {uang-total:,}")
            # Simpan riwayat
            save_riwayat({
                "user": user,
                "total": total,
                "uang": uang,
                "kembalian": uang-total,
                "waktu": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            # Reset keranjang user
            keranjang_all[user] = {}
            with open(KERANJANG_FILE,"w",encoding="utf-8") as f:
                json.dump(keranjang_all,f,ensure_ascii=False,indent=2)
            st.rerun()
