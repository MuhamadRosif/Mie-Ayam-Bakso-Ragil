# =========================
# admin_app.py — Kasir Mas Ragil
# =========================
import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime

MENU_FILE = "kasir_mas_ragil/menu.json"
DATA_FILE = "kasir_mas_ragil/riwayat_penjualan.csv"
USERS_FILE = "kasir_mas_ragil/users.json"

ADMIN_USER = "admin"
ADMIN_PASS = "1234"

def load_menu():
    if os.path.exists(MENU_FILE):
        with open(MENU_FILE,"r",encoding="utf-8") as f:
            data = json.load(f)
            return data.get("makanan",{}), data.get("minuman",{})
    else:
        makanan = {"Mie Ayam":15000,"Bakso Urat":18000,"Mie Ayam Bakso":20000,"Bakso Telur":19000}
        minuman = {"Es Teh Manis":5000,"Es Jeruk":7000,"Teh Hangat":5000,"Jeruk Hangat":6000}
        with open(MENU_FILE,"w",encoding="utf-8") as f:
            json.dump({"makanan":makanan,"minuman":minuman}, f, ensure_ascii=False, indent=2)
        return makanan, minuman

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE,"r",encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_menu(makanan, minuman):
    with open(MENU_FILE,"w",encoding="utf-8") as f:
        json.dump({"makanan":makanan,"minuman":minuman}, f, ensure_ascii=False, indent=2)

def save_transaction(timestamp,nama,items_dict,subtotal,diskon,total,bayar=None,kembalian=None):
    record={"timestamp":timestamp,"nama":nama,"items":json.dumps(items_dict,ensure_ascii=False),
            "subtotal":subtotal,"diskon":diskon,"total":total,"bayar":bayar if bayar else "","kembalian":kembalian if kembalian else ""}
    df=pd.DataFrame([record])
    if os.path.exists(DATA_FILE):
        df.to_csv(DATA_FILE,mode="a",header=False,index=False,encoding="utf-8-sig")
    else:
        df.to_csv(DATA_FILE,index=False,encoding="utf-8-sig")

def build_struk(nama,pesanan_dict,total_before,diskon,total_bayar,uang_bayar=None,kembalian=None):
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
    if uang_bayar:
        t+=f"Bayar     : Rp {uang_bayar:,}\n"
        t+=f"Kembalian : Rp {kembalian:,}\n"
    t+="=============================\n"
    t+="Terima kasih! Salam, Mas Ragil 🍜\n"
    return t

def run_admin():
    st.set_page_config(page_title="Kasir Mas Ragil - Admin", page_icon="🍜", layout="wide")

    if "admin_login" not in st.session_state:
        st.session_state.admin_login = False

    # -----------------------
    # Login Admin
    # -----------------------
    if not st.session_state.admin_login:
        st.header("🔐 Login Admin")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Masuk"):
            if username==ADMIN_USER and password==ADMIN_PASS:
                st.session_state.admin_login = True
                st.rerun()
            else:
                st.error("Username / password salah.")
        st.stop()

    # -----------------------
    # Admin sudah login
    # -----------------------
    st.header("👑 Admin Kasir Mas Ragil")

    makanan, minuman = load_menu()
    users = load_users()

    # -----------------------
    # Menu Update / Tambah / Delete
    # -----------------------
    st.subheader("🛠️ Kelola Menu")
    st.write("Update / Hapus Menu Makanan")
    for item,harga in makanan.copy().items():
        col1,col2,col3 = st.columns([3,2,1])
        with col1:
            nama_baru = st.text_input(f"{item}", value=item, key=f"makanan-{item}")
        with col2:
            harga_baru = st.number_input(f"Harga {item}", value=harga, step=1000, key=f"harga-{item}")
        with col3:
            if st.button("❌", key=f"del-makanan-{item}"):
                del makanan[item]
                save_menu(makanan,minuman)
                st.success(f"{item} dihapus")
                st.experimental_rerun()
        if st.button("💾 Update", key=f"update-makanan-{item}"):
            makanan[nama_baru] = harga_baru
            if nama_baru != item:
                del makanan[item]
            save_menu(makanan,minuman)
            st.success(f"{nama_baru} diperbarui")
            st.experimental_rerun()

    st.write("Update / Hapus Menu Minuman")
    for item,harga in minuman.copy().items():
        col1,col2,col3 = st.columns([3,2,1])
        with col1:
            nama_baru = st.text_input(f"{item}", value=item, key=f"minum-{item}")
        with col2:
            harga_baru = st.number_input(f"Harga {item}", value=harga, step=1000, key=f"harga-minum-{item}")
        with col3:
            if st.button("❌", key=f"del-minum-{item}"):
                del minuman[item]
                save_menu(makanan,minuman)
                st.success(f"{item} dihapus")
                st.experimental_rerun()
        if st.button("💾 Update", key=f"update-minum-{item}"):
            minuman[nama_baru] = harga_baru
            if nama_baru != item:
                del minuman[item]
            save_menu(makanan,minuman)
            st.success(f"{nama_baru} diperbarui")
            st.experimental_rerun()

    # Tambah menu baru
    st.markdown("### ➕ Tambah Menu Baru")
    nama_baru = st.text_input("Nama Menu Baru", key="new_nama")
    harga_baru = st.number_input("Harga Menu Baru", min_value=0, step=1000, key="new_harga")
    jenis = st.selectbox("Jenis Menu", ["Makanan","Minuman"], key="new_jenis")
    if st.button("Tambah Menu"):
        if nama_baru.strip() and harga_baru>0:
            if jenis=="Makanan":
                makanan[nama_baru] = harga_baru
            else:
                minuman[nama_baru] = harga_baru
            save_menu(makanan,minuman)
            st.success(f"{nama_baru} berhasil ditambahkan")
            st.experimental_rerun()
        else:
            st.warning("Isi nama dan harga menu dengan benar.")

    # -----------------------
    # Laporan Transaksi
    # -----------------------
    st.subheader("📈 Laporan Penjualan")
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE, encoding="utf-8-sig")
        if not df.empty:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['total'] = df['total'].astype(int)
            st.dataframe(df[['timestamp','nama','subtotal','diskon','total','bayar','kembalian']])
            daily_revenue = df.groupby(df['timestamp'].dt.date)['total'].sum()
            st.bar_chart(daily_revenue)

            st.markdown("### ❌ Hapus Transaksi")
            for idx,row in df.iterrows():
                if st.button(f"Hapus {row['nama']} {row['timestamp']}", key=f"del-{idx}"):
                    df.drop(idx,inplace=True)
                    df.to_csv(DATA_FILE,index=False,encoding="utf-8-sig")
                    st.success("Transaksi dihapus")
                    st.experimental_rerun()
        else:
            st.info("Belum ada transaksi.")
    else:
        st.info("Belum ada transaksi.")

    # -----------------------
    # Logout
    # -----------------------
    if st.button("🚪 Logout Admin"):
        st.session_state.admin_login = False
        st.rerun()
