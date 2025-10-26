import streamlit as st
import json, os
import pandas as pd
from datetime import datetime

ADMIN_USER = "admin"
ADMIN_PASS = "1234"
MENU_FILE = "kasir_mas_ragil/menu.json"
KERANJANG_FILE = "kasir_mas_ragil/keranjang.json"
RIWAYAT_FILE = "kasir_mas_ragil/riwayat_penjualan.csv"

# ----------------------- LOAD / SAVE -----------------------
def load_menu():
    if os.path.exists(MENU_FILE):
        with open(MENU_FILE,"r",encoding="utf-8") as f:
            data = json.load(f)
            return data.get("makanan",{}), data.get("minuman",{})
    return {}, {}

def save_menu(makanan,minuman):
    with open(MENU_FILE,"w",encoding="utf-8") as f:
        json.dump({"makanan":makanan,"minuman":minuman}, f, ensure_ascii=False, indent=2)

def load_keranjang():
    if os.path.exists(KERANJANG_FILE):
        with open(KERANJANG_FILE,"r",encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_keranjang(data):
    with open(KERANJANG_FILE,"w",encoding="utf-8") as f:
        json.dump(data,f,ensure_ascii=False,indent=2)

def save_riwayat(transaksi):
    df = pd.DataFrame([transaksi])
    if os.path.exists(RIWAYAT_FILE):
        df.to_csv(RIWAYAT_FILE, mode="a", header=False, index=False, encoding="utf-8-sig")
    else:
        df.to_csv(RIWAYAT_FILE, index=False, encoding="utf-8-sig")

# ----------------------- ADMIN APP -----------------------
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
    keranjang_all = load_keranjang()

    # ----------------------- PESANAN USER -----------------------
    st.subheader("🛒 Semua Pesanan User")
    for user, items in keranjang_all.items():
        if not items: continue
        st.markdown(f"### {user}")
        total = 0
        for k,v in items.items():
            harga = makanan.get(k,minuman.get(k,0))
            total += v*harga
            st.write(f"{k} x {v} = Rp {v*harga:,}")
        st.info(f"Total: Rp {total:,}")

        uang = st.number_input(f"Uang diterima {user}", min_value=0, value=total, step=1000, key=f"uang-{user}")
        if st.button(f"Bayar {user}", key=f"bayar-{user}"):
            st.success(f"Pembayaran {user} berhasil! Kembalian: Rp {uang-total:,}")
            # Simpan riwayat
            save_riwayat({
                "user": user,
                "items": json.dumps(items, ensure_ascii=False),
                "total": total,
                "uang": uang,
                "kembalian": uang-total,
                "waktu": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            # Reset keranjang user
            keranjang_all[user] = {}
            save_keranjang(keranjang_all)
            st.rerun()

    # ----------------------- ADMIN MENU -----------------------
    st.subheader("🛠️ Update/Tambah/Hapus Menu")
    st.markdown("#### 🍽️ Menu Makanan")
    for item,harga in makanan.copy().items():
        col1,col2,col3 = st.columns([3,2,1])
        with col1: nama_baru = st.text_input(f"{item}", value=item, key=f"makanan-{item}")
        with col2: harga_baru = st.number_input(f"Harga {item}", value=harga, step=1000, key=f"harga-{item}")
        with col3:
            if st.button("❌", key=f"del-makanan-{item}"):
                del makanan[item]
                save_menu(makanan,minuman)
                st.success(f"{item} dihapus")
                st.rerun()
        if st.button("💾 Update", key=f"update-makanan-{item}"):
            makanan[nama_baru] = harga_baru
            if nama_baru != item: del makanan[item]
            save_menu(makanan,minuman)
            st.success(f"{nama_baru} diperbarui")
            st.rerun()

    st.markdown("#### 🥤 Menu Minuman")
    for item,harga in minuman.copy().items():
        col1,col2,col3 = st.columns([3,2,1])
        with col1: nama_baru = st.text_input(f"{item}", value=item, key=f"minum-{item}")
        with col2: harga_baru = st.number_input(f"Harga {item}", value=harga, step=1000, key=f"harga-minum-{item}")
        with col3:
            if st.button("❌", key=f"del-minum-{item}"):
                del minuman[item]
                save_menu(makanan,minuman)
                st.success(f"{item} dihapus")
                st.rerun()
        if st.button("💾 Update", key=f"update-minum-{item}"):
            minuman[nama_baru] = harga_baru
            if nama_baru != item: del minuman[item]
            save_menu(makanan,minuman)
            st.success(f"{nama_baru} diperbarui")
            st.rerun()

    # Tambah menu baru
    st.markdown("### ➕ Tambah Menu Baru")
    nama_baru = st.text_input("Nama Menu Baru")
    harga_baru = st.number_input("Harga Menu Baru", min_value=0, step=1000)
    jenis = st.selectbox("Jenis Menu", ["Makanan","Minuman"])
    if st.button("Tambah Menu"):
        if nama_baru.strip() and harga_baru>0:
            if jenis=="Makanan": makanan[nama_baru] = harga_baru
            else: minuman[nama_baru] = harga_baru
            save_menu(makanan,minuman)
            st.success(f"{nama_baru} berhasil ditambahkan")
            st.rerun()

    # ----------------------- LAPORAN -----------------------
    st.subheader("📈 Laporan Penjualan")
    if os.path.exists(RIWAYAT_FILE):
        df = pd.read_csv(RIWAYAT_FILE, encoding="utf-8-sig")
        if not df.empty:
            df['waktu'] = pd.to_datetime(df['waktu'])
            st.dataframe(df[['waktu','user','items','total','uang','kembalian']])
            daily = df.groupby(df['waktu'].dt.date)['total'].sum()
            st.bar_chart(daily)

            # Hapus seluruh laporan
            if st.button("❌ Hapus Semua Laporan"):
                os.remove(RIWAYAT_FILE)
                st.success("Semua laporan dihapus!")
                st.rerun()
        else:
            st.info("Belum ada transaksi.")
    else:
        st.info("Belum ada transaksi.")
