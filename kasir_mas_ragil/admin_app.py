import streamlit as st
import json, os
from datetime import datetime

MENU_FILE = "kasir_mas_ragil/menu.json"
KERANJANG_FILE = "kasir_mas_ragil/keranjang.json"
DATA_FILE = "kasir_mas_ragil/riwayat_penjualan.csv"

ADMIN_USER = "admin"
ADMIN_PASS = "1234"

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

def save_transaction(timestamp,nama,items_dict,subtotal,total):
    import pandas as pd
    record={"timestamp":timestamp,"nama":nama,"items":json.dumps(items_dict,ensure_ascii=False),
            "subtotal":subtotal,"total":total}
    df=pd.DataFrame([record])
    if os.path.exists(DATA_FILE):
        df.to_csv(DATA_FILE,mode="a",header=False,index=False,encoding="utf-8-sig")
    else:
        df.to_csv(DATA_FILE,index=False,encoding="utf-8-sig")

def run_admin():
    st.title("🍜 Kasir Mas Ragil — Admin")

    if "admin_login" not in st.session_state:
        st.session_state.admin_login = False

    if not st.session_state.admin_login:
        username = st.text_input("Username Admin", key="admin_user")
        password = st.text_input("Password", type="password", key="admin_pass")
        if st.button("Login"):
            if username==ADMIN_USER and password==ADMIN_PASS:
                st.session_state.admin_login = True
                st.success("Login berhasil!")
                st.rerun()
            else:
                st.error("Username atau password salah")
        return

    # ------------------- Lihat Keranjang User -------------------
    st.header("📋 Pesanan User")
    keranjang_all = load_keranjang()
    makanan,minuman = load_menu()
    if not keranjang_all:
        st.info("Belum ada pesanan dari user.")
        return

    for user,items in keranjang_all.items():
        st.subheader(f"User: {user}")
        total = 0
        for k,v in items.items():
            h = makanan.get(k, minuman.get(k,0))
            total += v*h
            st.write(f"{k} x {v} = Rp {v*h:,}")
        st.write(f"**Total Pesanan: Rp {total:,}**")
        if st.button(f"Proses Pembayaran {user}", key=f"pay-{user}"):
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            save_transaction(timestamp,user,items,total,total)
            del keranjang_all[user]
            with open(KERANJANG_FILE,"w",encoding="utf-8") as f:
                json.dump(keranjang_all,f,ensure_ascii=False,indent=2)
            st.success(f"Pesanan {user} berhasil dibayar dan dicatat!")
            st.experimental_rerun()
