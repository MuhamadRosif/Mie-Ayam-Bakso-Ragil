# app.py - FINAL RAPI
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
config = load_json(CONFIG_FILE, {"cashier": "ADMIN RAGIL", "counter": 0, "shop_name": "MIE AYAM MAS RAGIL", 
                                  "address": "Jl. Rasa Bahagia No.1", "ppn": 11, "diskon": 0, "footer": "Terima kasih"})

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
if "buyer_name" not in st.session_state:
    st.session_state.buyer_name = ""
if "selected_buyer" not in st.session_state:
    st.session_state.selected_buyer = ""

# ---------------- User Page ----------------
def user_page():
    st.title("🍜 Menu & Pesanan")
    st.session_state.buyer_name = st.text_input("👤 Nama Pembeli", value=st.session_state.buyer_name)
    
    if st.session_state.buyer_name.strip() == "":
        st.warning("Isi nama pembeli terlebih dahulu!")
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

# ---------------- Admin Page ----------------
def admin_page():
    st.title("⚙️ Admin Panel")
    menu = st.sidebar.radio("Menu Admin", ["Data Menu", "Data Pesanan", "Pembayaran", "Laporan", "Pengaturan Toko"])
    
    # ---------------- Pengaturan Toko ----------------
    if menu == "Pengaturan Toko":
        st.header("🛠️ Pengaturan Toko")
        shop_name = st.text_input("Nama Toko", value=config.get("shop_name", ""))
        address = st.text_input("Alamat Toko", value=config.get("address", ""))
        cashier = st.text_input("Nama Kasir", value=config.get("cashier", ""))
        ppn = st.number_input("PPN (%)", min_value=0, max_value=20, value=config.get("ppn", 11))
        diskon = st.number_input("Diskon (%)", min_value=0, max_value=100, value=config.get("diskon", 0))
        footer = st.text_input("Footer Struk", value=config.get("footer", ""))
        if st.button("Simpan Pengaturan"):
            config.update({"shop_name": shop_name, "address": address, "cashier": cashier, "ppn": ppn, "diskon": diskon, "footer": footer})
            save_json(CONFIG_FILE, config)
            st.success("✅ Pengaturan disimpan")
    
    # ---------------- Data Menu ----------------
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

    # ---------------- Pembayaran ----------------
    elif menu == "Pembayaran":
        st.header("💳 Pembayaran")
        if not checkout:
            st.info("Belum ada transaksi.")
            return

        buyers = list(set([c["buyer"] for c in checkout]))
        st.session_state.selected_buyer = st.selectbox("Pilih Pembeli", buyers)
        buyer_items = [i for i in checkout if i["buyer"] == st.session_state.selected_buyer]

        if not buyer_items:
            st.info("Tidak ada item untuk pembeli ini.")
            return

        df = pd.DataFrame(buyer_items)
        df["total"] = df["harga"] * df["jumlah"]
        df["total"] = df["total"].apply(lambda x: f"Rp {x:,}".replace(",", "."))
        st.table(df)

        subtotal = sum(i["harga"]*i["jumlah"] for i in buyer_items)
        ppn_amt = int(subtotal * config.get("ppn", 11)/100)
        diskon_amt = int(subtotal * config.get("diskon", 0)/100)
        total_final = subtotal + ppn_amt - diskon_amt

        tunai = st.number_input("Tunai (Rp)", min_value=0, value=total_final)
        kembalian = tunai - total_final if tunai >= total_final else 0

        def build_struk(items, buyer_name, tunai, kembalian):
            tz = pytz.timezone("Asia/Jakarta")
            now = datetime.now(tz)
            config["counter"] = config.get("counter",0)+1
            save_json(CONFIG_FILE, config)
            kode = f"RG-{now.strftime('%Y%m%d')}-{config['counter']:05d}"

            def center32(text):
                return str(text).center(32)

            def lr32(left, right, width=32):
                left_s = str(left)
                right_s = str(right)
                space = width - len(left_s) - len(right_s)
                if space < 1:
                    left_s = left_s[:width - len(right_s) - 1]
                    space = 1
                return left_s + " " * space + right_s

            subtotal = sum(i["harga"] * i["jumlah"] for i in items)
            ppn_amt = int(subtotal * config.get("ppn",11)/100)
            diskon_amt = int(subtotal * config.get("diskon",0)/100)
            total_final = subtotal + ppn_amt - diskon_amt

            lines = []
            lines.append(center32(config.get("shop_name")))
            lines.append(center32(config.get("address")))
            lines.append("-"*32)
            lines.append(lr32("No. Transaksi", kode))
            lines.append(lr32("Kasir", config.get("cashier")))
            lines.append(lr32("Tgl", now.strftime("%d-%m-%Y %H:%M:%S")+" WIB"))
            lines.append("-"*32)
            for d in items:
                name_line = d["nama"][:32]
                detail_line = f"{d['jumlah']} x Rp {d['harga']:,}".replace(",", ".")
                total_line = f"Rp {d['jumlah']*d['harga']:,}".replace(",", ".")
                lines.append(name_line)
                lines.append(lr32(detail_line,total_line))
            lines.append("-"*32)
            lines.append(lr32("Total Item", sum(i["jumlah"] for i in items)))
            lines.append(lr32("Subtotal", f"Rp {subtotal:,}".replace(",", ".")))
            lines.append(lr32(f"PPN ({config.get('ppn')}%)", f"Rp {ppn_amt:,}".replace(",", ".")))
            lines.append(lr32(f"Diskon ({config.get('diskon')}%)", f"-Rp {diskon_amt:,}".replace(",", ".")))
            lines.append(lr32("Total", f"Rp {total_final:,}".replace(",", ".")))
            lines.append(lr32("Tunai", f"Rp {tunai:,}".replace(",", ".")))
            lines.append(lr32("Kembalian", f"Rp {kembalian:,}".replace(",", ".")))
            lines.append(lr32("Pembeli", buyer_name))
            lines.append(center32(config.get("footer")))
            struk_text = "\n".join(lines)
            return struk_text, kode

        if st.button("🖨️ Cetak Struk (Tampil)"):
            struk_text, kode = build_struk(buyer_items, st.session_state.selected_buyer, tunai, kembalian)
            st.text(struk_text)
            sales.append({
                "tanggal": datetime.now(pytz.timezone("Asia/Jakarta")).strftime("%Y-%m-%d"),
                "total": total_final,
                "kode": kode,
                "cashier": config.get("cashier"),
                "buyer": st.session_state.selected_buyer,
                "items": buyer_items
            })
            save_json(SALES_FILE, sales)
            # hapus dari checkout
            checkout[:] = [c for c in checkout if c["buyer"] != st.session_state.selected_buyer]
            save_json(CHECKOUT_FILE, checkout)
            st.success("✅ Struk tampil — tekan Ctrl+P untuk cetak.")

# ---------------- Routing ----------------
if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.rerun()

user_page()
admin_page()
