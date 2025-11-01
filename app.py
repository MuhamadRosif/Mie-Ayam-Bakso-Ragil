# app.py - FINAL (Alfamart-style struk, WIB, editable settings in sidebar)
import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime
import pytz
from io import BytesIO

# Optional libs (barcode + qrcode)
try:
    import barcode
    from barcode.writer import ImageWriter
    HAS_BARCODE = True
except Exception:
    HAS_BARCODE = False

try:
    import qrcode
    HAS_QR = True
except Exception:
    HAS_QR = False

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

def rupiah_int(n):
    try:
        return f"Rp {int(n):,}".replace(",", ".")
    except:
        return f"Rp {n}"

# ---------------- defaults ----------------
menu_data = load_json(MENU_FILE, {
    "makanan": {"Mie Ayam": 15000, "Bakso": 18000},
    "minuman": {"Es Teh": 5000}
})
checkout = load_json(CHECKOUT_FILE, [])
sales = load_json(SALES_FILE, [])
config = load_json(CONFIG_FILE, {
    "shop_name": "PT. SUMBER ALFARIA TRIJAYA, TBK",
    "branch": "MELIA WALK",
    "address": "JL.MH. THAMRIN NO.9.CIKOKOL, TANGERANG",
    "npwp": "01.336.238.9-054.000",
    "cashier_default": "ROOFID S",
    "footer": "Selalu segar bangsat",
    "ppn_percent": 11,
    "discount_percent": 0,
    "counter": 0
})

# ensure old sales entries compat
for s in sales:
    s.setdefault("kode", "-")
    s.setdefault("cashier", config.get("cashier_default", "ADMIN"))
    s.setdefault("buyer", "Umum")
    s.setdefault("items", [])

# ---------------- UI setup ----------------
st.set_page_config(page_title="Mie Ayam Mas Ragil", page_icon="🍜", layout="centered")
st.markdown("<style>body{background:#faf6f0;} footer{visibility:hidden;}</style>", unsafe_allow_html=True)

# session defaults
if "role" not in st.session_state:
    st.session_state.role = None
if "buyer_name" not in st.session_state:
    st.session_state.buyer_name = ""

# ---------------- small layout utils (32-char thermal) ----------------
def center32(s):
    s = str(s)
    return s if len(s) >= 32 else s.center(32)

def lr32(left, right):
    left_s = str(left)
    right_s = str(right)
    space = 32 - len(left_s) - len(right_s)
    if space < 1:
        # trim left if too long
        left_s = left_s[:32 - len(right_s) - 1]
        space = 1
    return left_s + (" " * space) + right_s

# ---------------- pages ----------------
def login_page():
    st.title("🍜 Mie Ayam & Bakso Ragil")
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

def user_page():
    st.title("🍜 Menu Pesanan")
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
        df["total"] = df["total"].apply(lambda x: f"Rp {int(x):,}".replace(",", "."))
        st.table(df)
        if st.button("Hapus Semua Keranjang"):
            checkout.clear(); save_json(CHECKOUT_FILE, checkout); st.success("✅ Keranjang dikosongkan")
    else:
        st.info("Keranjang kosong")

def admin_page():
    st.title("⚙️ Admin Panel")
    st.sidebar.header("📂 Panel Admin")
    menu = st.sidebar.radio("Pilih", ["Pengaturan Toko", "Data Menu", "Data Pesanan", "Pembayaran", "Laporan"])

    # ---------- Pengaturan Toko ----------
    if menu == "Pengaturan Toko":
        st.header("🛠 Pengaturan Toko")
        shop = st.text_input("Nama Perusahaan", config.get("shop_name", ""))
        branch = st.text_input("Cabang", config.get("branch", ""))
        addr = st.text_input("Alamat", config.get("address", ""))
        npwp = st.text_input("NPWP", config.get("npwp", ""))
        cashier = st.text_input("Nama Kasir Default", config.get("cashier_default", ""))
        footer = st.text_input("Footer Struk", config.get("footer", ""))
        ppn = st.number_input("PPN (%)", min_value=0, max_value=100, value=int(config.get("ppn_percent", 0)))
        default_disc = st.number_input("Diskon Default (%)", min_value=0, max_value=100, value=int(config.get("discount_percent", 0)))

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Simpan Pengaturan"):
                config["shop_name"] = shop.strip()
                config["branch"] = branch.strip()
                config["address"] = addr.strip()
                config["npwp"] = npwp.strip()
                config["cashier_default"] = cashier.strip()
                config["footer"] = footer
                config["ppn_percent"] = int(ppn)
                config["discount_percent"] = int(default_disc)
                save_json(CONFIG_FILE, config)
                st.success("✅ Pengaturan disimpan")
                st.rerun()
        with col2:
            if st.button("Reset Counter"):
                config["counter"] = 0; save_json(CONFIG_FILE, config); st.success("✅ Counter direset")

    # ---------- Data Menu ----------
    elif menu == "Data Menu":
        st.header("📋 Data Menu")
        rows = []
        for k, items in menu_data.items():
            for name, price in items.items():
                rows.append({"Kategori": k, "Nama": name, "Harga": rupiah_int(price)})
        st.table(pd.DataFrame(rows))

        st.subheader("➕ Tambah / Edit Menu")
        kat = st.selectbox("Kategori", list(menu_data.keys()))
        nama = st.text_input("Nama Menu")
        harga = st.number_input("Harga (Rp)", min_value=0)
        if st.button("Simpan Menu"):
            if nama.strip() == "":
                st.error("Nama menu kosong")
            else:
                menu_data[kat][nama] = int(harga)
                save_json(MENU_FILE, menu_data)
                st.success("✅ Menu disimpan"); st.experimental_rerun()

        st.subheader("🗑 Hapus Menu")
        del_kat = st.selectbox("Pilih Kategori (Hapus)", list(menu_data.keys()))
        del_item = st.selectbox("Pilih Menu (Hapus)", list(menu_data[del_kat].keys()))
        if st.button("Hapus Menu"):
            del menu_data[del_kat][del_item]; save_json(MENU_FILE, menu_data); st.success("✅ Menu dihapus"); st.experimental_rerun()

    # ---------- Data Pesanan ----------
    elif menu == "Data Pesanan":
        st.header("📝 Pesanan Masuk")
        if not checkout:
            st.info("Belum ada pesanan")
        else:
            df = pd.DataFrame(checkout)
            df["total"] = df["harga"] * df["jumlah"]
            df["total"] = df["total"].apply(lambda x: f"Rp {int(x):,}".replace(",", "."))
            st.table(df)
            if st.button("Hapus Semua Pesanan"):
                checkout.clear(); save_json(CHECKOUT_FILE, checkout); st.success("✅ Semua pesanan dihapus"); st.experimental_rerun()

    # ---------- Pembayaran ----------
    elif menu == "Pembayaran":
        st.header("💳 Pembayaran")
        if not checkout:
            st.info("Belum ada transaksi")
        else:
            df = pd.DataFrame(checkout)
            df["subtotal"] = df["harga"] * df["jumlah"]
            df["subtotal"] = df["subtotal"].apply(lambda x: f"Rp {int(x):,}".replace(",", "."))
            st.table(df)

            buyer_name = checkout[0].get("buyer", "Umum")
            st.markdown(f"**Pembeli:** {buyer_name}")

            subtotal = sum(i["harga"] * i["jumlah"] for i in checkout)

            st.write("### Pengaturan Diskon & PPN")
            disc_mode = st.selectbox("Diskon sebagai", ["Tidak", "Rp", "%"], index=2 if config.get("discount_percent",0)>0 else 0)
            disc_amount = 0
            if disc_mode == "Rp":
                disc_amount = st.number_input("Diskon (Rp)", min_value=0, value=0)
            elif disc_mode == "%":
                disc_pct = st.number_input("Diskon (%)", min_value=0.0, max_value=100.0, value=float(config.get("discount_percent", 0.0)))
                disc_amount = int(round(subtotal * (disc_pct/100.0)))
            else:
                disc_amount = 0

            ppn_pct = st.number_input("PPN (%)", min_value=0, max_value=100, value=int(config.get("ppn_percent", 0)))
            taxable = max(0, subtotal - disc_amount)
            ppn = int(round(taxable * (ppn_pct / 100.0)))
            total = taxable + ppn

            st.write(f"Subtotal: {rupiah_int(subtotal)}")
            st.write(f"Diskon: {rupiah_int(disc_amount)}")
            st.write(f"PPN ({ppn_pct}%): {rupiah_int(ppn)}")
            st.write(f"Total Bayar: {rupiah_int(total)}")

            tunai = st.number_input("Tunai (Rp)", min_value=0, value=total)
            kembalian = tunai - total if tunai >= total else 0
            if tunai < total:
                st.warning("Tunai kurang!")
            else:
                st.success(f"Kembalian: {rupiah_int(kembalian)}")

            cashier_input = st.text_input("Nama Kasir", config.get("cashier_default", "ADMIN"))
            tz = pytz.timezone("Asia/Jakarta")
            now = datetime.now(tz)

            def build_struk(increment_counter=True):
                if increment_counter:
                    config["counter"] = config.get("counter", 0) + 1
                    save_json(CONFIG_FILE, config)
                counter = config.get("counter", 0)
                kode = f"RG-{now.strftime('%Y%m%d')}-{counter:05d}"

                lines = []
                lines.append(center32(config.get("shop_name", "")))
                if config.get("branch"):
                    lines.append(center32(config.get("branch", "")))
                lines.append(center32(config.get("address", "")))
                if config.get("npwp"):
                    lines.append(center32(f"NPWP: {config.get('npwp')}"))
                lines.append("-" * 32)
                lines.append(f"No. Transaksi: {kode}")
                lines.append(f"Kasir: {cashier_input}")
                lines.append(f"Tgl: {now.strftime('%d-%m-%Y')}  {now.strftime('%H:%M:%S')} WIB")
                lines.append("-" * 32)

                total_items = 0
                for d in checkout:
                    name = d["nama"][:32]
                    qty = d["jumlah"]
                    price = d["harga"]
                    subtotal_item = qty * price
                    lines.append(name)
                    lines.append(lr32(f"{qty} x Rp {price:,}".replace(",", "."), f"Rp {subtotal_item:,}".replace(",", ".")))
                    total_items += qty

                lines.append("-" * 32)
                lines.append(lr32("Total Item", str(total_items)))
                lines.append(lr32("Subtotal", f"Rp {subtotal:,}".replace(",", ".")))
                lines.append(lr32("Diskon", f"Rp {disc_amount:,}".replace(",", ".")))
                lines.append(lr32(f"PPN ({ppn_pct}%)", f"Rp {ppn:,}".replace(",", ".")))
                lines.append(lr32("Total Bayar", f"Rp {total:,}".replace(",", ".")))
                lines.append(lr32("Tunai", f"Rp {tunai:,}".replace(",", ".")))
                lines.append(lr32("Kembalian", f"Rp {kembalian:,}".replace(",", ".")))
                lines.append("-" * 32)
                lines.append(f"Pembeli: {buyer_name}")
                lines.append("")
                lines.append(center32(config.get("footer", "")))
                lines.append(center32("Simpan struk ini sebagai bukti"))
                struk_text = "\n".join(lines)
                return struk_text, kode

            col1, col2 = st.columns(2)

            with col1:
                if st.button("🖨️ Cetak Struk (Tampil)"):
                    struk_text, kode = build_struk(increment_counter=True)

                    barcode_png = None
                    if HAS_BARCODE:
                        try:
                            code128 = barcode.get('code128', kode, writer=ImageWriter())
                            buf = BytesIO()
                            code128.write(buf, options={"module_width": 0.2, "module_height": 15, "font_size": 10})
                            buf.seek(0)
                            barcode_png = buf.getvalue()
                        except Exception as e:
                            st.warning(f"Gagal membuat barcode PNG: {e}")
                            barcode_png = None

                    # QR from transaction code (not static)
                    qr_png = None
                    if HAS_QR:
                        try:
                            qr_obj = qrcode.QRCode(box_size=3, border=1)
                            qr_obj.add_data(kode)
                            qr_obj.make(fit=True)
                            img_qr = qr_obj.make_image(fill_color="black", back_color="white")
                            buf_qr = BytesIO(); img_qr.save(buf_qr, format="PNG"); buf_qr.seek(0); qr_png = buf_qr.getvalue()
                        except Exception:
                            qr_png = None

                    st.text(struk_text)
                    if barcode_png:
                        st.image(barcode_png, width=240)
                    else:
                        st.info(f"Kode transaksi: {kode}")

                    if qr_png:
                        st.image(qr_png, width=120)

                    sales.append({
                        "tanggal": now.strftime("%Y-%m-%d"),
                        "total": total,
                        "kode": kode,
                        "cashier": cashier_input,
                        "buyer": buyer_name,
                        "items": checkout.copy()
                    })
                    save_json(SALES_FILE, sales)

                    checkout.clear()
                    save_json(CHECKOUT_FILE, checkout)
                    st.success("✅ Transaksi disimpan. Struk tampil — tekan Ctrl+P untuk cetak.")

            with col2:
                if st.button("⬇️ Download Struk (.txt) & Barcode"):
                    struk_text, kode = build_struk(increment_counter=True)

                    barcode_png = None
                    if HAS_BARCODE:
                        try:
                            code128 = barcode.get('code128', kode, writer=ImageWriter())
                            buf = BytesIO()
                            code128.write(buf, options={"module_width": 0.2, "module_height": 15, "font_size": 10})
                            buf.seek(0)
                            barcode_png = buf.getvalue()
                        except Exception as e:
                            st.warning(f"Gagal membuat barcode PNG: {e}")
                            barcode_png = None

                    qr_png = None
                    if HAS_QR:
                        try:
                            qr_obj = qrcode.QRCode(box_size=3, border=1)
                            qr_obj.add_data(kode)
                            qr_obj.make(fit=True)
                            img_qr = qr_obj.make_image(fill_color="black", back_color="white")
                            buf_qr = BytesIO(); img_qr.save(buf_qr, format="PNG"); buf_qr.seek(0); qr_png = buf_qr.getvalue()
                        except Exception:
                            qr_png = None

                    st.download_button("Download: Struk TXT", data=struk_text.encode("utf-8"), file_name=f"struk_{kode}.txt", mime="text/plain")
                    if barcode_png:
                        st.download_button("Download: Barcode PNG", data=barcode_png, file_name=f"barcode_{kode}.png", mime="image/png")
                    if qr_png:
                        st.download_button("Download: QR PNG", data=qr_png, file_name=f"qr_{kode}.png", mime="image/png")

                    sales.append({
                        "tanggal": now.strftime("%Y-%m-%d"),
                        "total": total,
                        "kode": kode,
                        "cashier": cashier_input,
                        "buyer": buyer_name,
                        "items": checkout.copy()
                    })
                    save_json(SALES_FILE, sales)

                    checkout.clear()
                    save_json(CHECKOUT_FILE, checkout)
                    st.success("✅ File disediakan untuk di-download. Transaksi tersimpan & checkout dikosongkan.")

    # ---------- Laporan ----------
    elif menu == "Laporan":
        st.header("📊 Laporan Penjualan")
        if not sales:
            st.info("Belum ada transaksi")
        else:
            df = pd.DataFrame(sales)
            df["Tanggal"] = pd.to_datetime(df["tanggal"]).dt.strftime("%d/%m/%Y")
            df["Pemasukan"] = df["total"].apply(lambda x: f"Rp {int(x):,}".replace(",", "."))
            cols = ["Tanggal", "Pemasukan", "kode", "cashier", "buyer"]
            st.table(df[cols])
            st.write(f"### 💰 Total: {rupiah_int(sum(s['total'] for s in sales))}")

            kode_hapus = st.selectbox("Pilih kode untuk hapus", [s.get("kode") for s in sales])
            if st.button("Hapus Transaksi"):
                sales[:] = [s for s in sales if s.get("kode") != kode_hapus]
                save_json(SALES_FILE, sales)
                st.success("✅ Transaksi dihapus"); st.experimental_rerun()

# ---------------- routing ----------------
if st.session_state.role == "admin":
    st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"role": None}))
    admin_page()
elif st.session_state.role == "user":
    st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"role": None}))
    user_page()
else:
    login_page()
