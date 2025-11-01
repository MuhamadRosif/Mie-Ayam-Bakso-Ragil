# app.py - FULL FINAL
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
    "shop_name": "Mie Ayam & Bakso Mas Ragil",
    "address": "Jl. Kertoharjo",
    "cashier": "ADMIN",
    "counter": 0,
    "ppn": 11,
    "diskon": 2,
    "footer": "Selalu segar bangsat"
})

# ---------------- normalize sales ----------------
for s in sales:
    s.setdefault("kode", "-")
    s.setdefault("cashier", config.get("cashier", "ADMIN"))
    s.setdefault("buyer", "Umum")
    s.setdefault("items", [])

# ---------------- UI setup ----------------
st.set_page_config(page_title="Mie Ayam & Bakso Mas Ragil", page_icon="🍜", layout="centered")
st.markdown("""<style>body{background:#faf6f0;} footer{visibility:hidden;}</style>""", unsafe_allow_html=True)

# ---------------- session defaults ----------------
if "role" not in st.session_state:
    st.session_state.role = None
if "buyer_name" not in st.session_state:
    st.session_state.buyer_name = ""

# ---------------- Login page ----------------
def login_page():
    st.title("🍜 Mie Ayam & Bakso Ragil")
    role = st.selectbox("Masuk sebagai", ["Pelanggan", "Admin"])
    user = st.text_input("Username")
    pw = st.text_input("Password", type="password")
    if st.button("Masuk"):
        if role == "Admin" and user == "admin" and pw == "123":
            st.session_state.role = "admin"
            st.rerun()
        elif role == "Pelanggan" and user == "user" and pw == "123":
            st.session_state.role = "user"
            st.rerun()
        else:
            st.error("Login salah!")

# ---------------- User page ----------------
def user_page():
    st.title("🍜 Menu & Pesanan")
    st.subheader("👤 Nama Pembeli (opsional)")
    st.session_state.buyer_name = st.text_input("Nama Pembeli", value=st.session_state.buyer_name)

    st.subheader("📜 Menu")
    kategori = st.selectbox("Kategori", list(menu_data.keys()))
    item = st.selectbox("Menu", list(menu_data[kategori].keys()))
    qty = st.number_input("Jumlah", min_value=1, value=1)

    if st.button("Tambah ke Keranjang"):
        buyer = st.session_state.buyer_name or "Umum"
        checkout.append({"nama": item, "harga": menu_data[kategori][item], "jumlah": qty, "buyer": buyer})
        save_json(CHECKOUT_FILE, checkout)
        st.success("✅ Ditambahkan ke keranjang")

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

    menu = st.sidebar.radio("Menu Admin", ["Data Menu", "Data Pesanan", "Pembayaran", "Laporan", "Pengaturan Toko"])

    # ---------- Pengaturan Toko ----------
    if menu == "Pengaturan Toko":
        st.subheader("🔧 Pengaturan Toko")
        shop_name = st.text_input("Nama Toko", value=config.get("shop_name"))
        address = st.text_input("Alamat Toko", value=config.get("address"))
        cashier = st.text_input("Nama Kasir Default", value=config.get("cashier"))
        ppn = st.number_input("PPN (%)", 0, 20, value=config.get("ppn"))
        diskon = st.number_input("Diskon (%)", 0, 100, value=config.get("diskon"))
        footer = st.text_input("Footer", value=config.get("footer"))
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Simpan Pengaturan"):
                config.update({"shop_name": shop_name, "address": address, "cashier": cashier, "ppn": ppn, "diskon": diskon, "footer": footer})
                save_json(CONFIG_FILE, config)
                st.success("✅ Pengaturan disimpan")
                st.rerun()
        with col2:
            if st.button("Reset Counter (0)"):
                config["counter"] = 0
                save_json(CONFIG_FILE, config)
                st.success("✅ Counter direset")

    # ---------- Data Menu ----------
    elif menu == "Data Menu":
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

    # ---------- Data Pesanan ----------
    elif menu == "Data Pesanan":
        st.subheader("📝 Pesanan Masuk")
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
            st.info("Belum ada transaksi")
            return

        df = pd.DataFrame(checkout)
        df["subtotal"] = df["harga"] * df["jumlah"]
        st.table(df)

        total_items = sum(i["jumlah"] for i in checkout)
        subtotal = sum(i["subtotal"] for i in df.to_dict('records'))
        ppn_amount = int(subtotal * config["ppn"] / 100)
        diskon_amount = int(subtotal * config["diskon"] / 100)
        total_final = subtotal + ppn_amount - diskon_amount

        tunai = st.number_input("Tunai", min_value=0, value=total_final)
        kembalian = tunai - total_final
        buyer_name = checkout[0].get("buyer", "Umum")

        # build struk
        tz = pytz.timezone("Asia/Jakarta")
        now = datetime.now(tz)
        config["counter"] += 1
        kode = f"RG-{now.strftime('%Y%m%d')}-{config['counter']:05d}"
        save_json(CONFIG_FILE, config)

        def lr32(left, right):
            left_s = str(left)
            right_s = str(right)
            space = 32 - len(left_s) - len(right_s)
            if space < 1:
                left_s = left_s[:32 - len(right_s) - 1]
                space = 1
            return left_s + ' ' * space + right_s

        struk_lines = []
        struk_lines.append(config["shop_name"].center(32))
        struk_lines.append(config["address"].center(32))
        struk_lines.append('-'*32)
        struk_lines.append(f'No. Transaksi: {kode}')
        struk_lines.append(f'Kasir: {config["cashier"]}')
        struk_lines.append(f'Tgl: {now.strftime("%d-%m-%Y %H:%M:%S")} WIB')
        struk_lines.append('-'*32)

        for d in checkout:
            name = d['nama'][:32]
            qty = d['jumlah']
            price = d['harga']
            subtotal_item = qty*price
            struk_lines.append(name)
            struk_lines.append(lr32(f'{qty} x Rp {price:,}'.replace(",", "."), f'Rp {subtotal_item:,}'.replace(",", ".")))

        struk_lines.append('-'*32)
        struk_lines.append(lr32("Total Item", str(total_items)))
        struk_lines.append(lr32("Subtotal", f'Rp {subtotal:,}'.replace(",", ".")))
        struk_lines.append(lr32(f'PPN ({config["ppn"]}%)', f'Rp {ppn_amount:,}'.replace(",", ".")))
        struk_lines.append(lr32(f'Diskon ({config["diskon"]}%)', f'-Rp {diskon_amount:,}'.replace(",", ".")))
        struk_lines.append(lr32("Total", f'Rp {total_final:,}'.replace(",", ".")))
        struk_lines.append(lr32("Tunai", f'Rp {tunai:,}'.replace(",", ".")))
        struk_lines.append(lr32("Kembalian", f'Rp {kembalian:,}'.replace(",", ".")))
        struk_lines.append(lr32("Pembeli", buyer_name))
        struk_lines.append(config["footer"].center(32))
        struk_text = '\n'.join(struk_lines)

        st.text(struk_text)

        # barcode
        code128 = barcode.get('code128', kode, writer=ImageWriter())
        buf_bar = BytesIO()
        code128.write(buf_bar, options={"module_width":0.2, "module_height":15, "font_size":10})
        buf_bar.seek(0)
        st.image(buf_bar, width=230)

        # simpan transaksi
        sales.append({"tanggal": now.strftime('%Y-%m-%d'), "total": total_final, "kode": kode, "cashier": config["cashier"], "buyer": buyer_name, "items": checkout.copy()})
        save_json(SALES_FILE, sales)

        # clear checkout
        checkout.clear()
        save_json(CHECKOUT_FILE, checkout)

    # ---------- Laporan ----------
    elif menu == "Laporan":
        st.subheader("📊 Laporan Harian")
        if not sales:
            st.info("Belum ada transaksi.")
        else:
            df = pd.DataFrame(sales)
            df['Tanggal'] = pd.to_datetime(df['tanggal']).dt.strftime('%d/%m/%Y')
            df['Pemasukan'] = df['total'].apply(lambda x: f'Rp {x:,}'.replace(',', '.'))
            st.table(df[['Tanggal','Pemasukan','kode','cashier','buyer']])
            st.write(f"### 💰 Total: Rp {sum(s['total'] for s in sales):,}".replace(',', '.'))

# ---------------- routing ----------------
if st.session_state.role == "admin":
    if st.sidebar.button("Logout"):
        st.session_state.role = None
        st.rerun()
    admin_page()
elif st.session_state.role == "user":
    if st.sidebar.button("Logout"):
        st.session_state.role = None
        st.rerun()
    user_page()
else:
    login_page()
