# app.py - FINAL (User/Admin, Pengaturan Toko, Struk ala Alfamart)
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
    "footer": "Terima kasih telah berbelanja"
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
if "selected_buyer" not in st.session_state:
    st.session_state.selected_buyer = ""

# ---------------- helpers ----------------
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

# ---------------- User page ----------------
def user_page():
    st.title("🍜 Menu & Pesanan")
    st.subheader("👤 Nama Pembeli (wajib diisi)")
    st.session_state.buyer_name = st.text_input("Nama Pembeli", value=st.session_state.buyer_name)

    st.subheader("📜 Menu")
    kategori = st.selectbox("Kategori", list(menu_data.keys()))
    item = st.selectbox("Menu", list(menu_data[kategori].keys()))
    qty = st.number_input("Jumlah", min_value=1, value=1)

    if st.button("Tambah ke Keranjang"):
        if not st.session_state.buyer_name.strip():
            st.error("⚠️ Nama pembeli wajib diisi sebelum memesan!")
        else:
            checkout.append({
                "nama": item,
                "harga": menu_data[kategori][item],
                "jumlah": qty,
                "buyer": st.session_state.buyer_name.strip()
            })
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

    # ---------------- Pengaturan Toko ----------------
    if menu == "Pengaturan Toko":
        st.subheader("🔧 Pengaturan Toko")
        shop_name = st.text_input("Nama Toko", value=config.get("shop_name"))
        address = st.text_input("Alamat Toko", value=config.get("address"))
        cashier = st.text_input("Nama Kasir Default", value=config.get("cashier"))
        ppn = st.number_input("PPN (%)", 0, 20, config.get("ppn", 0))
        diskon = st.number_input("Diskon (%)", 0, 50, config.get("diskon", 0))
        footer = st.text_input("Footer Struk", value=config.get("footer"))
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Simpan Pengaturan Toko"):
                config.update({
                    "shop_name": shop_name,
                    "address": address,
                    "cashier": cashier,
                    "ppn": ppn,
                    "diskon": diskon,
                    "footer": footer
                })
                save_json(CONFIG_FILE, config)
                st.success("✅ Pengaturan Toko disimpan")
        with col2:
            if st.button("Reset Counter"):
                config["counter"] = 0
                save_json(CONFIG_FILE, config)
                st.success("✅ Counter direset")

    # ---------------- Data Menu ----------------
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

    # ---------------- Data Pesanan ----------------
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

    # ---------------- Pembayaran ----------------
    elif menu == "Pembayaran":
        st.header("💳 Pembayaran")
        if not checkout:
            st.info("Belum ada transaksi.")
        else:
            # pilih buyer
            buyers = list({c["buyer"] for c in checkout})
            st.session_state.selected_buyer = st.selectbox("Pilih Nama Pembeli", buyers)
            items = [c for c in checkout if c["buyer"] == st.session_state.selected_buyer]
            df = pd.DataFrame(items)
            df["subtotal"] = df["harga"] * df["jumlah"]
            df_display = df[["nama", "jumlah", "harga", "subtotal"]]
            df_display["harga"] = df_display["harga"].apply(lambda x: f"Rp {x:,}".replace(",", "."))
            df_display["subtotal"] = df_display["subtotal"].apply(lambda x: f"Rp {x:,}".replace(",", "."))
            st.table(df_display)

            subtotal = sum(i["harga"]*i["jumlah"] for i in items)
            ppn_amt = int(subtotal * config.get("ppn", 0) / 100)
            diskon_amt = int(subtotal * config.get("diskon", 0) / 100)
            total_final = subtotal + ppn_amt - diskon_amt

            st.write(f"Subtotal: Rp {subtotal:,}".replace(",", "."))
            st.write(f"PPN ({config.get('ppn')}%): Rp {ppn_amt:,}".replace(",", "."))
            st.write(f"Diskon ({config.get('diskon')}%): -Rp {diskon_amt:,}".replace(",", "."))
            st.write(f"Total: Rp {total_final:,}".replace(",", "."))

            tunai = st.number_input("Tunai", min_value=0, value=total_final)
            kembalian = tunai - total_final
            st.write(f"Kembalian: Rp {kembalian:,}".replace(",", "."))

            if st.button("🖨️ Cetak Struk (Tampil)"):
                tz = pytz.timezone("Asia/Jakarta")
                now = datetime.now(tz)
                config["counter"] = config.get("counter",0) + 1
                kode = f"RG-{now.strftime('%Y%m%d')}-{config['counter']:05d}"
                save_json(CONFIG_FILE, config)

                lines = []
                lines.append(center32(config.get("shop_name")))
                lines.append(center32(config.get("address")))
                lines.append(center32(""))
                lines.append("-"*32)
                lines.append(f"No. Transaksi: {kode}")
                lines.append(f"Kasir: {config.get('cashier')}")
                lines.append(f"Tgl: {now.strftime('%d-%m-%Y %H:%M:%S')} WIB")
                lines.append("-"*32)
                total_items = 0
                for d in items:
                    name = d["nama"][:32]
                    qty = d["jumlah"]
                    price = d["harga"]
                    subtotal_item = qty * price
                    lines.append(name)
                    lines.append(lr32(f"{qty} x Rp {price:,}".replace(",", "."), f"Rp {subtotal_item:,}".replace(",", ".")))
                    total_items += qty
                lines.append("-"*32)
                lines.append(lr32("Total Item", str(total_items)))
                lines.append(lr32("Subtotal", f"Rp {subtotal:,}".replace(",", ".")))
                lines.append(lr32(f"PPN ({config.get('ppn')}%)", f"Rp {ppn_amt:,}".replace(",", ".")))
                lines.append(lr32(f"Diskon ({config.get('diskon')}%)", f"-Rp {diskon_amt:,}".replace(",", ".")))
                lines.append(lr32("Total", f"Rp {total_final:,}".replace(",", ".")))
                lines.append(lr32("Tunai", f"Rp {tunai:,}".replace(",", ".")))
                lines.append(lr32("Kembalian", f"Rp {kembalian:,}".replace(",", ".")))
                lines.append(f"Pembeli: {st.session_state.selected_buyer}")
                lines.append("")
                lines.append(center32(config.get("footer", "")))

                struk_text = "\n".join(lines)
                st.text(struk_text)

                # generate barcode
                code128 = barcode.get('code128', kode, writer=ImageWriter())
                buf_bar = BytesIO()
                code128.write(buf_bar, options={"module_width":0.2,"module_height":15,"font_size":10})
                buf_bar.seek(0)
                st.image(buf_bar, width=230)

                # save sale
                sales.append({
                    "tanggal": now.strftime("%Y-%m-%d"),
                    "total": total_final,
                    "kode": kode,
                    "cashier": config.get("cashier"),
                    "buyer": st.session_state.selected_buyer,
                    "items": items
                })
                save_json(SALES_FILE, sales)

                # remove items from checkout for this buyer
                checkout[:] = [c for c in checkout if c["buyer"] != st.session_state.selected_buyer]
                save_json(CHECKOUT_FILE, checkout)
                st.success("✅ Transaksi disimpan. Tekan Ctrl+P untuk cetak.")

    # ---------------- Laporan ----------------
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
st.sidebar.title("Menu")
if st.sidebar.button("Admin Login"):
    st.session_state.role = "admin"

if st.session_state.role == "admin":
    if st.sidebar.button("Logout Admin"):
        st.session_state.role = None
        st.rerun()
    admin_page()
else:
    user_page()
