# app.py - FINAL (Alfamart-style struk, PPN, Diskon, pengaturan toko, Barcode 128)
import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime
import pytz
from io import BytesIO

# optional barcode lib
try:
    import barcode
    from barcode.writer import ImageWriter
    HAS_BARCODE = True
except Exception:
    HAS_BARCODE = False

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

def rupiah(n):
    # format integer to "12.345"
    try:
        return f"Rp {int(n):,}".replace(",", ".")
    except Exception:
        return f"Rp {n}"

# ---------------- initial data ----------------
menu_data = load_json(MENU_FILE, {"makanan": {"Mie Ayam": 15000, "Bakso": 18000}, "minuman": {"Es Teh": 5000}})
checkout = load_json(CHECKOUT_FILE, [])
sales = load_json(SALES_FILE, [])
config = load_json(CONFIG_FILE, {
    "shop_name": "MIE AYAM MAS RAGIL",
    "address": "Jl. Rasa Bahagia No.1",
    "npwp": "",
    "cashier": "ADMIN RAGIL",
    "footer": "Selalu segar bangsat",
    "counter": 0
})

# back-compat sales entries
for s in sales:
    s.setdefault("kode", "-")
    s.setdefault("cashier", config.get("cashier", "ADMIN RAGIL"))
    s.setdefault("buyer", "Umum")
    s.setdefault("items", [])

# ---------------- UI setup ----------------
st.set_page_config(page_title=config.get("shop_name", "Mie Ayam"), page_icon="🍜", layout="centered")
st.markdown("""<style>body{background:#faf6f0;} footer{visibility:hidden;}</style>""", unsafe_allow_html=True)

# session defaults
if "role" not in st.session_state:
    st.session_state.role = None
if "buyer_name" not in st.session_state:
    st.session_state.buyer_name = ""

# ---------------- small util for thermal 32-char layout ----------------
def center32(text):
    s = str(text)
    if len(s) >= 32:
        return s[:32]
    return s.center(32)

def lr32(left, right):
    left_s = str(left)
    right_s = str(right)
    space = 32 - len(left_s) - len(right_s)
    if space < 1:
        # trim left to fit
        left_s = left_s[:32 - len(right_s) - 1]
        space = 1
    return left_s + " " * space + right_s

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
    st.title("🍜 Menu Pesanan")
    st.subheader("👤 Nama Pembeli (opsional)")
    st.session_state.buyer_name = st.text_input("Nama Pembeli", value=st.session_state.buyer_name)

    kategori = st.selectbox("Kategori", list(menu_data.keys()))
    item = st.selectbox("Menu", list(menu_data[kategori].keys()))
    qty = st.number_input("Jumlah", min_value=1, value=1)

    if st.button("Tambah"):
        buyer = st.session_state.buyer_name or "Umum"
        checkout.append({
            "nama": item,
            "harga": menu_data[kategori][item],
            "jumlah": qty,
            "buyer": buyer
        })
        save_json(CHECKOUT_FILE, checkout)
        st.success("✅ Ditambahkan ke keranjang")

    st.subheader("🧾 Keranjang")
    if checkout:
        df = pd.DataFrame(checkout)
        df["Total"] = df["harga"] * df["jumlah"]
        df["Total"] = df["Total"].apply(lambda x: f"Rp {x:,}".replace(",", "."))
        st.table(df)
        if st.button("Bersihkan Keranjang"):
            checkout.clear(); save_json(CHECKOUT_FILE, checkout); st.success("✅ Keranjang dibersihkan")
    else:
        st.info("Belum ada pesanan")

# ---------------- Admin page ----------------
def admin_page():
    st.title("⚙️ Admin Panel")
    st.subheader("🔧 Pengaturan Toko")
    shop = st.text_input("Nama Toko", value=config.get("shop_name"))
    addr = st.text_input("Alamat", value=config.get("address"))
    npwp = st.text_input("NPWP", value=config.get("npwp"))
    cashier = st.text_input("Nama Kasir Default", value=config.get("cashier"))
    footer = st.text_input("Footer Struk", value=config.get("footer"))

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Simpan Pengaturan"):
            config["shop_name"] = shop.strip() or config.get("shop_name")
            config["address"] = addr.strip() or config.get("address")
            config["npwp"] = npwp.strip()
            config["cashier"] = cashier.strip() or config.get("cashier")
            config["footer"] = footer
            save_json(CONFIG_FILE, config)
            st.success("✅ Pengaturan disimpan")
            st.rerun()
    with col2:
        if st.button("Reset Counter"):
            config["counter"] = 0; save_json(CONFIG_FILE, config); st.success("✅ Counter direset")

    menu = st.sidebar.radio("Menu Admin", ["Data Menu", "Data Pesanan", "Pembayaran", "Laporan"])

    # Data Menu
    if menu == "Data Menu":
        st.subheader("📋 Daftar Menu")
        rows = []
        for k, items in menu_data.items():
            for n, h in items.items():
                rows.append({"Kategori": k, "Nama": n, "Harga": rupiah(h)})
        st.table(pd.DataFrame(rows))

        st.subheader("➕ Tambah / Edit Menu")
        kat = st.selectbox("Kategori", list(menu_data.keys()))
        nama = st.text_input("Nama Menu")
        harga = st.number_input("Harga (Rp)", min_value=0)
        if st.button("Simpan Menu"):
            if nama.strip() == "":
                st.error("Nama menu tidak boleh kosong")
            else:
                menu_data[kat][nama] = harga
                save_json(MENU_FILE, menu_data)
                st.success("✅ Menu disimpan"); st.rerun()

        st.subheader("🗑️ Hapus Menu")
        del_kat = st.selectbox("Pilih Kategori (Hapus)", list(menu_data.keys()))
        del_item = st.selectbox("Pilih Menu (Hapus)", list(menu_data[del_kat].keys()))
        if st.button("Hapus Menu"):
            del menu_data[del_kat][del_item]
            save_json(MENU_FILE, menu_data)
            st.success("✅ Menu dihapus"); st.rerun()

    # Data Pesanan
    elif menu == "Data Pesanan":
        st.subheader("📝 Pesanan Masuk")
        if not checkout:
            st.info("Belum ada pesanan.")
        else:
            df = pd.DataFrame(checkout)
            df["Total"] = df["harga"] * df["jumlah"]
            df["Total"] = df["Total"].apply(lambda x: f"Rp {x:,}".replace(",", "."))
            st.table(df)
            if st.button("Hapus Semua Pesanan"):
                checkout.clear(); save_json(CHECKOUT_FILE, checkout); st.success("✅ Semua pesanan dibersihkan"); st.rerun()

    # Pembayaran
    elif menu == "Pembayaran":
        st.subheader("💳 Pembayaran")
        if not checkout:
            st.info("Belum ada transaksi.")
            return

        df = pd.DataFrame(checkout)
        df["subtotal"] = df["harga"] * df["jumlah"]
        df["subtotal"] = df["subtotal"].apply(lambda x: f"Rp {x:,}".replace(",", "."))
        st.table(df)

        buyer_name = checkout[0].get("buyer", "Umum")
        st.markdown(f"**Pembeli**: {buyer_name}")

        subtotal = sum(i["harga"] * i["jumlah"] for i in checkout)

        # Diskon input
        disc_type = st.selectbox("Tipe Diskon", ["Rp", "%"])
        if disc_type == "Rp":
            disc_val = st.number_input("Diskon (Rp)", min_value=0, value=0)
            disc_amount = int(disc_val)
        else:
            disc_pct = st.number_input("Diskon (%)", min_value=0.0, max_value=100.0, value=0.0, format="%.2f")
            disc_amount = int(round(subtotal * (float(disc_pct) / 100.0)))

        # PPN 11%
        taxable = max(0, subtotal - disc_amount)
        ppn = int(round(taxable * 0.11))

        total = taxable + ppn

        st.write(f"Subtotal: {rupiah(subtotal)}")
        st.write(f"Diskon: {rupiah(disc_amount)}")
        st.write(f"PPN (11%): {rupiah(ppn)}")
        st.write(f"Total Bayar: {rupiah(total)}")

        # pembayaran
        tunai = st.number_input("Tunai (Rp)", min_value=0, value=total)
        kembalian = tunai - total if tunai >= total else 0
        if tunai < total:
            st.warning("Tunai kurang!")
        else:
            st.success(f"Kembalian: {rupiah(kembalian)}")

        cashier_input = st.text_input("Nama Kasir", config.get("cashier", "ADMIN RAGIL"))

        # WIB time
        tz = pytz.timezone("Asia/Jakarta")
        now = datetime.now(tz)

        # build struk
        def build_struk(increment_counter=True):
            if increment_counter:
                config["counter"] = config.get("counter", 0) + 1
                save_json(CONFIG_FILE, config)
            counter = config.get("counter", 0)
            kode = f"RG-{now.strftime('%Y%m%d')}-{counter:05d}"

            lines = []
            lines.append(center32(config.get("shop_name", "MIE AYAM MAS RAGIL")))
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
            lines.append(lr32("PPN (11%)", f"Rp {ppn:,}".replace(",", ".")))
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

        # buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🖨️ Cetak Struk (Tampil)"):
                struk_text, kode = build_struk(increment_counter=True)

                # generate barcode if available
                barcode_png = None
                if HAS_BARCODE:
                    try:
                        code128 = barcode.get('code128', kode, writer=ImageWriter())
                        buf = BytesIO()
                        code128.write(buf, options={"module_width": 0.2, "module_height": 15, "font_size": 10})
                        buf.seek(0)
                        barcode_png = buf.getvalue()
                    except Exception as e:
                        st.warning(f"Gagal membuat gambar barcode: {e}")
                        barcode_png = None

                st.text(struk_text)
                if barcode_png:
                    st.image(barcode_png, width=240)
                else:
                    st.info(f"Kode transaksi: {kode} (gambar barcode tidak tersedia)")

                # save sale
                sales.append({
                    "tanggal": now.strftime("%Y-%m-%d"),
                    "total": total,
                    "kode": kode,
                    "cashier": cashier_input,
                    "buyer": buyer_name,
                    "items": checkout.copy()
                })
                save_json(SALES_FILE, sales)

                # clear
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
                        st.warning(f"Gagal membuat gambar barcode: {e}")
                        barcode_png = None
                else:
                    st.info("python-barcode belum terpasang — hanya struk TXT yang tersedia")

                st.download_button("Download: Struk TXT", data=struk_text.encode("utf-8"), file_name=f"struk_{kode}.txt", mime="text/plain")
                if barcode_png:
                    st.download_button("Download: Barcode PNG", data=barcode_png, file_name=f"barcode_{kode}.png", mime="image/png")

                # finalize
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

                st.success("✅ File disediakan untuk di-download. Transaksi disimpan & checkout dikosongkan.")

    # Laporan
    elif menu == "Laporan":
        st.subheader("📊 Laporan Harian")
        if not sales:
            st.info("Belum ada transaksi.")
        else:
            df = pd.DataFrame(sales)
            df["Tanggal"] = pd.to_datetime(df["tanggal"]).dt.strftime("%d/%m/%Y")
            df["Pemasukan"] = df["total"].apply(lambda x: f"Rp {x:,}".replace(",", "."))
            cols = ["Tanggal", "Pemasukan"]
            for c in ["kode", "cashier", "buyer"]:
                if c in df.columns:
                    cols.append(c)
            st.table(df[cols])
            total_all = sum(s["total"] for s in sales)
            st.write(f"### 💰 Total: Rp {total_all:,}".replace(",", "."))

            st.subheader("🗑️ Hapus Transaksi")
            pilih_kode = st.selectbox("Pilih kode transaksi yang mau dihapus", [s.get("kode", f"no-{i}") for i, s in enumerate(sales)])
            if st.button("Hapus Transaksi"):
                sales[:] = [s for s in sales if s.get("kode") != pilih_kode]
                save_json(SALES_FILE, sales)
                st.success(f"✅ Transaksi {pilih_kode} dihapus")
                st.rerun()

# ---------------- routing ----------------
if st.session_state.role == "admin":
    st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"role": None}))
    admin_page()
elif st.session_state.role == "user":
    st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"role": None}))
    user_page()
else:
    login_page()
