# app.py - Mie Ayam & Bakso Mas Ragil (Final Full)
import streamlit as st
import json, os
import pandas as pd
from datetime import datetime
import pytz
from io import BytesIO
import qrcode
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
    "cashier": "ADMIN RAGIL", "counter": 0, 
    "shop_name": "MIE AYAM MAS RAGIL", "address": "Jl. Rasa Bahagia No.1",
    "ppn": 11, "diskon": 0, "footer": "Terima kasih telah berbelanja!"
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
if "role" not in st.session_state:
    st.session_state.role = None
if "buyer_name" not in st.session_state:
    st.session_state.buyer_name = ""

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
    st.session_state.buyer_name = st.text_input("Nama Pembeli (wajib diisi)", value=st.session_state.buyer_name)
    if not st.session_state.buyer_name.strip():
        st.warning("Nama pembeli harus diisi sebelum memesan.")
        return

    st.subheader("📜 Menu")
    kategori = st.selectbox("Kategori", list(menu_data.keys()))
    item = st.selectbox("Menu", list(menu_data[kategori].keys()))
    qty = st.number_input("Jumlah", min_value=1, value=1)

    if st.button("Tambah ke Keranjang"):
        buyer = st.session_state.buyer_name.strip()
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
    st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"role": None}))
    st.title("⚙️ Admin Panel")

    menu = st.sidebar.radio("Menu Admin", ["Data Menu", "Data Pesanan", "Pembayaran", "Laporan", "Pengaturan Toko"])

    # ---------- Pengaturan Toko ----------
    if menu == "Pengaturan Toko":
        st.subheader("🏪 Pengaturan Toko")
        shop_name = st.text_input("Nama Toko", value=config.get("shop_name"))
        address = st.text_input("Alamat Toko", value=config.get("address"))
        cashier_name = st.text_input("Nama Kasir Default", value=config.get("cashier"))
        ppn = st.number_input("PPN (%)", 0, 20, config.get("ppn",11))
        diskon = st.number_input("Diskon (%)", 0, 50, config.get("diskon",0))
        footer = st.text_input("Footer Struk", value=config.get("footer"))

        if st.button("Simpan Pengaturan"):
            config.update({"shop_name": shop_name, "address": address, "cashier": cashier_name,
                           "ppn": ppn, "diskon": diskon, "footer": footer})
            save_json(CONFIG_FILE, config)
            st.success("✅ Pengaturan disimpan")
            st.rerun()

    # ---------- Data Menu ----------
    elif menu == "Data Menu":
        st.subheader("📋 Data Menu")
        rows = []
        for k, items in menu_data.items():
            for n, h in items.items():
                rows.append({"Kategori": k, "Nama": n, "Harga": f"Rp {h:,}".replace(',', '.')})
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
        else:
            df = pd.DataFrame(checkout)
            df["subtotal"] = df["harga"] * df["jumlah"]
            st.table(df[["nama","jumlah","harga","subtotal"]])

            subtotal = sum(i["harga"]*i["jumlah"] for i in checkout)
            ppn_amt = int(subtotal * config.get("ppn",0)/100)
            diskon_amt = int(subtotal * config.get("diskon",0)/100)
            total_final = subtotal + ppn_amt - diskon_amt

            tunai = st.number_input("Tunai (Rp)", min_value=0, value=total_final)
            kembalian = tunai - total_final
            st.write(f"Kembalian: Rp {kembalian:,}".replace(',', '.'))
            st.write(f"Nama Pembeli: {checkout[0]['buyer']}")

            # WIB timezone
            tz = pytz.timezone("Asia/Jakarta")
            now = datetime.now(tz)

            # thermal helpers
            def center32(text):
                return str(text).center(32)
            def lr32(left,right):
                space = 32 - len(str(left)) - len(str(right))
                return str(left) + " "*max(space,1) + str(right)

            # build struk
            lines=[]
            lines.append(center32(config.get("shop_name")))
            lines.append(center32(config.get("address")))
            lines.append("-"*32)
            lines.append(f"No. Transaksi: RG-{now.strftime('%Y%m%d')}-{config.get('counter',0):05d}")
            lines.append(f"Kasir: {config.get('cashier')}")
            lines.append(f"Tgl: {now.strftime('%d-%m-%Y %H:%M:%S')} WIB")
            lines.append("-"*32)

            total_items = sum(i["jumlah"] for i in checkout)
            for d in checkout:
                lines.append(d["nama"])
                lines.append(lr32(f"{d['jumlah']} x Rp {d['harga']:,}".replace(',', '.'), f"Rp {d['harga']*d['jumlah']:,}".replace(',', '.')))

            lines.append("-"*32)
            lines.append(lr32("Total Item", total_items))
            lines.append(lr32("Subtotal", f"Rp {subtotal:,}".replace(',', '.')))
            lines.append(lr32(f"PPN ({config.get('ppn')}%)", f"Rp {ppn_amt:,}".replace(',', '.')))
            lines.append(lr32(f"Diskon ({config.get('diskon')}%)", f"-Rp {diskon_amt:,}".replace(',', '.')))
            lines.append(lr32("Total", f"Rp {total_final:,}".replace(',', '.')))
            lines.append(lr32("Tunai", f"Rp {tunai:,}".replace(',', '.')))
            lines.append(lr32("Kembalian", f"Rp {kembalian:,}".replace(',', '.')))
            lines.append(f"Pembeli: {checkout[0]['buyer']}")
            lines.append(center32(config.get("footer","")))

            if st.button("🖨️ Cetak Struk"):
                config["counter"] +=1
                save_json(CONFIG_FILE, config)
                st.text("\n".join(lines))

                # barcode
                CODE = f"RG-{now.strftime('%Y%m%d')}-{config['counter']:05d}"
                code128 = barcode.get('code128', CODE, writer=ImageWriter())
                buf_bar = BytesIO()
                code128.write(buf_bar, options={"module_width":0.2,"module_height":15,"font_size":10})
                buf_bar.seek(0)
                st.image(buf_bar)

                # save sale
                sales.append({"tanggal": now.strftime("%Y-%m-%d"), "total": total_final, "kode": CODE,
                              "cashier": config.get("cashier"), "buyer": checkout[0]["buyer"],
                              "items": checkout.copy()})
                save_json(SALES_FILE, sales)
                checkout.clear()
                save_json(CHECKOUT_FILE, checkout)
                st.success("✅ Transaksi disimpan, struk tampil.")

    # ---------- Laporan ----------
    elif menu == "Laporan":
        st.subheader("📊 Laporan Harian")
        if not sales:
            st.info("Belum ada transaksi.")
        else:
            df = pd.DataFrame(sales)
            df["Tanggal"] = pd.to_datetime(df["tanggal"]).dt.strftime("%d/%m/%Y")
            df["Pemasukan"] = df["total"].apply(lambda x: f"Rp {x:,}".replace(",", "."))
            cols = ["Tanggal","Pemasukan"]
            for c in ["kode","cashier","buyer"]:
                if c in df.columns: cols.append(c)
            st.table(df[cols])
            total_all = sum(s["total"] for s in sales)
            st.write(f"### 💰 Total: Rp {total_all:,}".replace(",","."))

            st.subheader("🗑️ Hapus Transaksi")
            pilih_kode = st.selectbox("Pilih kode transaksi yang mau dihapus", [s.get("kode",f"no-{i}") for i,s in enumerate(sales)])
            if st.button("Hapus Transaksi"):
                sales[:] = [s for s in sales if s.get("kode")!=pilih_kode]
                save_json(SALES_FILE, sales)
                st.success(f"✅ Transaksi {pilih_kode} dihapus")
                st.rerun()

# ---------------- routing ----------------
if st.session_state.role == "admin":
    admin_page()
elif st.session_state.role == "user":
    st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"role": None}))
    user_page()
else:
    login_page()
