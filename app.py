import streamlit as st
import json, os
import pandas as pd
from datetime import datetime
import pytz
from io import BytesIO
import qrcode
from PIL import Image

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

for s in sales:
    s.setdefault("kode", "-")
    s.setdefault("cashier", config.get("cashier", "ADMIN RAGIL"))
    s.setdefault("buyer", "Umum")
    s.setdefault("items", [])

# ---------------- UI setup ----------------
st.set_page_config(page_title="Mie Ayam Mas Ragil", page_icon="🍜", layout="wide")
st.markdown("""<style>body{background:#faf6f0;} footer{visibility:hidden;}</style>""", unsafe_allow_html=True)

# ---------------- session defaults ----------------
if "page" not in st.session_state:
    st.session_state.page = "user"
if "admin_logged" not in st.session_state:
    st.session_state.admin_logged = False
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
    return left_s + (" " * space) + right_s

# ---------------- Pages ----------------
def user_page():
    st.title("🍜 Menu & Pesanan")
    st.subheader("👤 Nama Pembeli (wajib diisi)")
    st.session_state.buyer_name = st.text_input("Nama Pembeli", value=st.session_state.buyer_name)

    disable_order = not st.session_state.buyer_name
    if disable_order:
        st.warning("Nama pembeli wajib diisi sebelum memesan")

    col_menu, col_cart = st.columns([2,1])
    with col_menu:
        st.subheader("📜 Menu")
        kategori = st.selectbox("Kategori", list(menu_data.keys()))
        item = st.selectbox("Menu", list(menu_data[kategori].keys()))
        qty = st.number_input("Jumlah", min_value=1, value=1)
        if st.button("Tambah ke Keranjang", disabled=disable_order):
            checkout.append({
                "nama": item,
                "harga": menu_data[kategori][item],
                "jumlah": qty,
                "buyer": st.session_state.buyer_name
            })
            save_json(CHECKOUT_FILE, checkout)
            st.success("✅ Ditambahkan ke keranjang")
            st.rerun()

    with col_cart:
        st.subheader("🧾 Keranjang Saat Ini")
        with st.expander("Lihat Keranjang"):
            if checkout:
                df = pd.DataFrame(checkout)
                df["total"] = df["harga"] * df["jumlah"]
                st.dataframe(df, use_container_width=True)
            else:
                st.info("Keranjang kosong")

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

    # Data Menu
    if menu == "Data Menu":
        st.header("📋 Data Menu")
        rows = []
        for k, items in menu_data.items():
            for n, h in items.items():
                rows.append({"Kategori": k, "Nama": n, "Harga": f"Rp {h:,}".replace(",", ".")})
        st.dataframe(pd.DataFrame(rows), use_container_width=True)

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

    # Data Pesanan
    elif menu == "Data Pesanan":
        st.header("📝 Pesanan Masuk")
        if not checkout:
            st.info("Belum ada pesanan.")
        else:
            st.dataframe(pd.DataFrame(checkout), use_container_width=True)
            if st.button("Hapus Semua Pesanan"):
                checkout.clear()
                save_json(CHECKOUT_FILE, checkout)
                st.success("✅ Semua pesanan dibersihkan")
                st.experimental_rerun()

    # Pembayaran
    elif menu == "Pembayaran":
        st.header("💳 Pembayaran")
        if not checkout:
            st.info("Belum ada transaksi")
            return

        buyers = list({c["buyer"] for c in checkout})
        selected_buyer = st.selectbox("Pilih Pembeli", buyers)
        buyer_checkout = [c for c in checkout if c["buyer"]==selected_buyer]
        st.dataframe(pd.DataFrame(buyer_checkout), use_container_width=True)

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
            lines.append(f"No. Transaksi  : {kode}")
            lines.append(f"Kasir          : {config.get('cashier')}")
            lines.append(f"Tanggal        : {now.strftime('%d-%m-%Y %H:%M:%S')} WIB")
            lines.append("-"*32)

            for i in buyer_checkout:
                name = i["nama"][:20]
                total_item = i["jumlah"] * i["harga"]
                lines.append(f"{name:<24}Rp {total_item:,}".replace(",", "."))
                lines.append(f"{i['jumlah']} pesanan")

            lines.append("-"*32)
            total_items = sum(i["jumlah"] for i in buyer_checkout)
            lines.append(lr32("Total Item", str(total_items)))
            lines.append(lr32("Subtotal", f"Rp {subtotal:,}".replace(",", ".")))
            lines.append(lr32(f"PPN ({config['ppn']}%)", f"Rp {ppn_amt:,}".replace(",", ".")))
            if config["diskon"]>0:
                lines.append(lr32(f"Diskon ({config['diskon']}%)", f"-Rp {diskon_amt:,}".replace(",", ".")))
            lines.append(lr32("Total", f"Rp {total_final:,}".replace(",", ".")))
            lines.append(lr32("Tunai", f"Rp {tunai:,}".replace(",", ".")))
            lines.append(lr32("Kembalian", f"Rp {kembalian:,}".replace(",", ".")))
            lines.append(f"Pembeli        : {selected_buyer}")
            lines.append("-"*32)
            lines.append(center32(config.get("footer")))
            lines.append("-"*32)

            st.text("\n".join(lines))

            qr = qrcode.QRCode(box_size=2, border=1)
            qr.add_data("Hikam - Dev")
            qr.make(fit=True)
            img_qr = qr.make_image(fill_color="black", back_color="white")
            buf = BytesIO()
            img_qr.save(buf, format="PNG")
            buf.seek(0)
            st.image(buf)

            sales.append({
                "tanggal": now.strftime("%Y-%m-%d"),
                "total": total_final,
                "kode": kode,
                "cashier": config.get("cashier"),
                "buyer": selected_buyer,
                "items": buyer_checkout
            })
            save_json(SALES_FILE, sales)

            checkout[:] = [c for c in checkout if c["buyer"]!=selected_buyer]
            save_json(CHECKOUT_FILE, checkout)

            # reset nama pembeli di user page
            st.session_state.buyer_name = ""

            st.success("✅ Struk dicetak, transaksi tersimpan")
            # reload user page jika bukan admin
            if not st.session_state.admin_logged:
                st.rerun()

# ---------------- Laporan Harian ----------------
    elif menu == "Laporan":
        st.header("📊 Laporan Harian")
        if not sales:
            st.info("Belum ada transaksi.")
        else:
            df = pd.DataFrame(sales)
            df["Tanggal"] = pd.to_datetime(df["tanggal"]).dt.strftime("%d/%m/%Y")
            df["Pemasukan"] = df["total"].apply(lambda x: f"Rp {x:,}".replace(",", "."))
            cols = ["Tanggal","Pemasukan","kode","cashier","buyer"]
            st.dataframe(df[cols], use_container_width=True)
            total_all = sum(s["total"] for s in sales)
            st.write(f"### 💰 Total: Rp {total_all:,}".replace(",", "."))

            pilih_kode = st.selectbox("Pilih kode transaksi yang mau dihapus", [s.get("kode") for s in sales])
            if st.button("Hapus Transaksi"):
                sales[:] = [s for s in sales if s.get("kode")!=pilih_kode]
                save_json(SALES_FILE, sales)
                st.success(f"✅ Transaksi {pilih_kode} dihapus")
                st.rerun()

# ---------------- Pengaturan Toko ----------------
    elif menu == "Pengaturan Toko":
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
