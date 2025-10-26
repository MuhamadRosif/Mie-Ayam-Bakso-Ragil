# kasir_mas_ragil/admin_app.py
import streamlit as st
import os
import json
import pandas as pd
from datetime import datetime

MENU_FILE = "kasir_mas_ragil/menu.json"
CHECKOUT_FILE = "kasir_mas_ragil/checkout.json"
DATA_FILE = "kasir_mas_ragil/riwayat_penjualan.csv"

# -----------------------
# Helper
# -----------------------
def load_menu():
    if os.path.exists(MENU_FILE):
        with open(MENU_FILE,"r",encoding="utf-8") as f:
            return json.load(f)
    else:
        return {"makanan":{},"minuman":{}}

def save_menu(menu):
    with open(MENU_FILE,"w",encoding="utf-8") as f:
        json.dump(menu,f,ensure_ascii=False,indent=2)

def save_transaction(timestamp,nama,items_dict,subtotal,diskon,total,bayar,kembalian):
    record={"timestamp":timestamp,"nama":nama,"items":json.dumps(items_dict,ensure_ascii=False),
            "subtotal":subtotal,"diskon":diskon,"total":total,"bayar":bayar,"kembalian":kembalian}
    df=pd.DataFrame([record])
    if os.path.exists(DATA_FILE):
        df.to_csv(DATA_FILE,mode="a",header=False,index=False,encoding="utf-8-sig")
    else:
        df.to_csv(DATA_FILE,index=False,encoding="utf-8-sig")

def build_struk(nama,pesanan_dict,total_before,diskon,total_bayar,uang_bayar,kembalian):
    t="===== STRUK PEMBAYARAN =====\n"
    t+=f"Tanggal : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    t+=f"Nama    : {nama}\n"
    t+="-----------------------------\n"
    for it,subtotal in pesanan_dict.items():
        t+=f"{it:<20} Rp {subtotal:,}\n"
    t+="-----------------------------\n"
    t+=f"Sub Total : Rp {total_before:,}\n"
    t+=f"Diskon    : Rp {diskon:,}\n"
    t+=f"Total     : Rp {total_bayar:,}\n"
    t+=f"Bayar     : Rp {uang_bayar:,}\n"
    t+=f"Kembalian : Rp {kembalian:,}\n"
    t+="=============================\n"
    t+="Terima kasih! Salam, Mas Ragil 🍜\n"
    return t

# -----------------------
# Admin App
# -----------------------
def run_admin():
    st.header("🛠️ Admin Panel — Kasir Mas Ragil")

    # Login admin
    if "admin_login" not in st.session_state:
        st.session_state.admin_login = False
    if not st.session_state.admin_login:
        st.subheader("🔐 Login Admin")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Masuk"):
            if username=="admin" and password=="1234":
                st.session_state.admin_login = True
                st.success("Login berhasil!")
                st.rerun()
            else:
                st.error("Username atau password salah.")
        return

    menu = load_menu()
    st.subheader("📋 Menu Navigasi Admin")
    page = st.radio("", ["Pesanan User","Pembayaran","Admin Menu","Laporan"], index=0)

    # ------------------ PESANAN USER ------------------
    if page=="Pesanan User":
        st.header("📦 Checkout User")
        if os.path.exists(CHECKOUT_FILE):
            with open(CHECKOUT_FILE,"r",encoding="utf-8") as f:
                all_checkout = json.load(f)
            if all_checkout:
                for idx,co in enumerate(all_checkout):
                    st.markdown(f"**{co['username']} — {co['timestamp']}**")
                    total = 0
                    for k,v in co["cart"].items():
                        harga = menu["makanan"].get(k, menu["minuman"].get(k,0))
                        subtotal = harga*v
                        total += subtotal
                        st.write(f"{k} x {v} = Rp {subtotal:,}")
                    st.info(f"Total Pesanan: Rp {total:,}")
                    if st.button("Proses Pembayaran", key=f"pay-{idx}"):
                        st.session_state.pay_user = co
                        st.session_state.pay_user_idx = idx
                        st.rerun()
            else:
                st.info("Belum ada pesanan yang di checkout.")
        else:
            st.info("Belum ada pesanan yang di checkout.")

    # ------------------ PEMBAYARAN ------------------
    if page=="Pembayaran" and "pay_user" in st.session_state:
        co = st.session_state.pay_user
        st.subheader(f"💳 Pembayaran — {co['username']}")
        subtotal = sum(menu["makanan"].get(k,menu["minuman"].get(k,0))*v for k,v in co["cart"].items())
        diskon = int(subtotal*0.05) if subtotal>=100000 else 0
        total_bayar = subtotal - diskon
        st.write(f"Sub Total : Rp {subtotal:,}")
        st.write(f"Diskon    : Rp {diskon:,}")
        st.write(f"Total     : Rp {total_bayar:,}")
        uang = st.number_input("Uang Diterima", min_value=0, value=total_bayar, step=1000)
        if st.button("Bayar"):
            if uang>=total_bayar:
                kembalian = uang-total_bayar
                st.success(f"Pembayaran berhasil! Kembalian Rp {kembalian:,}")
                pesanan_subtotal = {k:v*menu["makanan"].get(k,menu["minuman"].get(k,0)) for k,v in co["cart"].items()}
                struk = build_struk(co['username'],pesanan_subtotal,subtotal,diskon,total_bayar,uang,kembalian)
                st.text_area("🧾 Struk", struk, height=300)
                save_transaction(datetime.now().strftime("%Y-%m-%d %H:%M:%S"),co['username'],co['cart'],subtotal,diskon,total_bayar,uang,kembalian)
                # hapus dari checkout
                with open(CHECKOUT_FILE,"r",encoding="utf-8") as f:
                    checkout_list = json.load(f)
                checkout_list.pop(st.session_state.pay_user_idx)
                with open(CHECKOUT_FILE,"w",encoding="utf-8") as f:
                    json.dump(checkout_list,f,ensure_ascii=False,indent=2)
                del st.session_state.pay_user
                del st.session_state.pay_user_idx
                st.success("Riwayat transaksi tersimpan.")
                st.rerun()
            else:
                st.error("Uang kurang!")

    # ------------------ ADMIN MENU ------------------
    if page=="Admin Menu":
        st.subheader("🛠️ Update / Tambah / Hapus Menu")
        # Makanan
        st.markdown("### 🍽️ Menu Makanan")
        for item,harga in menu["makanan"].copy().items():
            col1,col2,col3 = st.columns([3,2,1])
            with col1: nama_baru = st.text_input(item,value=item,key=f"m-{item}")
            with col2: harga_baru = st.number_input(item,value=harga,step=1000,key=f"h-{item}")
            with col3:
                if st.button("❌", key=f"del-{item}"):
                    del menu["makanan"][item]
                    save_menu(menu)
                    st.experimental_rerun()
            if st.button("💾 Update", key=f"upd-{item}"):
                menu["makanan"][nama_baru] = harga_baru
                if nama_baru!=item: del menu["makanan"][item]
                save_menu(menu)
                st.rerun()
        # Minuman
        st.markdown("### 🥤 Menu Minuman")
        for item,harga in menu["minuman"].copy().items():
            col1,col2,col3 = st.columns([3,2,1])
            with col1: nama_baru = st.text_input(item,value=item,key=f"mm-{item}")
            with col2: harga_baru = st.number_input(item,value=harga,step=1000,key=f"hm-{item}")
            with col3:
                if st.button("❌", key=f"delm-{item}"):
                    del menu["minuman"][item]
                    save_menu(menu)
                    st.rerun()
            if st.button("💾 Update", key=f"updm-{item}"):
                menu["minuman"][nama_baru] = harga_baru
                if nama_baru!=item: del menu["minuman"][item]
                save_menu(menu)
                st.rerun()
        # Tambah menu baru
        st.markdown("### ➕ Tambah Menu Baru")
        nama_baru = st.text_input("Nama Item Baru", key="new_item")
        kategori = st.selectbox("Kategori", ["makanan","minuman"], key="new_kategori")
        harga_baru = st.number_input("Harga", min_value=1000, step=1000, key="new_harga")
        if st.button("Tambah Menu"):
            if nama_baru.strip()!="":
                menu[kategori][nama_baru] = harga_baru
                save_menu(menu)
                st.success(f"{nama_baru} ditambahkan!")
                st.rerun()

    # ------------------ LAPORAN ------------------
    if page=="Laporan":
        st.subheader("📊 Riwayat Transaksi")
        if os.path.exists(DATA_FILE):
            df = pd.read_csv(DATA_FILE,encoding="utf-8-sig")
            if not df.empty:
                st.dataframe(df)
                if st.button("❌ Hapus Laporan"):
                    os.remove(DATA_FILE)
                    st.success("Laporan terhapus.")
                    st.rerun()
            else:
                st.info("Belum ada laporan transaksi.")
        else:
            st.info("Belum ada laporan transaksi.")
