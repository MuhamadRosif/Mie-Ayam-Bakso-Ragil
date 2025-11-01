# app.py - Full Final Aman
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
    "shop_name": "Mie Ayam Mas Ragil",
    "address": "Jl. Rasa Bahagia No.1",
    "cashier": "ADMIN RAGIL",
    "counter": 0,
    "ppn": 11,
    "diskon": 0,
    "footer": "Selalu segar bangsat"
})

# normalize old sales entries
for s in sales:
    s.setdefault("kode", "-")
    s.setdefault("cashier", config.get("cashier"))
    s.setdefault("buyer", "Umum")
    s.setdefault("items", [])

# ---------------- UI setup ----------------
st.set_page_config(page_title="Mie Ayam Mas Ragil", page_icon="🍜", layout="centered")
st.markdown("""<style>body{background:#faf6f0;} footer{visibility:hidden;}</style>""", unsafe_allow_html=True)

# ---------------- session defaults ----------------
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False
if "buyer_name" not in st.session_state:
    st.session_state.buyer_name = ""

# ---------------- helpers struk ----------------
def center32(text):
    return str(text).center(32)

def lr32(left, right):
    left_s = str(left)
    right_s = str(right)
    space = 32 - len(left_s) - len(right_s)
    if space < 1:
        left_s = left_s[:32 - len(right_s) - 1]
        space = 1
    return left_s + " " * space + right_s

def build_struk(items, buyer, total_paid):
    tz = pytz.timezone("Asia/Jakarta")
    now = datetime.now(tz)
    counter = config.get("counter",0)+1
    config["counter"] = counter
    save_json(CONFIG_FILE, config)
    kode = f"RG-{now.strftime('%Y%m%d')}-{counter:05d}"

    subtotal = sum(d['harga']*d['jumlah'] for d in items)
    ppn_amt = int(subtotal * config.get("ppn",11)/100)
    diskon_amt = int(subtotal * config.get("diskon",0)/100)
    total_final = subtotal + ppn_amt - diskon_amt
    kembalian = total_paid - total_final

    lines = []
    lines.append(center32(config["shop_name"]))
    lines.append(center32(config["address"]))
    lines.append("-"*32)
    lines.append(f"No. Transaksi: {kode}")
    lines.append(f"Kasir: {config['cashier']}")
    lines.append(f"Tgl: {now.strftime('%d-%m-%Y %H:%M:%S')} WIB")
    lines.append("-"*32)
    total_items = 0
    for d in items:
        lines.append(d['nama'])
        qty = d['jumlah']
        price = d['harga']
        subtotal_item = qty*price
        lines.append(lr32(f"{qty} x Rp {price:,}".replace(",","."), f"Rp {subtotal_item:,}".replace(",",".")))
        total_items += qty
    lines.append("-"*32)
    lines.append(lr32("Total Item", str(total_items)))
    lines.append(lr32("Subtotal", f"Rp {subtotal:,}".replace(",",".")))
    lines.append(lr32(f"PPN ({config.get('ppn')}%)", f"Rp {ppn_amt:,}".replace(",",".")))
    lines.append(lr32(f"Diskon ({config.get('diskon')}%)", f"-Rp {diskon_amt:,}".replace(",",".")))
    lines.append(lr32("Total", f"Rp {total_final:,}".replace(",",".")))
    lines.append(lr32("Tunai", f"Rp {total_paid:,}".replace(",",".")))
    lines.append(lr32("Kembalian", f"Rp {kembalian:,}".replace(",",".")))
    lines.append(f"Pembeli: {buyer}")
    lines.append("")
    lines.append(center32(config.get("footer","")))
    struk_text = "\n".join(lines)
    return struk_text, kode

# ---------------- user page ----------------
def user_page():
    st.title("🍜 Menu & Pesanan")
    st.session_state.buyer_name = st.text_input("Nama Pembeli", value=st.session_state.buyer_name)
    if not st.session_state.buyer_name:
        st.warning("Nama pembeli wajib diisi sebelum memesan.")
    kategori = st.selectbox("Kategori Menu", list(menu_data.keys()))
    item = st.selectbox("Menu", list(menu_data[kategori].keys()))
    qty = st.number_input("Jumlah", min_value=1, value=1)

    if st.button("Tambah ke Keranjang"):
        if not st.session_state.buyer_name:
            st.error("Isi nama pembeli dulu!")
        else:
            checkout.append({"nama": item, "harga": menu_data[kategori][item], "jumlah": qty, "buyer": st.session_state.buyer_name})
            save_json(CHECKOUT_FILE, checkout)
            st.success("✅ Ditambahkan ke keranjang")

    st.subheader("🧾 Keranjang Saat Ini")
    if checkout:
        df = pd.DataFrame(checkout)
        df["total"] = df["harga"]*df["jumlah"]
        df["total"] = df["total"].apply(lambda x: f"Rp {x:,}".replace(",","."))    
        st.table(df)
    else:
        st.info("Keranjang kosong")

# ---------------- admin login ----------------
def admin_login_page():
    st.subheader("🔒 Login Admin")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username=="admin" and password=="123":  # bisa diganti
            st.session_state.admin_logged_in = True
            st.success("✅ Login berhasil")
            st.rerun()
        else:
            st.error("Login salah!")

# ---------------- admin page ----------------
def admin_page():
    st.title("⚙️ Admin Panel")
    menu = st.sidebar.radio("Menu Admin", ["Data Menu", "Data Pesanan", "Pembayaran", "Laporan", "Pengaturan Toko"])
    st.sidebar.button("Logout Admin", on_click=lambda: st.session_state.update({"admin_logged_in": False}))

    if menu == "Data Menu":
        st.subheader("📋 Data Menu")
        # tampilkan menu, tambah, hapus
        rows = []
        for k, items in menu_data.items():
            for n, h in items.items():
                rows.append({"Kategori": k, "Nama": n, "Harga": f"Rp {h:,}".replace(",",".")})
        st.table(pd.DataFrame(rows))

    elif menu == "Data Pesanan":
        st.subheader("📝 Pesanan Masuk")
        if not checkout:
            st.info("Belum ada pesanan.")
        else:
            df = pd.DataFrame(checkout)
            df["total"] = df["harga"]*df["jumlah"]
            df["total"] = df["total"].apply(lambda x: f"Rp {x:,}".replace(",","."))
            st.table(df)

    elif menu == "Pembayaran":
        st.subheader("💳 Pembayaran")
        buyers = list(set(d['buyer'] for d in checkout))
        selected_buyer = st.selectbox("Pilih Pembeli", buyers) if buyers else None
        buyer_items = [d for d in checkout if d['buyer']==selected_buyer]
        if not buyer_items:
            st.info("Belum ada transaksi untuk pembeli ini.")
        else:
            df = pd.DataFrame(buyer_items)
            df["total"] = df["harga"]*df["jumlah"]
            df["total"] = df["total"].apply(lambda x: f"Rp {x:,}".replace(",","."))
            st.table(df)
            total_final = sum(d['harga']*d['jumlah'] for d in buyer_items)
            tunai = st.number_input("Tunai (Rp)", min_value=0, value=total_final)
            if st.button("🖨️ Cetak Struk"):
                struk_text, kode = build_struk(buyer_items, selected_buyer, tunai)
                st.text(struk_text)
                # simpan sales & clear checkout untuk buyer itu
                sales.append({"tanggal":datetime.now(pytz.timezone("Asia/Jakarta")).strftime("%Y-%m-%d"),"total":total_final,"kode":kode,"cashier":config["cashier"],"buyer":selected_buyer,"items":buyer_items.copy()})
                save_json(SALES_FILE, sales)
                # hapus dari checkout
                checkout[:] = [d for d in checkout if d['buyer']!=selected_buyer]
                save_json(CHECKOUT_FILE, checkout)
                st.success("✅ Transaksi dicatat.")

    elif menu == "Laporan":
        st.subheader("📊 Laporan Harian")
        if sales:
            df = pd.DataFrame(sales)
            df["Tanggal"] = pd.to_datetime(df["tanggal"]).dt.strftime("%d/%m/%Y")
            df["Pemasukan"] = df["total"].apply(lambda x: f"Rp {x:,}".replace(",","."))
            st.table(df[["Tanggal","kode","cashier","buyer","Pemasukan"]])
            total_all = sum(s["total"] for s in sales)
            st.write(f"### 💰 Total: Rp {total_all:,}".replace(",","."))

    elif menu == "Pengaturan Toko":
        st.subheader("⚙️ Pengaturan Toko")
        shop_name = st.text_input("Nama Toko", value=config["shop_name"])
        address = st.text_input("Alamat Toko", value=config["address"])
        cashier = st.text_input("Nama Kasir", value=config["cashier"])
        ppn = st.number_input("PPN (%)", 0, 20, config.get("ppn",11))
        diskon = st.number_input("Diskon (%)",0,50, config.get("diskon",0))
        footer = st.text_input("Footer", value=config.get("footer",""))
        if st.button("Simpan Pengaturan"):
            config.update({"shop_name":shop_name,"address":address,"cashier":cashier,"ppn":ppn,"diskon":diskon,"footer":footer})
            save_json(CONFIG_FILE, config)
            st.success("✅ Pengaturan disimpan")
            st.rerun()

# ---------------- routing ----------------
st.sidebar.title("Mie Ayam & Bakso Mas Ragil")
if st.session_state.admin_logged_in:
    admin_page()
else:
    if st.sidebar.button("Admin Login"):
        admin_login_page()
    user_page()
