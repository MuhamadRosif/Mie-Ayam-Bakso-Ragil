# app.py - FINAL FULL (Alfamart-style, multiple buyers, PPN, Diskon, Footer)
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

# ---------------- normalize old sales ----------------
for s in sales:
    s.setdefault("kode", "-")
    s.setdefault("cashier", config.get("cashier", "ADMIN RAGIL"))
    s.setdefault("buyer", "Umum")
    s.setdefault("items", [])

# ---------------- UI setup ----------------
st.set_page_config(page_title="Mie Ayam Mas Ragil", page_icon="🍜", layout="centered")
st.markdown("""<style>body{background:#faf6f0;} footer{visibility:hidden;}</style>""", unsafe_allow_html=True)

# ---------------- session defaults ----------------
if "role" not in st.session_state:
    st.session_state.role = None
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
    return left_s + " "*space + right_s

# ---------------- Login page ----------------
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

# ---------------- User page ----------------
def user_page():
    st.title("🍜 Menu & Pesanan")
    st.subheader("👤 Nama Pembeli (wajib diisi)")
    st.session_state.buyer_name = st.text_input("Nama Pembeli", value=st.session_state.buyer_name)

    if st.session_state.buyer_name.strip() == "":
        st.warning("Nama harus diisi sebelum memesan.")
        return

    st.subheader("📜 Menu")
    kategori = st.selectbox("Kategori", list(menu_data.keys()))
    item = st.selectbox("Menu", list(menu_data[kategori].keys()))
    qty = st.number_input("Jumlah", min_value=1, value=1)

    if st.button("Tambah ke Keranjang"):
        buyer = st.session_state.buyer_name
        checkout.append({"nama": item, "harga": menu_data[kategori][item], "jumlah": qty, "buyer": buyer})
        save_json(CHECKOUT_FILE, checkout)
        st.success(f"✅ {item} ditambahkan ke keranjang")

    st.subheader("🧾 Keranjang Saat Ini")
    if checkout:
        df = pd.DataFrame(checkout)
        df["total"] = df["harga"] * df["jumlah"]
        df["total"] = df["total"].apply(lambda x: f"Rp {x:,}".replace(",", "."))
        st.table(df)
    else:
        st.info("Keranjang kosong")

# ---------------- Admin page ----------------
def admin_page():
    st.title("⚙️ Admin Panel")
    st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"role": None}))
    menu = st.sidebar.radio("Menu Admin", ["Data Menu", "Data Pesanan", "Pembayaran", "Laporan", "Pengaturan Toko"])

    # ---------- Pengaturan Toko ----------
    if menu == "Pengaturan Toko":
        st.header("🏪 Pengaturan Toko")
        config["shop_name"] = st.text_input("Nama Toko", value=config.get("shop_name"))
        config["address"] = st.text_input("Alamat Toko", value=config.get("address"))
        config["cashier"] = st.text_input("Nama Kasir Default", value=config.get("cashier"))
        config["ppn"] = st.number_input("PPN (%)", min_value=0, max_value=100, value=config.get("ppn", 0))
        config["diskon"] = st.number_input("Diskon (%)", min_value=0, max_value=100, value=config.get("diskon", 0))
        config["footer"] = st.text_input("Footer Struk", value=config.get("footer"))
        if st.button("Simpan Pengaturan"):
            save_json(CONFIG_FILE, config)
            st.success("✅ Pengaturan toko disimpan")
            st.rerun()

    # ---------- Data Menu ----------
    elif menu == "Data Menu":
        st.header("📋 Data Menu")
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

    # ---------- Data Pesanan ----------
    elif menu == "Data Pesanan":
        st.header("📝 Pesanan Masuk")
        if not checkout:
            st.info("Belum ada pesanan.")
        else:
            df = pd.DataFrame(checkout)
            df["total"] = df["harga"] * df["jumlah"]
            df["total"] = df["total"].apply(lambda x: f"Rp {x:,}".replace(",", "."))
            st.table(df)
            if st.button("Hapus Semua Pesanan"):
                checkout.clear()
                save_json(CHECKOUT_FILE, checkout)
                st.success("✅ Semua pesanan dibersihkan")
                st.rerun()

    # ---------- Pembayaran ----------
    elif menu == "Pembayaran":
        st.header("💳 Pembayaran")
        if not checkout:
            st.info("Belum ada transaksi.")
            return

        buyers = list(set(c["buyer"] for c in checkout))
        selected_buyer = st.selectbox("Pilih Pembeli", buyers)
        buyer_checkout = [c for c in checkout if c["buyer"] == selected_buyer]

        subtotal = sum(i["harga"]*i["jumlah"] for i in buyer_checkout)
        ppn_amt = int(subtotal*config["ppn"]/100)
        diskon_amt = int(subtotal*config["diskon"]/100)
        total_final = subtotal + ppn_amt - diskon_amt

        tunai = st.number_input("Tunai", min_value=0, value=total_final)
        kembalian = max(tunai - total_final, 0)

        # struk
        tz = pytz.timezone("Asia/Jakarta")
        now = datetime.now(tz)
        counter = config.get("counter",0)+1
        config["counter"] = counter
        save_json(CONFIG_FILE, config)
        kode = f"RG-{now.strftime('%Y%m%d')}-{counter:05d}"

        lines = []
        lines.append(center32(config["shop_name"]))
        lines.append(center32(config["address"]))
        lines.append("-"*32)
        lines.append(f"No. Transaksi: {kode}")
        lines.append(f"Kasir: {config['cashier']}")
        lines.append(f"Tgl: {now.strftime('%d-%m-%Y %H:%M:%S')} WIB")
        lines.append("-"*32)
        for i in buyer_checkout:
            lines.append(i["nama"])
            lines.append(lr32(f'{i["jumlah"]} x Rp {i["harga"]:,}'.replace(",","."), f'Rp {i["jumlah"]*i["harga"]:,}'.replace(",",".")))
        lines.append("-"*32)
        lines.append(lr32("Total Item", str(sum(i["jumlah"] for i in buyer_checkout))))
        lines.append(lr32("Subtotal", f'Rp {subtotal:,}'.replace(",",".")))
        lines.append(lr32(f'PPN ({config["ppn"]}%)', f'Rp {ppn_amt:,}'.replace(",",".")))
        lines.append(lr32(f'Diskon ({config["diskon"]}%)', f'-Rp {diskon_amt:,}'.replace(",",".")))
        lines.append(lr32("Total", f'Rp {total_final:,}'.replace(",",".")))
        lines.append(lr32("Tunai", f'Rp {tunai:,}'.replace(",",".")))
        lines.append(lr32("Kembalian", f'Rp {kembalian:,}'.replace(",",".")))
        lines.append(f'Pembeli: {selected_buyer}')
        lines.append(center32(config.get("footer","")))

        struk_text = "\n".join(lines)
        st.text(struk_text)

        # finalize transaction
        if st.button("✅ Simpan Transaksi & Hapus Pesanan Pembeli Ini"):
            sales.append({"tanggal": now.strftime("%Y-%m-%d"),"kode": kode,"cashier": config['cashier'],"buyer": selected_buyer,"items": buyer_checkout,"total": total_final})
            save_json(SALES_FILE, sales)
            checkout[:] = [c for c in checkout if c["buyer"] != selected_buyer]
            save_json(CHECKOUT_FILE, checkout)
            st.success("✅ Transaksi tersimpan dan checkout pembeli ini dibersihkan")

    # ---------- Laporan ----------
    elif menu == "Laporan":
        st.header("📊 Laporan Harian")
        if not sales:
            st.info("Belum ada transaksi.")
        else:
            df = pd.DataFrame(sales)
            df["Tanggal"] = pd.to_datetime(df["tanggal"]).dt.strftime("%d/%m/%Y")
            df["Pemasukan"] = df["total"].apply(lambda x: f"Rp {x:,}".replace(",","."))
            cols = ["Tanggal", "Pemasukan"]
            for c in ["kode","cashier","buyer"]:
                if c in df.columns:
                    cols.append(c)
            st.table(df[cols])
            total_all = sum(s["total"] for s in sales)
            st.write(f"### 💰 Total: Rp {total_all:,}".replace(",","."))

            st.subheader("🗑️ Hapus Transaksi")
            pilih_kode = st.selectbox("Pilih kode transaksi yang mau dihapus", [s.get("kode", f"no-{i}") for i, s in enumerate(sales)])
            if st.button("Hapus Transaksi"):
                sales[:] = [s for s in sales if s.get("kode") != pilih_kode]
                save_json(SALES_FILE, sales)
                st.success(f"✅ Transaksi {pilih_kode} dihapus")
                st.rerun()

# ---------------- routing ----------------
if st.session_state.role == "admin":
    admin_page()
elif st.session_state.role == "user":
    user_page()
else:
    login_page()
