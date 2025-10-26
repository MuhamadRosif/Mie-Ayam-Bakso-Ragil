import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

MENU_FILE = "kasir_mas_ragil/menu.json"
DATA_FILE = "kasir_mas_ragil/riwayat_penjualan.csv"

ADMIN_USER = "admin"
ADMIN_PASS = "1234"

def run_admin():
    st.title("🛠️ Admin Panel — Kasir Mas Ragil")
    
    # Session state
    if "admin_login" not in st.session_state:
        st.session_state.admin_login = False
    
    if not st.session_state.admin_login:
        username = st.text_input("Username Admin")
        password = st.text_input("Password Admin", type="password")
        if st.button("Login Admin", key="admin_login_btn"):
            if username == ADMIN_USER and password == ADMIN_PASS:
                st.session_state.admin_login = True
                st.experimental_rerun()
            else:
                st.error("Username atau password salah.")
        return
    
    # ---------------- Menu Admin ----------------
    st.subheader("🍽️ Menu Management")
    # Load menu
    if os.path.exists(MENU_FILE):
        with open(MENU_FILE,"r",encoding="utf-8") as f:
            menu_data = json.load(f)
    else:
        menu_data = {"makanan": {}, "minuman": {}}
    
    # Update/Hapus Menu
    for category in ["makanan", "minuman"]:
        st.markdown(f"### {category.capitalize()}")
        for item, harga in menu_data.get(category, {}).copy().items():
            col1,col2,col3 = st.columns([3,2,1])
            with col1:
                new_name = st.text_input(f"{item}", value=item, key=f"{category}-{item}")
            with col2:
                new_price = st.number_input(f"Harga {item}", value=harga, step=1000, key=f"harga-{category}-{item}")
            with col3:
                if st.button("❌", key=f"del-{category}-{item}"):
                    del menu_data[category][item]
                    with open(MENU_FILE,"w",encoding="utf-8") as f:
                        json.dump(menu_data,f,ensure_ascii=False,indent=2)
                    st.success(f"{item} dihapus")
                    st.experimental_rerun()
            
            if st.button("💾 Update", key=f"update-{category}-{item}"):
                menu_data[category][new_name] = new_price
                if new_name != item:
                    del menu_data[category][item]
                with open(MENU_FILE,"w",encoding="utf-8") as f:
                    json.dump(menu_data,f,ensure_ascii=False,indent=2)
                st.success(f"{new_name} diperbarui")
                st.experimental_rerun()
    
    # Tambah Menu Baru
    st.markdown("### ➕ Tambah Menu Baru")
    new_item = st.text_input("Nama Menu Baru", key="new_item")
    new_price = st.number_input("Harga Menu Baru", min_value=0, step=1000, key="new_price")
    jenis = st.selectbox("Jenis Menu", ["Makanan","Minuman"])
    if st.button("Tambah Menu", key="add_new"):
        if new_item.strip() and new_price>0:
            kategori = "makanan" if jenis=="Makanan" else "minuman"
            menu_data[kategori][new_item] = new_price
            with open(MENU_FILE,"w",encoding="utf-8") as f:
                json.dump(menu_data,f,ensure_ascii=False,indent=2)
            st.success(f"{new_item} berhasil ditambahkan")
            st.experimental_rerun()
        else:
            st.warning("Isi nama dan harga dengan benar.")

    # ---------------- Pesanan User ----------------
    st.subheader("🛒 Pesanan User")
    if os.path.exists("kasir_mas_ragil/user_pesanan.json"):
        with open("kasir_mas_ragil/user_pesanan.json","r",encoding="utf-8") as f:
            pesanan_user = json.load(f)
    else:
        pesanan_user = {}
    
    if pesanan_user:
        total_bayar_all = 0
        for user,pesanan in pesanan_user.items():
            st.markdown(f"**{user}**")
            subtotal = sum(menu_data.get("makanan",{}).get(k,menu_data.get("minuman",{}).get(k,0))*v for k,v in pesanan.items())
            st.write(pesanan)
            st.write(f"Subtotal: Rp {subtotal:,}")
            uang = st.number_input(f"Uang diterima {user}", min_value=0, value=subtotal, step=1000, key=f"bayar-{user}")
            if st.button(f"Proses Bayar {user}", key=f"proses-{user}"):
                kembalian = uang - subtotal
                st.success(f"{user} dibayar, kembalian: Rp {kembalian:,}")
                # Simpan transaksi
                record = {"timestamp":datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "nama":user,
                          "items":pesanan, "subtotal":subtotal, "diskon":0, "total":subtotal,
                          "bayar":uang, "kembalian":kembalian}
                df = pd.DataFrame([record])
                if os.path.exists(DATA_FILE):
                    df.to_csv(DATA_FILE,mode="a",header=False,index=False,encoding="utf-8-sig")
                else:
                    df.to_csv(DATA_FILE,index=False,encoding="utf-8-sig")
                # Hapus pesanan user setelah dibayar
                del pesanan_user[user]
                with open("kasir_mas_ragil/user_pesanan.json","w",encoding="utf-8") as f:
                    json.dump(pesanan_user,f,ensure_ascii=False,indent=2)
                st.experimental_rerun()
    else:
        st.info("Belum ada pesanan user.")

    # ---------------- Laporan ----------------
    st.subheader("📈 Laporan Penjualan")
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE, encoding="utf-8-sig")
        st.dataframe(df)
        daily = df.groupby(df['timestamp'].str[:10])['total'].sum()
        st.bar_chart(daily)
        # Hapus transaksi
        for idx,row in df.iterrows():
            if st.button(f"Hapus {row['nama']} {row['timestamp']}", key=f"del-report-{idx}"):
                df.drop(idx,inplace=True)
                df.to_csv(DATA_FILE,index=False,encoding="utf-8-sig")
                st.success("Transaksi dihapus")
                st.experimental_rerun()
    else:
        st.info("Belum ada transaksi.")
