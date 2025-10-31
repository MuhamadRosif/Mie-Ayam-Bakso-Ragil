import streamlit as st
import json, os
import pandas as pd
from datetime import datetime

MENU_FILE = "menu.json"
CHECKOUT_FILE = "checkout.json"
SALES_FILE = "sales.json"
CONFIG_FILE = "config.json"

# ================== JSON HELPERS ==================
def load_json(file, default):
    if not os.path.exists(file):
        with open(file, "w") as f: json.dump(default, f)
    with open(file, "r") as f: return json.load(f)

def save_json(file, data):
    with open(file, "w") as f: json.dump(data, f, indent=2)

# ================== INITIAL DATA ==================
menu_data = load_json(MENU_FILE, {"makanan":{}, "minuman":{}})
checkout = load_json(CHECKOUT_FILE, [])
sales = load_json(SALES_FILE, [])
config = load_json(CONFIG_FILE, {"cashier": "ADMIN RAGIL"})

# Fix data sales lama biar nggak error
for s in sales:
    s.setdefault("kode", "-")
    s.setdefault("cashier", config.get("cashier","ADMIN RAGIL"))
    s.setdefault("buyer", "Umum")
    s.setdefault("items", [])

# ================== UI CONFIG ==================
st.set_page_config(page_title="Mie Ayam Mas Ragil", page_icon="🍜", layout="centered")
st.markdown("""
<style>
body {background:#faf6f0;}
footer{visibility:hidden;}
</style>
""", unsafe_allow_html=True)

if "role" not in st.session_state: st.session_state.role = None
if "buyer_name" not in st.session_state: st.session_state.buyer_name = ""

# ================== LOGIN ==================
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

    st.subheader("👤 Nama Pembeli")
    st.session_state.buyer_name = st.text_input("Masukkan Nama (opsional)", value=st.session_state.buyer_name)

    kategori = st.selectbox("Kategori", list(menu_data.keys()))
    item = st.selectbox("Menu", list(menu_data[kategori].keys()))
    qty = st.number_input("Jumlah", min_value=1, value=1)

    if st.button("Tambah"):
        buyer = st.session_state.buyer_name or "Umum"
        checkout.append({"nama": item,"harga": menu_data[kategori][item],"jumlah": qty,"buyer": buyer})
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

# ================== ADMIN ==================
def admin_page():
    st.title("⚙️ Admin Panel")
    menu = st.sidebar.radio("Menu", ["Data Menu","Data Pesanan","Pembayaran","Laporan","Pengaturan Kasir"])

    # ------- Nama Kasir -------
    if menu == "Pengaturan Kasir":
        st.subheader("👨‍🍳 Nama Kasir")
        kas = st.text_input("Nama Kasir", value=config.get("cashier","ADMIN RAGIL"))
        if st.button("Simpan"):
            config["cashier"] = kas.strip()
            save_json(CONFIG_FILE, config)
            st.success("✅ Disimpan"); st.rerun()

    # ------- Menu -------
    if menu == "Data Menu":
        st.subheader("📋 Menu")
        rows=[]
        for k,i in menu_data.items():
            for n,h in i.items(): rows.append({"Kategori":k,"Nama":n,"Harga":f"Rp {h:,}".replace(",",".")})
        st.table(pd.DataFrame(rows))

        st.subheader("Tambah Menu")
        kat = st.selectbox("Kategori", list(menu_data.keys()))
        nama = st.text_input("Nama")
        harga = st.number_input("Harga", min_value=0)
        if st.button("Simpan Menu"):
            menu_data[kat][nama] = harga; save_json(MENU_FILE, menu_data)
            st.success("✅ Disimpan"); st.rerun()

        st.subheader("Hapus Menu")
        dk = st.selectbox("Pilih Kategori", list(menu_data.keys()))
        di = st.selectbox("Pilih Menu", list(menu_data[dk].keys()))
        if st.button("Hapus"):
            del menu_data[dk][di]; save_json(MENU_FILE, menu_data)
            st.success("✅ Dihapus"); st.rerun()

    # ------- Pesanan masuk -------
    if menu == "Data Pesanan":
        st.subheader("📝 Pesanan Masuk")
        if not checkout: st.info("Kosong"); return
        df = pd.DataFrame(checkout); df["total"] = df["harga"] * df["jumlah"]
        df["total"] = df["total"].apply(lambda v:f"Rp {v:,}".replace(",","."))
        st.table(df)
        if st.button("Hapus Semua"):
            checkout.clear(); save_json(CHECKOUT_FILE, checkout)
            st.success("✅ Bersih"); st.rerun()

    # ------- Pembayaran -------
    if menu == "Pembayaran":
        if not checkout:
            st.info("Belum ada transaksi."); return

        df = pd.DataFrame(checkout)
        df["total"] = df["harga"] * df["jumlah"]
        df["total"] = df["total"].apply(lambda x: f"Rp {x:,}".replace(",", "."))
        st.table(df)

        buyer = checkout[0].get("buyer","Umum")
        total = sum(i["harga"]*i["jumlah"] for i in checkout)
        now = datetime.now()
        kode = now.strftime("AC%y%m%d%H%M%S")
        kasir = config.get("cashier","ADMIN RAGIL")

        # STRUK
        lines = [
            "   PT. RAGIL JAYA MAKMUR",
            " MIE AYAM & BAKSO RAGIL",
            "JL. RASA BAHAGIA NO.1 JAKARTA",
            "NPWP: 12.345.678.9-012.000",
            "",
            f"No. Transaksi: {kode}",
            f"Kasir: {kasir}",
            f"Tgl. {now.strftime('%d-%m-%Y')} {now.strftime('%H:%M:%S')}",
            "--------------------------------"
        ]
        for d in checkout:
            nm = d['nama'][:20].ljust(20)
            lines.append(f"{nm} {str(d['jumlah']).rjust(2)} x Rp {d['harga']:,}".replace(",","."))
            lines.append(f"  Subtotal: Rp {d['harga']*d['jumlah']:,}".replace(",","."))
        lines += [
            "--------------------------------",
            f"Total Item: {len(checkout)}",
            f"Total     : Rp {total:,}".replace(",","."),
            f"Tunai     : Rp {total:,}".replace(",","."),
            "Kembalian : Rp 0",
            "PPN sudah termasuk",
            "--------------------------------",
            f"Pembeli: {buyer}",
            "",
            "Terima kasih 🙏"
        ]
        struk = "\n".join(lines)

        # CETAK STRUK
        if st.button("🖨️ Cetak Struk (Print)"):
            st.subheader("🧾 STRUK")
            st.text(struk)

            sales.append({"tanggal": now.strftime("%Y-%m-%d"),"total": total,"kode": kode,"cashier":kasir,"buyer":buyer,"items":checkout.copy()})
            save_json(SALES_FILE, sales)

            checkout.clear(); save_json(CHECKOUT_FILE, checkout)
            st.success("✅ Struk dicetak"); st.stop()

        # DOWNLOAD STRUK
        fn = f"struk_{kode}.txt"
        with open(fn,"w") as f: f.write(struk)
        with open(fn,"rb") as f:
            if st.download_button("⬇️ Download Struk", f, file_name=fn):
                sales.append({"tanggal": now.strftime("%Y-%m-%d"),"total": total,"kode": kode,"cashier":kasir,"buyer":buyer,"items":checkout.copy()})
                save_json(SALES_FILE, sales)
                checkout.clear(); save_json(CHECKOUT_FILE, checkout)
                st.success("✅ Tersimpan & checkout dibersihkan")

    # ------- Laporan -------
    if menu == "Laporan":
        st.subheader("📊 Laporan")
        if not sales:
            st.info("Belum ada transaksi"); return

        df = pd.DataFrame(sales)
        df["Tanggal"] = pd.to_datetime(df["tanggal"]).dt.strftime("%d/%m/%Y")
        df["Pemasukan"] = df["total"].apply(lambda x:f"Rp {x:,}".replace(",","."))
        
        cols = ["Tanggal","Pemasukan"]
        for c in ["kode","cashier","buyer"]:
            if c in df.columns: cols.append(c)

        st.table(df[cols])
        st.write(f"### 💰 Total: Rp {sum(s['total'] for s in sales):,}".replace(",", "."))

        st.subheader("🗑️ Hapus Transaksi")
        pilih = st.selectbox("Pilih kode transaksi", [s["kode"] for s in sales])
        if st.button("Hapus Transaksi"):
            sales[:] = [s for s in sales if s["kode"] != pilih]
            save_json(SALES_FILE, sales)
            st.success("✅ Dihapus"); st.rerun()

# ================== ROUTING ==================
if st.session_state.role == "admin":
    st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"role":None}))
    admin_page()
elif st.session_state.role == "user":
    st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"role":None}))
    user_page()
else:
    login_page()
