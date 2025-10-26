import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

DATA_FILE = "riwayat_penjualan.csv"
MENU_FILE = "menu.json"
CHECKOUT_FILE = "checkout.json"

def run_admin():
    st.header("🛠️ Admin Panel — Kasir Mas Ragil")

    # ----------------------
    # Admin Login
    # ----------------------
    if "admin_login" not in st.session_state:
        st.session_state.admin_login = False

    ADMIN_USER = "admin"
    ADMIN_PASS = "1234"

    if not st.session_state.admin_login:
        username = st.text_input("Username Admin")
        password = st.text_input("Password Admin", type="password")
        if st.button("Login"):
            if username == ADMIN_USER and password == ADMIN_PASS:
                st.session_state.admin_login = True
                st.success("Login berhasil!")
                st.rerun()
            else:
                st.error("Username atau password salah.")
        st.stop()

    # ----------------------
    # Load Menu
    # ----------------------
    if os.path.exists(MENU_FILE):
        with open(MENU_FILE,"r",encoding="utf-8") as f:
            menu = json.load(f)
    else:
        menu = {"makanan":{}, "minuman":{}}

    # ----------------------
    # Load Checkout
    # ----------------------
    if os.path.exists(CHECKOUT_FILE):
        with open(CHECKOUT_FILE,"r",encoding="utf-8") as f:
            checkout_data = json.load(f)
    else:
        checkout_data = {}

    # ----------------------
    # Proses Pembayaran
    # ----------------------
    st.subheader("💳 Checkout User")
    if checkout_data:
        for user, pesanan in checkout_data.items():
            st.markdown(f"### 👤 {user}")
            total = 0
            for k,v in pesanan.items():
                harga_satuan = menu["makanan"].get(k, menu["minuman"].get(k,0))
                subtotal = harga_satuan * v
                st.write(f"{k} x {v} = Rp {subtotal:,}")
                total += subtotal
            st.info(f"Total: Rp {total:,}")

            uang = st.number_input(f"Uang diterima {user}", min_value=0, value=total, step=1000, key=f"bayar-{user}")
            if st.button(f"Bayar {user}", key=f"btn-bayar-{user}"):
                if uang >= total:
                    kembalian = uang - total
                    st.success(f"✅ Pembayaran berhasil! Kembalian: Rp {kembalian:,}")

                    # Simpan transaksi ke CSV
                    record = {
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "nama": user,
                        "items": json.dumps(pesanan, ensure_ascii=False),
                        "subtotal": total,
                        "diskon": 0,
                        "total": total,
                        "bayar": uang,
                        "kembalian": kembalian
                    }
                    df = pd.DataFrame([record])
                    if os.path.exists(DATA_FILE):
                        df.to_csv(DATA_FILE, mode="a", header=False, index=False, encoding="utf-8-sig")
                    else:
                        df.to_csv(DATA_FILE, index=False, encoding="utf-8-sig")

                    # Hapus pesanan yang sudah dibayar
                    del checkout_data[user]
                    with open(CHECKOUT_FILE,"w",encoding="utf-8") as f:
                        json.dump(checkout_data,f,ensure_ascii=False, indent=2)

                    st.experimental_rerun()
                else:
                    st.error("Uang kurang!")
    else:
        st.info("Belum ada user yang checkout.")

    # ----------------------
    # Laporan Penjualan
    # ----------------------
    st.subheader("📈 Laporan Penjualan")
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE, encoding="utf-8-sig")
        if not df.empty:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['total'] = df['total'].astype(int)
            st.dataframe(df[['timestamp','nama','subtotal','total','bayar','kembalian']])
            daily_revenue = df.groupby(df['timestamp'].dt.date)['total'].sum()
            st.bar_chart(daily_revenue)

            # Delete transaksi
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
