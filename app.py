# app.py - FINAL FULL (User + Admin Sidebar + Login/Logout)
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

# ---------------- UI setup ----------------
st.set_page_config(page_title="Mie Ayam Mas Ragil", page_icon="🍜", layout="centered")
st.markdown("""<style>body{background:#faf6f0;} footer{visibility:hidden;}</style>""", unsafe_allow_html=True)

# ---------------- session defaults ----------------
if "admin_logged" not in st.session_state:
    st.session_state.admin_logged = False
if "buyer_name" not in st.session_state:
    st.session_state.buyer_name = ""

# ---------------- user page ----------------
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
            st.error("⚠️ Silakan isi nama pembeli sebelum memesan!")
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

# ---------------- admin page ----------------
def admin_page():
    st.title("⚙️ Admin Panel")
    menu = st.sidebar.radio("Menu Admin", ["Data Menu", "Data Pesanan", "Pembayaran", "Laporan", "Pengaturan Toko"])

    # ---------- Pengaturan Toko ----------
    if menu == "Pengaturan Toko":
        st.subheader("🔧 Pengaturan Toko")
        shop_name = st.text_input("Nama Toko", value=config.get("shop_name"))
        address = st.text_input("Alamat Toko", value=config.get("address"))
        cashier_name = st.text_input("Nama Kasir Default", value=config.get("cashier"))
        ppn = st.number_input("PPN (%)", 0, 20, value=config.get("ppn", 11))
        diskon = st.number_input("Diskon (%)", 0, 100, value=config.get("diskon", 0))
        footer = st.text_input("Footer Struk", value=config.get("footer", ""))

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Simpan Pengaturan Toko"):
                config.update({
                    "shop_name": shop_name.strip(),
                    "address": address.strip(),
                    "cashier": cashier_name.strip(),
                    "ppn": ppn,
                    "diskon": diskon,
                    "footer": footer.strip()
                })
                save_json(CONFIG_FILE, config)
                st.success("✅ Pengaturan disimpan")
                st.rerun()
        with col2:
            if st.button("Reset Counter"):
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
        else:
            buyers = list(set([c["buyer"] for c in checkout]))
            selected_buyer = st.selectbox("Pilih Pembeli yang akan membayar", buyers)
            buyer_items = [c for c in checkout if c["buyer"] == selected_buyer]

            df = pd.DataFrame(buyer_items)
            df["subtotal"] = df["harga"] * df["jumlah"]
            df_display = df[["nama", "jumlah", "harga", "subtotal"]].copy()
            df_display["harga"] = df_display["harga"].apply(lambda x: f"Rp {x:,}".replace(",", "."))
            df_display["subtotal"] = df_display["subtotal"].apply(lambda x: f"Rp {x:,}".replace(",", "."))
            st.table(df_display)

            subtotal = sum(c["harga"] * c["jumlah"] for c in buyer_items)
            ppn_amt = int(subtotal * config["ppn"] / 100)
            diskon_amt = int(subtotal * config["diskon"] / 100)
            total_final = subtotal + ppn_amt - diskon_amt

            tunai = st.number_input("Tunai", min_value=0, value=total_final)
            kembalian = tunai - total_final

            st.write(f"Subtotal: Rp {subtotal:,}".replace(",", "."))
            st.write(f"PPN ({config['ppn']}%): Rp {ppn_amt:,}".replace(",", "."))
            st.write(f"Diskon ({config['diskon']}%): -Rp {diskon_amt:,}".replace(",", "."))
            st.write(f"Total: Rp {total_final:,}".replace(",", "."))
            st.write(f"Tunai: Rp {tunai:,}".replace(",", "."))
            st.write(f"Kembalian: Rp {kembalian:,}".replace(",", "."))
            st.write(f"Nama Pembeli: {selected_buyer}")

            if st.button("🖨️ Cetak Struk"):
                tz = pytz.timezone("Asia/Jakarta")
                now = datetime.now(tz)
                config["counter"] += 1
                save_json(CONFIG_FILE, config)
                kode = f"RG-{now.strftime('%Y%m%d')}-{config['counter']:05d}"

                def center32(txt):
                    return txt.center(32)
                def lr32(left, right):
                    space = 32 - len(left) - len(right)
                    if space < 0: space = 0
                    return left + " " * space + right

                lines = []
                lines.append(center32(config["shop_name"]))
                lines.append(center32(config["address"]))
                lines.append("-"*32)
                lines.append(f"No. Transaksi: {kode}")
                lines.append(f"Kasir: {config['cashier']}")
                lines.append(f"Tgl: {now.strftime('%d-%m-%Y %H:%M:%S')} WIB")
                lines.append("-"*32)
                total_items = 0
                for d in buyer_items:
                    lines.append(d["nama"])
                    lines.append(lr32(f"{d['jumlah']} x Rp {d['harga']:,}".replace(",", "."), f"Rp {d['jumlah']*d['harga']:,}".replace(",", ".")))
                    total_items += d["jumlah"]
                lines.append("-"*32)
                lines.append(lr32("Total Item", str(total_items)))
                lines.append(lr32("Subtotal", f"Rp {subtotal:,}".replace(",", ".")))
                lines.append(lr32(f"PPN ({config['ppn']}%)", f"Rp {ppn_amt:,}".replace(",", ".")))
                lines.append(lr32(f"Diskon ({config['diskon']}%)", f"-Rp {diskon_amt:,}".replace(",", ".")))
                lines.append(lr32("Total", f"Rp {total_final:,}".replace(",", ".")))
                lines.append(lr32("Tunai", f"Rp {tunai:,}".replace(",", ".")))
                lines.append(lr32("Kembalian", f"Rp {kembalian:,}".replace(",", ".")))
                lines.append(f"Pembeli: {selected_buyer}")
                lines.append(center32(config.get("footer","")))
                struk_text = "\n".join(lines)
                st.text(struk_text)

                # generate Code128 barcode
                CODE = kode
                code128 = barcode.get('code128', CODE, writer=ImageWriter())
                buf_bar = BytesIO()
                code128.write(buf_bar, options={"module_width": 0.2, "module_height": 15, "font_size": 10})
                buf_bar.seek(0)
                st.image(buf_bar, width=230)

                # save sale
                sales.append({
                    "tanggal": now.strftime("%Y-%m-%d"),
                    "total": total_final,
                    "kode": kode,
                    "cashier": config["cashier"],
                    "buyer": selected_buyer,
                    "items": buyer_items.copy()
                })
                save_json(SALES_FILE, sales)
                # remove items from checkout
                for c in buyer_items:
                    checkout.remove(c)
                save_json(CHECKOUT_FILE, checkout)
                st.success("✅ Struk tampil — tekan Ctrl+P untuk cetak")

# ---------------- routing ----------------
st.sidebar.title("Mie Ayam & Bakso Mas Ragil")

if st.session_state.admin_logged:
    st.sidebar.button("Logout Admin", on_click=lambda: st.session_state.update({"admin_logged": False}))
    admin_page()
else:
    if st.sidebar.button("Admin Login"):
        password = st.text_input("Masukkan Password Admin", type="password")
        if password == "123":  # ganti sesuai kebutuhan
            st.session_state.admin_logged = True
            st.rerun()
    user_page()
