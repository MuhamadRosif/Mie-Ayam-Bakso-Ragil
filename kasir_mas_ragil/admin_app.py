import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd

USER_FILE = "users.json"
MENU_FILE = "menu.json"
DATA_FILE = "riwayat_penjualan.csv"

ADMIN_USER = "admin"
ADMIN_PASS = "1234"

def run_admin():
    st.header("👨‍💼 Admin Panel — Kasir Mas Ragil")

    # Login admin
    if "admin_login" not in st.session_state:
        st.session_state.admin_login = False

    if not st.session_state.admin_login:
        uname = st.text_input("Username Admin")
        upass = st.text_input("Password Admin", type="password")
        if st.button("Login Admin"):
            if uname==ADMIN_USER and upass==ADMIN_PASS:
                st.session_state.admin_login = True
            else:
                st.error("Username atau password admin salah.")
        return

    st.success("Selamat datang, Admin!")

    # Load users & menu
    if os.path.exists(USER_FILE):
        with open(USER_FILE,"r",encoding="utf-8") as f:
            users = json.load(f)
    else:
        users = {}

    if os.path.exists(MENU_FILE):
        with open(MENU_FILE,"r",encoding="utf-8") as f:
            menu = json.load(f)
    else:
        menu = {"makanan":{},"minuman":{}}

    # Admin Menu — Update/Tambah/Hapus menu
    st.subheader("🛠️ Menu Admin")
    st.write("Update/Tambah/Hapus Menu Makanan & Minuman")
    for cat in ["makanan","minuman"]:
        st.markdown(f"**{cat.title()}**")
        for item,harga in menu[cat].copy().items():
            col1,col2,col3 = st.columns([3,2,1])
            with col1: nama_baru = st.text_input(f"{item}", value=item, key=f"{cat}-{item}")
            with col2: harga_baru = st.number_input(f"Harga {item}", value=harga, step=1000, key=f"harga-{cat}-{item}")
            with col3:
                if st.button("❌", key=f"del-{cat}-{item}"):
                    del menu[cat][item]
                    with open(MENU_FILE,"w",encoding="utf-8") as f:
                        json.dump(menu,f,ensure_ascii=False, indent=2)
                    st.success(f"{item} dihapus")
                    st.experimental_rerun()
            if st.button("💾 Update", key=f"update-{cat}-{item}"):
                menu[cat][nama_baru] = harga_baru
                if nama_baru != item:
                    del menu[cat][item]
                with open(MENU_FILE,"w",encoding="utf-8") as f:
                    json.dump(menu,f,ensure_ascii=False, indent=2)
                st.success(f"{nama_baru} diperbarui")
                st.experimental_rerun()

    # Tambah menu baru
    st.markdown("### ➕ Tambah Menu Baru")
    nama_baru = st.text_input("Nama Menu Baru", key="new_nama")
    harga_baru = st.number_input("Harga Menu Baru", min_value=0, step=1000, key="new_harga")
    jenis = st.selectbox("Jenis Menu", ["Makanan","Minuman"], key="new_jenis")
    if st.button("Tambah Menu"):
        if nama_baru.strip() and harga_baru>0:
            menu[jenis.lower()][nama_baru] = harga_baru
            with open(MENU_FILE,"w",encoding="utf-8") as f:
                json.dump(menu,f,ensure_ascii=False, indent=2)
            st.success(f"{nama_baru} berhasil ditambahkan")
            st.experimental_rerun()
        else:
            st.warning("Isi nama dan harga menu dengan benar.")

    # Tampilkan semua pesanan user
    st.subheader("🛒 Pesanan User")
    for uname,udata in users.items():
        pesanan = {k:v for k,v in udata["pesanan"].items() if v>0}
        if pesanan:
            st.markdown(f"### {uname}")
            total_user = 0
            for k,v in pesanan.items():
                harga_satuan = menu["makanan"].get(k, menu["minuman"].get(k,0))
                subtotal = harga_satuan*v
                st.write(f"- {k} x {v} = Rp {subtotal:,}")
                total_user += subtotal

            if st.button(f"✅ Bayar {uname}", key=f"bayar-{uname}"):
                # Simpan riwayat
                record = {"timestamp":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                          "user":uname,
                          "items":json.dumps(pesanan,ensure_ascii=False),
                          "total":total_user}
                df = pd.DataFrame([record])
                if os.path.exists(DATA_FILE):
                    df.to_csv(DATA_FILE, mode="a", index=False, header=False, encoding="utf-8-sig")
                else:
                    df.to_csv(DATA_FILE,index=False, encoding="utf-8-sig")

                # Clear pesanan
                users[uname]["pesanan"] = {}
                with open(USER_FILE,"w",encoding="utf-8") as f:
                    json.dump(users,f,ensure_ascii=False, indent=2)

                # Struk
                st.success(f"Pesanan {uname} berhasil dibayar!")
                st.markdown("### 🧾 Struk Pembayaran")
                st.write(f"**User:** {uname}")
                st.write(f"**Tanggal:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                total_struk = 0
                for k,v in pesanan.items():
                    harga_satuan = menu["makanan"].get(k, menu["minuman"].get(k,0))
                    subtotal = harga_satuan*v
                    st.write(f"- {k} x {v} = Rp {subtotal:,}")
                    total_struk += subtotal
                st.write(f"**Total Bayar:** Rp {total_struk:,}")
                st.info("Terima kasih telah melakukan pembayaran!")
                st.experimental_rerun()

    # Laporan Harian
    st.subheader("📊 Laporan Penjualan")
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        st.dataframe(df)
        if st.button("🗑️ Hapus Laporan Harian"):
            os.remove(DATA_FILE)
            st.success("Laporan harian dihapus.")
            st.experimental_rerun()
    else:
        st.info("Belum ada transaksi.")
