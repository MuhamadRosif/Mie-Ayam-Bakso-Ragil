# app.py - FINAL CLEAN (No Static QR)
import streamlit as st
import json, os
import pandas as pd
from datetime import datetime
import pytz
from io import BytesIO
import barcode
from barcode.writer import ImageWriter

# ---------------- file paths ----------------
MENU_FILE = "menu.json"
CHECKOUT_FILE = "checkout.json"
SALES_FILE = "sales.json"
CONFIG_FILE = "config.json"

# ---------------- helpers ----------------
def load_json(path, default):
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(default, f, indent=2, ensure_ascii=False)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# ---------------- initial data ----------------
menu_data = load_json(MENU_FILE, {"makanan": {"Mie Ayam": 15000, "Bakso": 18000}, "minuman": {"Es Teh": 5000}})
checkout = load_json(CHECKOUT_FILE, [])
sales = load_json(SALES_FILE, [])
config = load_json(CONFIG_FILE, {
    "cashier": "ADMIN RAGIL",
    "counter": 0,
    "shop_name": "MIE AYAM MAS RAGIL",
    "address": "Jl. Rasa Bahagia No.1",
    "ppn": 11,
    "diskon": 0,
    "footer": "Selalu segar bangsat"
})

# ---------------- UI setup ----------------
st.set_page_config(page_title="Mie Ayam Mas Ragil", page_icon="🍜", layout="centered")
st.markdown("""<style>body{background:#faf6f0;} footer{visibility:hidden;}</style>""", unsafe_allow_html=True)

# ---------------- session defaults ----------------
if "role" not in st.session_state:
    st.session_state.role = None

# ---------------- Login ----------------
def login_page():
    st.title("🍜 Mie Ayam Bakso Ragil")
    role = st.selectbox("Masuk sebagai", ["Pelanggan", "Admin"])
    user = st.text_input("Username")
    pw = st.text_input("Password", type="password")
    if st.button("Masuk"):
        if role == "Admin" and user == "admin" and pw == "123":
            st.session_state.role = "admin"; st.rerun()
        elif role == "Pelanggan" and user == "user" and pw == "123":
            st.session_state.role = "user"; st.rerun()
        else:
            st.error("Login salah!")

# ---------------- User Menu ----------------
def user_page():
    st.title("🍜 Menu Pesanan")
    buyer = st.text_input("Nama Pembeli (opsional)")
    kategori = st.selectbox("Kategori", list(menu_data.keys()))
    item = st.selectbox("Menu", list(menu_data[kategori].keys()))
    qty = st.number_input("Jumlah", min_value=1, value=1)

    if st.button("Tambah"):
        checkout.append({"nama": item, "harga": menu_data[kategori][item], "jumlah": qty, "buyer": buyer or "Umum"})
        save_json(CHECKOUT_FILE, checkout)
        st.success("✅ Ditambahkan")

    if checkout:
        df = pd.DataFrame(checkout)
        df["total"] = df["harga"] * df["jumlah"]
        st.table(df)

# ---------------- Admin ----------------
def admin_page():
    st.title("⚙️ Admin Panel")

    # Sidebar nav
    page = st.sidebar.radio("Menu Admin", ["Pengaturan Toko", "Data Menu", "Pesanan", "Pembayaran", "Laporan"])

    # ---- Pengaturan Toko ----
    if page == "Pengaturan Toko":
        st.subheader("🏪 Pengaturan Toko")
        config["shop_name"] = st.text_input("Nama Toko", config["shop_name"])
        config["address"] = st.text_input("Alamat", config["address"])
        config["cashier"] = st.text_input("Nama Kasir", config["cashier"])
        config["ppn"] = st.number_input("PPN (%)", 0, 20, config["ppn"])
        config["diskon"] = st.number_input("Diskon (%)", 0, 100, config["diskon"])
        config["footer"] = st.text_input("Footer Struk", config["footer"])

        col1, col2 = st.columns(2)
        if col1.button("💾 Simpan"):
            save_json(CONFIG_FILE, config)
            st.success("✅ Disimpan")
        if col2.button("Reset Counter"):
            config["counter"] = 0
            save_json(CONFIG_FILE, config)
            st.success("✅ Counter Reset")

    # ---- Menu ----
    elif page == "Data Menu":
        st.subheader("📋 Menu")
        df = [{"Kategori": k, "Menu": n, "Harga": h} for k in menu_data for n, h in menu_data[k].items()]
        st.table(pd.DataFrame(df))
        kat = st.selectbox("Kategori", list(menu_data.keys()))
        nama = st.text_input("Nama Menu")
        harga = st.number_input("Harga", min_value=0)
        if st.button("Simpan Menu"):
            menu_data[kat][nama] = harga
            save_json(MENU_FILE, menu_data)
            st.success("✅ Menu disimpan")

    # ---- Pesanan ----
    elif page == "Pesanan":
        st.subheader("📝 Pesanan")
        if not checkout:
            st.info("Kosong")
        else:
            df = pd.DataFrame(checkout)
            df["total"] = df["harga"] * df["jumlah"]
            st.table(df)
            if st.button("Hapus Semua"):
                checkout.clear()
                save_json(CHECKOUT_FILE, checkout)
                st.success("✅ Dibersihkan")

    # ---- Pembayaran ----
    elif page == "Pembayaran":
        st.subheader("💳 Pembayaran")
        if not checkout:
            st.info("Belum ada transaksi")
            return

        df = pd.DataFrame(checkout)
        df["total"] = df["harga"] * df["jumlah"]
        st.table(df)

        buyer = checkout[0]["buyer"]
        total = sum(i["harga"] * i["jumlah"] for i in checkout)

        tz = pytz.timezone("Asia/Jakarta")
        now = datetime.now(tz)

        ppn_amount = total * config["ppn"] / 100
        disc_amount = total * config["diskon"] / 100
        final_total = total + ppn_amount - disc_amount

        def build_struk():
            config["counter"] += 1; save_json(CONFIG_FILE, config)
            kode = f"RG-{now.strftime('%Y%m%d')}-{config['counter']:05d}"

            lines = []
            lines.append(config["shop_name"].center(32))
            lines.append(config["address"].center(32))
            lines.append("-"*32)
            lines.append(f"No: {kode}")
            lines.append(f"Kasir: {config['cashier']}")
            lines.append(f"Tgl: {now.strftime('%d-%m-%Y %H:%M:%S')} WIB")
            lines.append("-"*32)

            for d in checkout:
                sub = d["harga"] * d["jumlah"]
                lines.append(d["nama"])
                lines.append(f"{d['jumlah']} x Rp {d['harga']:,}".replace(",", ".") + 
                             f"{' '*(32-len(str(sub))-10)}Rp {sub:,}".replace(",", "."))

            lines.append("-"*32)
            lines.append(f"Subtotal     Rp {total:,}".replace(",", "."))
            lines.append(f"PPN {config['ppn']}%      Rp {int(ppn_amount):,}".replace(",", "."))
            lines.append(f"Diskon {config['diskon']}% Rp {int(disc_amount):,}".replace(",", "."))
            lines.append(f"Total        Rp {int(final_total):,}".replace(",", "."))
            lines.append("-"*32)
            lines.append(f"Pembeli: {buyer}")
            lines.append(config["footer"].center(32))

            return "\n".join(lines), kode

        if st.button("🖨️ Cetak & Simpan"):
            struk,kode = build_struk()

            # generate barcode
            code128 = barcode.get('code128', kode, writer=ImageWriter())
            buf_bar = BytesIO(); code128.write(buf_bar); buf_bar.seek(0)

            st.text(struk)
            st.image(buf_bar.getvalue(), width=260)

            sales.append({"tanggal": now.strftime("%Y-%m-%d"),"total": final_total,"kode": kode,"cashier": config["cashier"],"buyer": buyer,"items": checkout.copy()})
            save_json(SALES_FILE, sales)

            checkout.clear(); save_json(CHECKOUT_FILE, checkout)
            st.success("✅ Disimpan & dicetak")

    # ---- Laporan ----
    elif page == "Laporan":
        st.subheader("📊 Laporan")
        if not sales:
            st.info("Belum ada")
        else:
            df = pd.DataFrame(sales)
            df["Tanggal"] = pd.to_datetime(df["tanggal"]).dt.strftime("%d/%m/%Y")
            df["Total"] = df["total"]
            st.table(df[["Tanggal","Total","kode","buyer"]])
            st.write("Total Semua:", f"Rp {sum(df['Total']):,}".replace(",", "."))

# ---------------- routing ----------------
if st.session_state.role == "admin":
    st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"role": None}))
    admin_page()
elif st.session_state.role == "user":
    st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"role": None}))
    user_page()
else:
    login_page()
