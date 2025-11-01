# app.py - FULL FINAL (User menu + Admin sidebar login + Struk rapi Alfamart)
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
    "diskon": 2,
    "footer": "Selalu segar bangsat"
})

# normalize old sales
for s in sales:
    s.setdefault("kode", "-")
    s.setdefault("cashier", config.get("cashier", "ADMIN RAGIL"))
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

def build_struk(items, buyer_name, total_tunai):
    tz = pytz.timezone("Asia/Jakarta")
    now = datetime.now(tz)
    config["counter"] += 1
    save_json(CONFIG_FILE, config)
    kode = f"RG-{now.strftime('%Y%m%d')}-{config['counter']:05d}"

    lines = []
    lines.append(center32(config["shop_name"]))
    lines.append(center32(config["address"]))
    lines.append(center32(""))
    lines.append("-"*32)

    lines.append(f"No. Transaksi: {kode}")
    lines.append(f"Kasir: {config['cashier']}")
    lines.append(f"Tgl: {now.strftime('%d-%m-%Y %H:%M:%S')} WIB")
    lines.append("-"*32)

    total_item = 0
    subtotal = 0
    for d in items:
        name = d["nama"][:32]
        qty = d["jumlah"]
        price = d["harga"]
        sub = qty*price
        lines.append(name)
        lines.append(lr32(f"{qty} x Rp {price:,}".replace(",", "."), f"Rp {sub:,}".replace(",", ".")))
        total_item += qty
        subtotal += sub

    ppn_amt = int(subtotal * config["ppn"]/100)
    diskon_amt = int(subtotal * config["diskon"]/100)
    total_final = subtotal + ppn_amt - diskon_amt
    kembalian = total_tunai - total_final

    lines.append("-"*32)
    lines.append(lr32("Total Item", total_item))
    lines.append(lr32("Subtotal", f"Rp {subtotal:,}".replace(",", ".")))
    lines.append(lr32(f'PPN ({config["ppn"]}%)', f"Rp {ppn_amt:,}".replace(",", ".")))
    lines.append(lr32(f'Diskon ({config["diskon"]}%)', f"-Rp {diskon_amt:,}".replace(",", ".")))
    lines.append(lr32("Total", f"Rp {total_final:,}".replace(",", ".")))
    lines.append(lr32("Tunai", f"Rp {total_tunai:,}".replace(",", ".")))
    lines.append(lr32("Kembalian", f"Rp {kembalian:,}".replace(",", ".")))
    lines.append(f"Pembeli: {buyer_name}")
    lines.append("")
    lines.append(center32(config["footer"]))

    # save sale
    sales.append({
        "tanggal": now.strftime("%Y-%m-%d"),
        "total": total_final,
        "kode": kode,
        "cashier": config["cashier"],
        "buyer": buyer_name,
        "items": items.copy()
    })
    save_json(SALES_FILE, sales)
    # hapus checkout untuk buyer itu saja
    checkout[:] = [c for c in checkout if c["buyer"] != buyer_name]
    save_json(CHECKOUT_FILE, checkout)
    return "\n".join(lines), kode

# ---------------- USER PAGE ----------------
st.title("🍜 Menu & Pesanan")
st.subheader("👤 Nama Pembeli (wajib diisi)")
st.session_state.buyer_name = st.text_input("Nama Pembeli", value=st.session_state.buyer_name)
if not st.session_state.buyer_name:
    st.warning("Nama pembeli wajib diisi sebelum memesan!")

st.subheader("📜 Menu")
kategori = st.selectbox("Kategori", list(menu_data.keys()))
item = st.selectbox("Menu", list(menu_data[kategori].keys()))
qty = st.number_input("Jumlah", min_value=1, value=1)

if st.button("Tambah ke Keranjang"):
    if not st.session_state.buyer_name:
        st.error("Isi nama pembeli dulu!")
    else:
        buyer = st.session_state.buyer_name
        checkout.append({"nama": item, "harga": menu_data[kategori][item], "jumlah": qty, "buyer": buyer})
        save_json(CHECKOUT_FILE, checkout)
        st.success("✅ Ditambahkan ke keranjang")

st.subheader("🧾 Keranjang Saat Ini")
if checkout:
    df = pd.DataFrame(checkout)
    df["total"] = df["harga"]*df["jumlah"]
    df["total"] = df["total"].apply(lambda x: f"Rp {x:,}".replace(",", "."))
    st.table(df)
else:
    st.info("Keranjang kosong")

# ---------------- SIDEBAR ADMIN ----------------
st.sidebar.title("Admin Panel")
if not st.session_state.admin_logged_in:
    if st.sidebar.button("Admin Login"):
        st.session_state.show_login = True

if hasattr(st.session_state, "show_login") and st.session_state.show_login and not st.session_state.admin_logged_in:
    st.sidebar.subheader("Login Admin")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Masuk"):
        if username == "admin" and password == "123":
            st.session_state.admin_logged_in = True
            st.session_state.show_login = False
            st.success("Login Admin berhasil!")
            st.rerun()
        else:
            st.sidebar.error("Login salah!")

if st.session_state.admin_logged_in:
    menu_admin = st.sidebar.radio("Menu Admin", ["Data Menu", "Data Pesanan", "Pembayaran", "Laporan", "Pengaturan Toko"])
    if st.sidebar.button("Logout Admin"):
        st.session_state.admin_logged_in = False
        st.success("Admin logout berhasil!")
        st.rerun()

    # ------------- ADMIN FUNCTIONALITY -------------
    if menu_admin == "Data Menu":
        st.subheader("📋 Data Menu")
        rows = []
        for k, items in menu_data.items():
            for n, h in items.items():
                rows.append({"Kategori": k, "Nama": n, "Harga": f"Rp {h:,}".replace(",", ".")})
        st.table(pd.DataFrame(rows))

        st.subheader("➕ Tambah/Edit Menu")
        kat = st.selectbox("Kategori", list(menu_data.keys()))
        nama = st.text_input("Nama Menu")
        harga = st.number_input("Harga (Rp)", min_value=0)
        if st.button("Simpan Menu"):
            menu_data[kat][nama] = harga
            save_json(MENU_FILE, menu_data)
            st.success("✅ Menu disimpan")
            st.rerun()

        st.subheader("🗑️ Hapus Menu")
        del_kat = st.selectbox("Pilih Kategori", list(menu_data.keys()))
        del_item = st.selectbox("Pilih Menu", list(menu_data[del_kat].keys()))
        if st.button("Hapus Menu"):
            del menu_data[del_kat][del_item]
            save_json(MENU_FILE, menu_data)
            st.success("✅ Menu dihapus")
            st.rerun()

# ---------------- END OF FILE ----------------
