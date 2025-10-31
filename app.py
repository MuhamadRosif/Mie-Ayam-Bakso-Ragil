import streamlit as st
import json, os
import pandas as pd
from datetime import datetime

MENU_FILE = "menu.json"
CHECKOUT_FILE = "checkout.json"
SALES_FILE = "sales.json"

# ================== JSON HELPERS ==================
def load_json(file, default):
    if not os.path.exists(file):
        with open(file, "w") as f: json.dump(default, f)
    with open(file, "r") as f: return json.load(f)

def save_json(file, data):
    with open(file, "w") as f: json.dump(data, f, indent=2)

menu_data = load_json(MENU_FILE, {"makanan":{}, "minuman":{}})
checkout = load_json(CHECKOUT_FILE, [])
sales = load_json(SALES_FILE, [])

# ================== UI CONFIG ==================
st.set_page_config(page_title="Mie Ayam Mas Ragil", page_icon="🍜", layout="centered")
st.markdown("""
<style>
body {background:#faf6f0;}
footer{visibility:hidden;}
</style>
""", unsafe_allow_html=True)

# ================== LOGIN ==================
if "role" not in st.session_state:
    st.session_state.role = None

def login_page():
    st.title("🍜 Mie Ayam Bakso Ragil")
    role = st.selectbox("Masuk sebagai", ["Pelanggan", "Admin"])
    user = st.text_input("Username")
    pw   = st.text_input("Password", type="password")

    if st.button("Masuk"):
        if role=="Admin" and user=="admin" and pw=="123":
            st.session_state.role = "admin"; st.rerun()
        elif role=="Pelanggan" and user=="user" and pw=="123":
            st.session_state.role = "user"; st.rerun()
        else:
            st.error("Login salah!")

# ================== USER PAGE ==================
def user_page():
    st.title("🍜 Menu Pesanan")

    kategori = st.selectbox("Kategori", list(menu_data.keys()))
    item = st.selectbox("Menu", list(menu_data[kategori].keys()))
    qty = st.number_input("Jumlah", min_value=1, value=1)

    if st.button("Tambah"):
        checkout.append({
            "nama": item,
            "harga": menu_data[kategori][item],
            "jumlah": qty
        })
        save_json(CHECKOUT_FILE, checkout)
        st.success("✅ Ditambahkan")

    st.subheader("🧾 Pesanan")
    if checkout:
        df = pd.DataFrame(checkout)
        df["total"] = df["harga"] * df["jumlah"]
        df["total"] = df["total"].apply(lambda x: f"Rp {x:,}".replace(",", "."))
        st.table(df)
    else:
        st.info("Belum ada pesanan.")

# ================== ADMIN PAGE ==================
def admin_page():
    st.title("⚙️ Admin Panel")
    menu = st.sidebar.radio("Menu", ["Data Menu","Data Pesanan","Pembayaran","Laporan"])

    # -------- Data Menu --------
    if menu == "Data Menu":
        st.subheader("📋 Menu Sekarang")

        rows=[]
        for k, items in menu_data.items():
            for i, h in items.items():
                rows.append({"Kategori":k,"Nama":i,"Harga":f"Rp {h:,}".replace(",",".")})
        st.table(pd.DataFrame(rows))

        st.subheader("➕ Tambah / Edit Menu")
        kat = st.selectbox("Kategori", list(menu_data.keys()))
        nama = st.text_input("Nama Menu")
        harga = st.number_input("Harga", min_value=0)

        if st.button("Simpan Menu"):
            menu_data[kat][nama] = harga
            save_json(MENU_FILE, menu_data)
            st.success("✅ Menu disimpan"); st.rerun()

        st.subheader("🗑️ Hapus Menu")
        del_kat = st.selectbox("Pilih Kategori", list(menu_data.keys()))
        del_item = st.selectbox("Pilih Menu", list(menu_data[del_kat].keys()))
        if st.button("Hapus Menu"):
            del menu_data[del_kat][del_item]
            save_json(MENU_FILE, menu_data)
            st.success("✅ Menu dihapus"); st.rerun()

    # -------- Pesanan --------
    elif menu == "Data Pesanan":
        st.subheader("📝 Pesanan Masuk")
        if not checkout:
            st.info("Belum ada pesanan.")
        else:
            df = pd.DataFrame(checkout)
            st.table(df)
            if st.button("Hapus Semua"):
                save_json(CHECKOUT_FILE, [])
                st.success("✅ Pesanan dibersihkan"); st.rerun()

    # -------- Pembayaran --------
    elif menu == "Pembayaran":
        if not checkout:
            st.info("Belum ada transaksi.")
        else:
            df = pd.DataFrame(checkout)
            df["total"] = df["harga"] * df["jumlah"]
            st.table(df)

            nama = st.text_input("Nama Pembeli")
            total = df["total"].sum()

            if st.button("Cetak Struk"):
                filename = f"struk_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                txt = "==== MIE AYAM MAS RAGIL ====\n"
                txt+= f"Tanggal : {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
                txt+= "==============================\n"
                for d in checkout:
                    txt += f"{d['nama']} x{d['jumlah']} = Rp {d['harga']*d['jumlah']:,}\n"
                txt+= "------------------------------\n"
                txt+= f"Total : Rp {total:,}\n"
                txt+= f"Pembeli: {nama or 'Umum'}\n"
                txt+= "Terima kasih 🙏\n"

                with open(filename,"w") as f: f.write(txt)

                st.download_button("Download Struk", open(filename,"rb"), filename)

                sales.append({"tanggal": datetime.now().strftime("%Y-%m-%d"),"total": total})
                save_json(SALES_FILE, sales)
                save_json(CHECKOUT_FILE, [])

                st.success("✅ Pembayaran selesai"); st.rerun()

    # -------- Laporan --------
    elif menu == "Laporan":
    st.subheader("📊 Laporan Harian")
    sales_data = load_json(SALES_FILE, [])

    if not sales_data:
        st.info("Belum ada transaksi.")
    else:
        df = pd.DataFrame(sales_data)
        df["Tanggal"] = pd.to_datetime(df["tanggal"]).dt.strftime("%d/%m/%Y")
        df["Pemasukan"] = df["total"].apply(lambda x: f"Rp {x:,}".replace(",","."))
        st.table(df[["Tanggal","Pemasukan"]])

        total_all = sum(s["total"] for s in sales_data)
        st.write(f"### 💰 Total: **Rp {total_all:,}**")

# ================== ROUTING ==================
if st.session_state.role == "admin":
    st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"role":None}))
    admin_page()

elif st.session_state.role == "user":
    st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"role":None}))
    user_page()

else:
    login_page()
