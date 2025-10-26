import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime

DATA_FILE = "riwayat_penjualan.csv"
MENU_FILE = "menu.json"

def run_admin_app():
    # -----------------------
    # Login Admin
    # -----------------------
    if "login" not in st.session_state:
        st.session_state.login = False

    ADMIN_USER = "admin"
    ADMIN_PASS = "1234"

    if not st.session_state.login:
        st.markdown("""
        <style>
        .stApp {background: linear-gradient(180deg,#071026,#0b1440); color:#e6eef8;}
        .login-card {background-color:#1b1b1b; padding:40px; border-radius:12px; width:360px; 
                    margin:120px auto; text-align:center; box-shadow:0 4px 20px rgba(0,0,0,0.4);}
        .stTextInput>div>div>input {background-color:#2b2b2b; color:#fff; border-radius:6px;}
        .stButton>button {background-color:#c62828; color:white; border:none; border-radius:6px; padding:8px 20px;}
        </style>
        """, unsafe_allow_html=True)

        st.markdown('<div class="login-card"><h3>🔐 Login Admin — Kasir Mas Ragil</h3>', unsafe_allow_html=True)
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Masuk"):
            if username == ADMIN_USER and password == ADMIN_PASS:
                st.session_state.login = True
                st.experimental_rerun()
            else:
                st.error("Username atau password salah.")
        st.markdown('</div>', unsafe_allow_html=True)
        st.stop()

    # -----------------------
    # Load Menu
    # -----------------------
    if "menu_makanan" not in st.session_state or "menu_minuman" not in st.session_state:
        if os.path.exists(MENU_FILE):
            with open(MENU_FILE,"r",encoding="utf-8") as f:
                data = json.load(f)
                st.session_state.menu_makanan = data.get("makanan",{})
                st.session_state.menu_minuman = data.get("minuman",{})
        else:
            st.session_state.menu_makanan = {"Mie Ayam":15000,"Bakso Urat":18000,"Mie Ayam Bakso":20000,"Bakso Telur":19000}
            st.session_state.menu_minuman = {"Es Teh Manis":5000,"Es Jeruk":7000,"Teh Hangat":5000,"Jeruk Hangat":6000}
            with open(MENU_FILE,"w",encoding="utf-8") as f:
                json.dump({"makanan":st.session_state.menu_makanan,"minuman":st.session_state.menu_minuman},f,ensure_ascii=False, indent=2)

    # -----------------------
    # Styling
    # -----------------------
    st.markdown("""
    <style>
    .stApp {background: linear-gradient(180deg,#071026,#0b1440); color:#e6eef8;}
    .topbar {display:flex; align-items:center; gap:12px; padding:10px 18px; 
            background: linear-gradient(90deg,#b71c1c,#9c2a2a); color:white; 
            border-radius:8px; box-shadow:0 2px 10px rgba(0,0,0,0.3);}
    .right-panel {background: linear-gradient(180deg,#0c0e16,#181b26); padding:14px; border-radius:10px;}
    .menu-item {display:block; width:100%; padding:10px; border-radius:8px; background:#222; color:white; border:none;}
    .menu-item:hover {background:#333;}
    .nota {background-color:#141826; padding:18px; border-radius:10px; border:1px solid #2f3340; font-family:"Courier New", monospace;}
    .stButton>button {background: linear-gradient(90deg,#c62828,#9c1f1f); color:white; border:none; border-radius:6px; padding:8px 16px;}
    .stButton>button:hover {transform:scale(1.05);}
    </style>
    """, unsafe_allow_html=True)

    # -----------------------
    # Topbar
    # -----------------------
    col_tb1, col_tb2, col_tb3 = st.columns([1,10,2])
    with col_tb1:
        if st.button("≡", key="hamb_btn"):
            st.session_state.menu_open = not st.session_state.menu_open
    with col_tb2:
        st.markdown('<div class="topbar"><div style="font-weight:800">🍜 Mie Ayam & Bakso — Admin</div></div>', unsafe_allow_html=True)
    with col_tb3:
        if st.button("🚪 Logout"):
            st.session_state.login = False
            st.experimental_rerun()

    # -----------------------
    # Layout
    # -----------------------
    if "menu_open" not in st.session_state:
        st.session_state.menu_open = True

    if st.session_state.menu_open:
        main_col, side_col = st.columns([7,3])
    else:
        main_col = st.columns([1])[0]
        side_col = None

    # -----------------------
    # Sidebar Navigasi
    # -----------------------
    if side_col is not None:
        with side_col:
            st.markdown('<div class="right-panel">', unsafe_allow_html=True)
            if st.button("📄 Laporan Penjualan"): st.session_state.page="laporan"
            if st.button("🛠️ Admin Menu"): st.session_state.page="admin_menu"
            if st.button("♻️ Reset Pesanan"):
                st.session_state.pesanan={}
                st.session_state.nama_pelanggan=""
                st.session_state.total_bayar=0
                st.session_state.struk=""
                st.success("Pesanan direset.")
            st.markdown("<div style='font-size:12px;opacity:0.7;'>© Mas Ragil 2025</div>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # -----------------------
    # Fungsi Pendukung
    # -----------------------
    def save_transaction(timestamp,nama,items_dict,subtotal,diskon,total,bayar=None,kembalian=None):
        record={"timestamp":timestamp,"nama":nama,"items":json.dumps(items_dict,ensure_ascii=False),
                "subtotal":subtotal,"diskon":diskon,"total":total,"bayar":bayar if bayar else "","kembalian":kembalian if kembalian else ""}
        df=pd.DataFrame([record])
        if os.path.exists(DATA_FILE):
            df.to_csv(DATA_FILE,mode="a",header=False,index=False,encoding="utf-8-sig")
        else:
            df.to_csv(DATA_FILE,index=False,encoding="utf-8-sig")

    # -----------------------
    # Halaman Admin
    # -----------------------
    page = st.session_state.get("page","laporan")
    with main_col:
        # ------------------- LAPORAN -------------------
        if page=="laporan":
            st.header("📈 Laporan Penjualan")
            if os.path.exists(DATA_FILE):
                df = pd.read_csv(DATA_FILE, encoding="utf-8-sig")
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df['total'] = df['total'].astype(int)
                st.dataframe(df[['timestamp','nama','subtotal','diskon','total','bayar','kembalian']])
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

        # ------------------- ADMIN MENU -------------------
        elif page=="admin_menu":
            st.header("🛠️ Admin Menu — Update/Tambah/Hapus")
            # Menu Makanan
            st.subheader("🍽️ Menu Makanan")
            for item,harga in st.session_state.menu_makanan.copy().items():
                col1,col2,col3 = st.columns([3,2,1])
                with col1:
                    nama_baru = st.text_input(f"{item}", value=item, key=f"makanan-{item}")
                with col2:
                    harga_baru = st.number_input(f"Harga {item}", value=harga, step=1000, key=f"harga-{item}")
                with col3:
                    if st.button("❌", key=f"del-makanan-{item}"):
                        del st.session_state.menu_makanan[item]
                        with open(MENU_FILE,"w",encoding="utf-8") as f:
                            json.dump({"makanan":st.session_state.menu_makanan,"minuman":st.session_state.menu_minuman}, f, ensure_ascii=False, indent=2)
                        st.success(f"{item} dihapus")
                        st.experimental_rerun()
                # Update
                if st.button("💾 Update", key=f"update-makanan-{item}"):
                    st.session_state.menu_makanan[nama_baru] = harga_baru
                    if nama_baru != item:
                        del st.session_state.menu_makanan[item]
                    with open(MENU_FILE,"w",encoding="utf-8") as f:
                        json.dump({"makanan":st.session_state.menu_makanan,"minuman":st.session_state.menu_minuman}, f, ensure_ascii=False, indent=2)
                    st.success(f"{nama_baru} diperbarui")
                    st.experimental_rerun()

            # Menu Minuman
            st.subheader("🥤 Menu Minuman")
            for item,harga in st.session_state.menu_minuman.copy().items():
                col1,col2,col3 = st.columns([3,2,1])
                with col1:
                    nama_baru = st.text_input(f"{item}", value=item, key=f"minum-{item}")
                with col2:
                    harga_baru = st.number_input(f"Harga {item}", value=harga, step=1000, key=f"harga-minum-{item}")
                with col3:
                    if st.button("❌", key=f"del-minum-{item}"):
                        del st.session_state.menu_minuman[item]
                        with open(MENU_FILE,"w",encoding="utf-8") as f:
                            json.dump({"makanan":st.session_state.menu_makanan,"minuman":st.session_state.menu_minuman}, f, ensure_ascii=False, indent=2)
                        st.success(f"{item} dihapus")
                        st.experimental_rerun()
                # Update
                if st.button("💾 Update", key=f"update-minum-{item}"):
                    st.session_state.menu_minuman[nama_baru] = harga_baru
                    if nama_baru != item:
                        del st.session_state.menu_minuman[item]
                    with open(MENU_FILE,"w",encoding="utf-8") as f:
                        json.dump({"makanan":st.session_state.menu_makanan,"minuman":st.session_state.menu_minuman}, f, ensure_ascii=False, indent=2)
                    st.success(f"{nama_baru} diperbarui")
                    st.experimental_rerun()
