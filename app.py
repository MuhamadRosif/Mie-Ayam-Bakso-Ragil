# app.py - FINAL Full Version with esthetic struk
import streamlit as st
import json, os
import pandas as pd
from datetime import datetime
import pytz
from io import BytesIO
import qrcode

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
if "page" not in st.session_state:
    st.session_state.page = "user"
if "admin_logged" not in st.session_state:
    st.session_state.admin_logged = False
if "buyer_name" not in st.session_state:
    st.session_state.buyer_name = ""

# ---------------- helpers: struk formatting ----------------
def center32(text):
    return str(text).center(32)

def lr32(left, right):
    left_s = str(left)
    right_s = str(right)
    space = 32 - len(left_s) - len(right_s)
    if space < 1:
        left_s = left_s[:32 - len(right_s) - 1]
        space = 1
    return left_s + (" " * space) + right_s

# ---------------- pages ----------------
def user_page():
    st.title("🍜 Menu & Pesanan")
    st.subheader("👤 Nama Pembeli (wajib diisi)")
    st.session_state.buyer_name = st.text_input("Nama Pembeli", value=st.session_state.buyer_name)

    disable_order = not st.session_state.buyer_name
    if disable_order:
        st.warning("Nama pembeli wajib diisi sebelum memesan")

    st.subheader("📜 Menu")
    kategori = st.selectbox("Kategori", list(menu_data.keys()))
    item = st.selectbox("Menu", list(menu_data[kategori].keys()))
    qty = st.number_input("Jumlah", min_value=1, value=1)

    if st.button("Tambah ke Keranjang", disabled=disable_order):
        buyer = st.session_state.buyer_name
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

    # Sidebar admin login
    if not st.session_state.admin_logged:
        if st.sidebar.button("Admin Login"):
            st.session_state.page = "admin_login"
            st.rerun()

def admin_login_page():
    st.title("🔒 Admin Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username=="admin" and password=="123":
            st.session_state.admin_logged = True
            st.session_state.page = "admin_panel"
            st.success("Login berhasil!")
            st.rerun()
        else:
            st.error("Username/Password salah")
    if st.button("Kembali ke Menu User"):
        st.session_state.page = "user"
        st.rerun()

def admin_page():
    st.sidebar.title("⚙️ Admin Panel")
    menu = st.sidebar.radio("Menu Admin", ["Data Menu","Data Pesanan","Pembayaran","Laporan","Pengaturan Toko"])
    if st.sidebar.button("Logout Admin"):
        st.session_state.admin_logged = False
        st.session_state.page = "user"
        st.success("Logout berhasil")
        st.rerun()

    if menu == "Data Menu":
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

        st.subheader("🗑️ Hapus Menu")
        del_kat = st.selectbox("Pilih Kategori", list(menu_data.keys()))
        del_item = st.selectbox("Pilih Menu", list(menu_data[del_kat].keys()))
        if st.button("Hapus Menu"):
            del menu_data[del_kat][del_item]
            save_json(MENU_FILE, menu_data)
            st.success("✅ Menu dihapus")
            st.rerun()

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

    elif menu == "Pembayaran":
        st.header("💳 Pembayaran")
        if not checkout:
            st.info("Belum ada transaksi")
            return

        buyers = list({c["buyer"] for c in checkout})
        selected_buyer = st.selectbox("Pilih Pembeli", buyers)
        buyer_checkout = [c for c in checkout if c["buyer"]==selected_buyer]
        df = pd.DataFrame(buyer_checkout)
        df["total"] = df["harga"] * df["jumlah"]
        df["total"] = df["total"].apply(lambda x: f"Rp {x:,}".replace(",", "."))
        st.table(df)

        subtotal = sum(i["harga"]*i["jumlah"] for i in buyer_checkout)
        ppn_amt = int(subtotal * config.get("ppn",11)/100)
        diskon_amt = int(subtotal * config.get("diskon",2)/100)
        total_final = subtotal + ppn_amt - diskon_amt

        st.write(f"Subtotal: Rp {subtotal:,}".replace(",", "."))
        st.write(f"PPN ({config.get('ppn')}%): Rp {ppn_amt:,}".replace(",", "."))
        st.write(f"Diskon ({config.get('diskon')}%): -Rp {diskon_amt:,}".replace(",", "."))
        st.write(f"Total: Rp {total_final:,}".replace(",", "."))
        tunai = st.number_input("Tunai", min_value=0, value=total_final)
        kembalian = tunai - total_final
        st.write(f"Kembalian: Rp {kembalian:,}".replace(",", "."))

        if st.button("🖨️ Cetak Struk"):
            tz = pytz.timezone("Asia/Jakarta")
            now = datetime.now(tz)
            config["counter"] +=1
            save_json(CONFIG_FILE, config)
            kode = f"RG-{now.strftime('%Y%m%d')}-{config['counter']:05d}"

            lines=[]
            lines.append(center32(config.get("shop_name")))
            lines.append(center32(config.get("address")))
            lines.append("-"*32)
            lines.append(f"No. Transaksi: {kode}")
            lines.append(f"Kasir: {config.get('cashier')}")
            lines.append(f"Tgl: {now.strftime('%d-%m-%Y %H:%M:%S')} WIB")
            lines.append("-"*32)

            # item list
            for i in buyer_checkout:
                lines.append(f"{i['nama']}")
                qty_price = f"{i['jumlah']} x Rp {i['harga']:,}".replace(",", ".")
                total_item = f"Rp {i['jumlah']*i['harga']:,}".replace(",", ".")
                lines.append(lr32(qty_price, total_item))

            lines.append("-"*32)
            total_items = sum(i["jumlah"] for i in buyer_checkout)
            lines.append(lr32("Total Item", total_items))
            lines.append(lr32("Subtotal", f"Rp {subtotal:,}".replace(",", ".")))
            lines.append(lr32(f"PPN ({config.get('ppn')}%)", f"Rp {ppn_amt:,}".replace(",", ".")))
            lines.append(lr32(f"Diskon ({config.get('diskon')}%)", f"-Rp {diskon_amt:,}".replace(",", ".")))
            lines.append(lr32("Total", f"Rp {total_final:,}".replace(",", ".")))
            lines.append(lr32("Tunai", f"Rp {tunai:,}".replace(",", ".")))
            lines.append(lr32("Kembalian", f"Rp {kembalian:,}".replace(",", ".")))
            lines.append(f"Pembeli: {selected_buyer}")
            lines.append("-"*32)
            lines.append(center32(config.get("footer")))
            lines.append(center32("Saya Muhamad Rosif Al Khikam Development Aplikasi ini"))

            st.text("\n".join(lines))

            # static QR
            qr = qrcode.QRCode(box_size=2, border=1)
            qr.add_data("Saya Muhamad Rosif Al Khikam Development Aplikasi ini")
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            st.image(img)

            # save sale
            sales.append({
                "tanggal": now.strftime("%Y-%m-%d"),
                "total": total_final,
                "kode": kode,
                "cashier": config.get("cashier"),
                "buyer": selected_buyer,
                "items": buyer_checkout
            })
            save_json(SALES_FILE, sales)

            # remove checkout for this buyer
            checkout[:] = [c for c in checkout if c["buyer"]!=selected_buyer]
            save_json(CHECKOUT_FILE, checkout)
            st.success("✅ Struk dicetak dan transaksi disimpan")

            # reload ke user page
            st.session_state.page = "user"
            st.rerun()

    elif menu=="Laporan":
        st.header("📊 Laporan Harian")
        if not sales:
            st.info("Belum ada transaksi.")
        else:
            df = pd.DataFrame(sales)
            df["Tanggal"] = pd.to_datetime(df["tanggal"]).dt.strftime("%d/%m/%Y")
            df["Pemasukan"] = df["total"].apply(lambda x: f"Rp {x:,}".replace(",", "."))
            cols = ["Tanggal","Pemasukan"]
            for c in ["kode","cashier","buyer"]:
                if c in df.columns:
                    cols.append(c)
            st.table(df[cols])
            total_all = sum(s["total"] for s in sales)
            st.write(f"### 💰 Total: Rp {total_all:,}".replace(",", "."))

            st.subheader("🗑️ Hapus Transaksi")
            pilih_kode = st.selectbox("Pilih kode transaksi yang mau dihapus", [s.get("kode", f"no-{i}") for i,s in enumerate(sales)])
            if st.button("Hapus Transaksi"):
                sales[:] = [s for s in sales if s.get("kode")!=pilih_kode]
                save_json(SALES_FILE, sales)
                st.success(f"✅ Transaksi {pilih_kode} dihapus")
                st.rerun()

    elif menu=="Pengaturan Toko":
        st.header("🛠️ Pengaturan Toko")
        shop_name = st.text_input("Nama Toko", value=config.get("shop_name"))
        address = st.text_input("Alamat Toko", value=config.get("address"))
        cashier = st.text_input("Nama Kasir", value=config.get("cashier"))
        ppn = st.number_input("PPN (%)", 0, 100, value=config.get("ppn"))
        diskon = st.number_input("Diskon (%)", 0, 100, value=config.get("diskon"))
        footer = st.text_input("Footer", value=config.get("footer"))
        col1,col2 = st.columns(2)
        with col1:
            if st.button("Simpan Pengaturan"):
                config.update({
                    "shop_name": shop_name,
                    "address": address,
                    "cashier": cashier,
                    "ppn": ppn,
                    "diskon": diskon,
                    "footer": footer
                })
                save_json(CONFIG_FILE, config)
                st.success("✅ Pengaturan tersimpan")
                st.rerun()
        with col2:
            if st.button("Reset Counter"):
                config["counter"]=0
                save_json(CONFIG_FILE, config)
                st.success("✅ Counter direset")
                st.rerun()

# ---------------- routing ----------------
if st.session_state.page=="user":
    user_page()
elif st.session_state.page=="admin_login":
    admin_login_page()
elif st.session_state.page=="admin_panel" and st.session_state.admin_logged:
    admin_page()
else:
    st.session_state.page="user"
    st.rerun()
