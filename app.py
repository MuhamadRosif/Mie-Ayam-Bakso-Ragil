# app.py - FINAL (Struk thermal Alfamart style + Code128 + WIB timezone + admin sidebar)
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
    "footer": "Selalu Segar Bangsat"
})

# normalize old sales entries
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
        df["subtotal"] = df["harga"] * df["jumlah"]
        df_display = df[["nama", "jumlah", "harga", "subtotal"]]
        df_display = df_display.rename(columns={"nama": "Nama", "jumlah": "Jml", "harga": "Harga", "subtotal": "Subtotal"})
        df_display["Harga"] = df_display["Harga"].apply(lambda x: f"{x:,}".replace(",", "."))
        df_display["Subtotal"] = df_display["Subtotal"].apply(lambda x: f"{x:,}".replace(",", "."))
        st.table(df_display)
    else:
        st.info("Keranjang kosong")

# ---------------- Admin page ----------------
def admin_page():
    st.title("⚙️ Admin Panel")

    menu = st.sidebar.radio("Menu Admin", ["Data Menu", "Data Pesanan", "Pembayaran", "Laporan", "Pengaturan Toko"])

    # ---- Pengaturan Toko ----
    if menu == "Pengaturan Toko":
        st.header("🛠️ Pengaturan Toko")
        shop_name = st.text_input("Nama Toko", value=config.get("shop_name"))
        address = st.text_input("Alamat Toko", value=config.get("address"))
        cashier_name = st.text_input("Nama Kasir Default", value=config.get("cashier"))
        ppn = st.number_input("PPN (%)", 0, 100, config.get("ppn", 11))
        diskon = st.number_input("Diskon (%)", 0, 100, config.get("diskon", 0))
        footer = st.text_input("Footer Struk", value=config.get("footer", "Selalu Segar Bangsat"))
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Simpan Pengaturan"):
                config["shop_name"] = shop_name.strip()
                config["address"] = address.strip()
                config["cashier"] = cashier_name.strip()
                config["ppn"] = ppn
                config["diskon"] = diskon
                config["footer"] = footer.strip()
                save_json(CONFIG_FILE, config)
                st.success("✅ Pengaturan disimpan")
                st.rerun()
        with col2:
            if st.button("Reset Counter (0)"):
                config["counter"] = 0
                save_json(CONFIG_FILE, config)
                st.success("✅ Counter direset")

    # ---- Data Menu ----
    elif menu == "Data Menu":
        st.subheader("📋 Data Menu")
        rows = []
        for k, items in menu_data.items():
            for n, h in items.items():
                rows.append({"Kategori": k, "Nama": n, "Harga": f"Rp {h:,}".replace(",", ".")})
        st.table(pd.DataFrame(rows))

    # ---- Data Pesanan ----
    elif menu == "Data Pesanan":
        st.subheader("📝 Pesanan Masuk")
        if not checkout:
            st.info("Belum ada pesanan.")
        else:
            df = pd.DataFrame(checkout)
            df["subtotal"] = df["harga"] * df["jumlah"]
            df_display = df[["nama","jumlah","harga","subtotal"]]
            df_display = df_display.rename(columns={"nama":"Nama","jumlah":"Jml","harga":"Harga","subtotal":"Subtotal"})
            df_display["Harga"] = df_display["Harga"].apply(lambda x: f"{x:,}".replace(",", "."))
            df_display["Subtotal"] = df_display["Subtotal"].apply(lambda x: f"{x:,}".replace(",", "."))
            st.table(df_display)
            if st.button("Hapus Semua Pesanan"):
                checkout.clear()
                save_json(CHECKOUT_FILE, checkout)
                st.success("✅ Semua pesanan dibersihkan")
                st.rerun()

    # ---- Pembayaran ----
    elif menu == "Pembayaran":
        st.header("💳 Pembayaran")
        if not checkout:
            st.info("Belum ada transaksi")
        else:
            df = pd.DataFrame(checkout)
            df["subtotal"] = df["harga"] * df["jumlah"]
            df_display = df[["nama","jumlah","harga","subtotal"]]
            df_display = df_display.rename(columns={"nama":"Nama","jumlah":"Jml","harga":"Harga","subtotal":"Subtotal"})
            df_display["Harga"] = df_display["Harga"].apply(lambda x: f"{x:,}".replace(",", "."))
            df_display["Subtotal"] = df_display["Subtotal"].apply(lambda x: f"{x:,}".replace(",", "."))
            st.table(df_display)

            buyer_name = checkout[0].get("buyer","Umum")
            st.markdown(f"**Nama Pembeli:** {buyer_name}")

            total_item = sum(i["jumlah"] for i in checkout)
            subtotal = sum(i["harga"]*i["jumlah"] for i in checkout)
            ppn_amount = int(subtotal*config.get("ppn",11)/100)
            diskon_amount = int(subtotal*config.get("diskon",0)/100)
            total_final = subtotal + ppn_amount - diskon_amount

            tunai = st.number_input("Tunai (Rp)", min_value=0, value=total_final)
            kembalian = tunai - total_final

            st.markdown(f"**Kembalian:** Rp {kembalian:,}".replace(",", "."))

            # ---------- Cetak Struk ----------
            def lr_align(left, right, width=32):
                left_s = str(left)
                right_s = str(right)
                space = width - len(left_s) - len(right_s)
                if space < 1:
                    space = 1
                return left_s + " "*space + right_s

            def build_struk():
                tz = pytz.timezone("Asia/Jakarta")
                now = datetime.now(tz)
                config["counter"] +=1
                save_json(CONFIG_FILE, config)
                kode = f"RG-{now.strftime('%Y%m%d')}-{config['counter']:05d}"
                lines = []
                lines.append(config.get("shop_name","").center(32))
                lines.append(config.get("address","").center(32))
                lines.append("-"*32)
                lines.append(f"No. Transaksi: {kode}")
                lines.append(f"Kasir: {config.get('cashier','')}")
                lines.append(f"Tgl: {now.strftime('%d-%m-%Y %H:%M:%S')} WIB")
                lines.append("-"*32)
                for d in checkout:
                    name = d["nama"][:16]
                    qty = d["jumlah"]
                    price = d["harga"]
                    subtotal_item = qty*price
                    lines.append(f"{name:<16}{qty:>2} x {price:,} {subtotal_item:>7,}".replace(",","."))
                lines.append("-"*32)
                lines.append(lr_align("Total Item", total_item))
                lines.append(lr_align("Subtotal", f"Rp {subtotal:,}".replace(",", ".")))
                lines.append(lr_align(f"PPN ({config.get('ppn',0)}%)", f"Rp {ppn_amount:,}".replace(",", ".")))
                lines.append(lr_align(f"Diskon ({config.get('diskon',0)}%)", f"-Rp {diskon_amount:,}".replace(",", ".")))
                lines.append(lr_align("Total", f"Rp {total_final:,}".replace(",", ".")))
                lines.append(lr_align("Tunai", f"Rp {tunai:,}".replace(",", ".")))
                lines.append(lr_align("Kembalian", f"Rp {kembalian:,}".replace(",", ".")))
                lines.append(lr_align(f"Pembeli", buyer_name))
                lines.append("-"*32)
                lines.append(config.get("footer","").center(32))
                return "\n".join(lines), kode

            if st.button("🖨️ Cetak Struk"):
                struk_text, kode = build_struk()
                st.text(struk_text)

                # generate barcode
                code128 = barcode.get('code128', kode, writer=ImageWriter())
                buf = BytesIO()
                code128.write(buf, options={"module_width":0.2,"module_height":15,"font_size":10})
                buf.seek(0)
                st.image(buf.getvalue(), width=230)

                # save sale
                sales.append({
                    "tanggal": datetime.now(pytz.timezone("Asia/Jakarta")).strftime("%Y-%m-%d"),
                    "total": total_final,
                    "kode": kode,
                    "cashier": config.get("cashier"),
                    "buyer": buyer_name,
                    "items": checkout.copy()
                })
                save_json(SALES_FILE, sales)
                checkout.clear()
                save_json(CHECKOUT_FILE, checkout)
                st.success("✅ Transaksi selesai dan struk dicetak.")

    # ---- Laporan ----
    elif menu == "Laporan":
        st.subheader("📊 Laporan Harian")
        if not sales:
            st.info("Belum ada transaksi.")
        else:
            df = pd.DataFrame(sales)
            df["Tanggal"] = pd.to_datetime(df["tanggal"]).dt.strftime("%d/%m/%Y")
            df["Pemasukan"] = df["total"].apply(lambda x: f"Rp {x:,}".replace(",", "."))
            cols = ["Tanggal","Pemasukan","kode","cashier","buyer"]
            st.table(df[cols])
            st.write(f"### 💰 Total: Rp {sum(s['total'] for s in sales):,}".replace(",", "."))

            pilih_kode = st.selectbox("Pilih kode transaksi yang mau dihapus", [s.get("kode") for s in sales])
            if st.button("Hapus Transaksi"):
                sales[:] = [s for s in sales if s.get("kode") != pilih_kode]
                save_json(SALES_FILE, sales)
                st.success(f"✅ Transaksi {pilih_kode} dihapus")
                st.rerun()

# ---------------- routing ----------------
def logout():
    st.session_state.role = None
    st.rerun()

if st.session_state.role == "admin":
    st.sidebar.button("Logout", on_click=logout)
    admin_page()
elif st.session_state.role == "user":
    st.sidebar.button("Logout", on_click=logout)
    user_page()
else:
    login_page()
