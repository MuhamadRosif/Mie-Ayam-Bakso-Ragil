import streamlit as st
import json, os
from datetime import datetime

CHECKOUT_FILE = "checkout.json"
MENU_FILE = "menu.json"

def run_admin():
    if "admin_login" not in st.session_state:
        st.session_state.admin_login=False

    ADMIN_USER="admin"
    ADMIN_PASS="1234"

    if not st.session_state.admin_login:
        st.subheader("🔐 Login Admin")
        username=st.text_input("Username")
        password=st.text_input("Password", type="password")
        if st.button("Masuk"):
            if username==ADMIN_USER and password==ADMIN_PASS:
                st.session_state.admin_login=True
                st.rerun()
            else:
                st.error("Username atau password salah.")
        return

    if st.sidebar.button("🚪 Logout Admin"):
        st.session_state.admin_login=False
        st.rerun()

    st.title("🛠️ Admin Dashboard")
    page = st.sidebar.selectbox("Menu Admin", ["Pesanan User","Pembayaran","Laporan","Kelola Menu"])

    # Load menu
    if os.path.exists(MENU_FILE):
        with open(MENU_FILE,"r",encoding="utf-8") as f:
            data=json.load(f)
            makanan=data.get("makanan",{})
            minuman=data.get("minuman",{})
    else:
        makanan={"Mie Ayam":15000,"Bakso":18000}
        minuman={"Es Teh":5000,"Es Jeruk":7000}

    # Pesanan User
    if page=="Pesanan User":
        st.header("📋 Pesanan User")
        if os.path.exists(CHECKOUT_FILE):
            with open(CHECKOUT_FILE,"r",encoding="utf-8") as f:
                checkout=json.load(f)
            if checkout:
                for idx,co in enumerate(checkout):
                    st.markdown(f"**{co['username']} — {co['timestamp']}**")
                    for item,qty in co["items"].items():
                        st.write(f"{item} x {qty}")
                    st.write(f"Total: Rp {co['total']:,}")
            else:
                st.info("Belum ada pesanan.")
        else:
            st.info("Belum ada pesanan.")

    # Pembayaran
    elif page=="Pembayaran":
        st.header("💳 Proses Pembayaran")
        if os.path.exists(CHECKOUT_FILE):
            with open(CHECKOUT_FILE,"r",encoding="utf-8") as f:
                checkout = json.load(f)
            if checkout:
                for idx,co in enumerate(checkout):
                    st.markdown(f"**{co['username']} — {co['timestamp']}**")
                    total=co['total']
                    uang=st.number_input(f"Uang diterima ({co['username']})", min_value=0,value=total,step=1000,key=f"uang-{idx}")
                    if st.button(f"Bayar {co['username']}", key=f"bayar-{idx}"):
                        if uang>=total:
                            kembalian=uang-total
                            st.success(f"✅ {co['username']} sudah bayar. Kembalian: Rp {kembalian:,}")
                            checkout.pop(idx)
                            with open(CHECKOUT_FILE,"w",encoding="utf-8") as f:
                                json.dump(checkout,f,ensure_ascii=False,indent=2)
                            st.rerun()
                        else:
                            st.error("Uang kurang!")
            else:
                st.info("Belum ada pesanan.")
        else:
            st.info("Belum ada pesanan.")

    # Laporan
    elif page=="Laporan":
        st.header("📈 Laporan Penjualan")
        if os.path.exists(CHECKOUT_FILE):
            with open(CHECKOUT_FILE,"r",encoding="utf-8") as f:
                checkout = json.load(f)
            if checkout:
                st.dataframe(checkout)
            else:
                st.info("Belum ada laporan.")
        else:
            st.info("Belum ada laporan.")

    # Kelola Menu
    elif page=="Kelola Menu":
        st.header("🍽️ Kelola Menu")
        st.subheader("Makanan")
        for item,harga in makanan.copy().items():
            col1,col2,col3=st.columns([3,2,1])
            with col1: nama_baru=st.text_input(f"{item}", value=item, key=f"m-{item}")
            with col2: harga_baru=st.number_input(f"Harga {item}", value=harga, step=1000, key=f"h-{item}")
            with col3:
                if st.button("💾 Update", key=f"up-{item}"):
                    makanan[nama_baru]=harga_baru
                    if nama_baru!=item: del makanan[item]
                    with open(MENU_FILE,"w",encoding="utf-8") as f:
                        json.dump({"makanan":makanan,"minuman":minuman},f,ensure_ascii=False,indent=2)
                    st.success(f"{nama_baru} diperbarui")
                    st.experimental_rerun()
                if st.button("❌ Hapus", key=f"delm-{item}"):
                    del makanan[item]
                    with open(MENU_FILE,"w",encoding="utf-8") as f:
                        json.dump({"makanan":makanan,"minuman":minuman},f,ensure_ascii=False,indent=2)
                    st.success(f"{item} dihapus")
                    st.rerun()
