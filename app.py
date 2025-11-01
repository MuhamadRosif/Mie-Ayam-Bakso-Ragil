# app.py - Struk Alfamart Style
import streamlit as st
import json, os
import pandas as pd
from datetime import datetime
import pytz
from io import BytesIO
import qrcode

MENU_FILE = "menu.json"
CHECKOUT_FILE = "checkout.json"
SALES_FILE = "sales.json"
CONFIG_FILE = "config.json"

def load_json(path, default):
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(default, f, indent=2, ensure_ascii=False)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

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

st.set_page_config(page_title="Mie Ayam Mas Ragil", page_icon="🍜", layout="centered")
st.markdown("""<style>body{background:#faf6f0;} footer{visibility:hidden;}</style>""", unsafe_allow_html=True)

if "page" not in st.session_state: st.session_state.page = "user"
if "admin_logged" not in st.session_state: st.session_state.admin_logged = False
if "buyer_name" not in st.session_state: st.session_state.buyer_name = ""

def center32(text): return str(text).center(32)
def lr32(left, right):
    left_s = str(left)
    right_s = str(right)
    space = 32 - len(left_s) - len(right_s)
    if space < 1: left_s = left_s[:32-len(right_s)-1]; space=1
    return left_s + (" "*space) + right_s

def user_page():
    st.title("🍜 Menu & Pesanan")
    st.subheader("👤 Nama Pembeli (wajib diisi)")
    st.session_state.buyer_name = st.text_input("Nama Pembeli", value=st.session_state.buyer_name)
    disable_order = not bool(st.session_state.buyer_name)
    if disable_order: st.warning("Nama pembeli wajib diisi sebelum memesan")

    st.subheader("📜 Menu")
    kategori = st.selectbox("Kategori", list(menu_data.keys()))
    item = st.selectbox("Menu", list(menu_data[kategori].keys()))
    qty = st.number_input("Jumlah", min_value=1, value=1)
    if st.button("Tambah ke Keranjang", disabled=disable_order):
        checkout.append({"nama": item, "harga": menu_data[kategori][item], "jumlah": qty, "buyer": st.session_state.buyer_name})
        save_json(CHECKOUT_FILE, checkout)
        st.success("✅ Ditambahkan ke keranjang")

    st.subheader("🧾 Keranjang Saat Ini")
    if checkout:
        df = pd.DataFrame(checkout)
        df["total"] = df["harga"] * df["jumlah"]
        df["total"] = df["total"].apply(lambda x: f"Rp {x:,}".replace(",", "."))
        st.table(df)
    else: st.info("Keranjang kosong")

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
        else: st.error("Username/Password salah")
    if st.button("Kembali ke Menu User"):
        st.session_state.page="user"
        st.rerun()

def admin_page():
    st.sidebar.title("⚙️ Admin Panel")
    menu = st.sidebar.radio("Menu Admin", ["Data Menu","Data Pesanan","Pembayaran","Laporan","Pengaturan Toko"])
    if st.sidebar.button("Logout Admin"):
        st.session_state.admin_logged=False
        st.session_state.page="user"
        st.success("Logout berhasil")
        st.rerun()

    if menu=="Pembayaran":
        st.header("💳 Pembayaran")
        if not checkout: st.info("Belum ada transaksi"); return
        buyers = list({c["buyer"] for c in checkout})
        selected_buyer = st.selectbox("Pilih Pembeli", buyers)
        buyer_checkout = [c for c in checkout if c["buyer"]==selected_buyer]

        subtotal = sum(i["harga"]*i["jumlah"] for i in buyer_checkout)
        ppn_amt = int(subtotal*config.get("ppn",11)/100)
        diskon_amt = int(subtotal*config.get("diskon",2)/100)
        total_final = subtotal + ppn_amt - diskon_amt
        tunai = st.number_input("Tunai", min_value=0, value=total_final)
        kembalian = tunai - total_final

        if st.button("🖨️ Cetak Struk"):
            tz=pytz.timezone("Asia/Jakarta")
            now=datetime.now(tz)
            config["counter"]+=1
            save_json(CONFIG_FILE, config)
            kode=f"RG-{now.strftime('%Y%m%d')}-{config['counter']:05d}"

            lines=[]
            lines.append(center32(config.get("shop_name")))
            lines.append(center32(config.get("address")))
            lines.append("-"*32)
            lines.append(f"No. Transaksi  : {kode}".ljust(32))
            lines.append(f"Kasir                 : {config.get('cashier')}".ljust(32))
            lines.append(f"Tanggal            : {now.strftime('%d-%m-%Y %H:%M:%S')} WIB".ljust(32))
            lines.append("-"*32)

            for i in buyer_checkout:
                name=i["nama"]
                qty=i["jumlah"]
                price=i["harga"]
                total=qty*price
                lines.append(f"{name}")
                qty_price = f"{qty} x Rp {price:,}".replace(",", ".")
                total_str = f"Rp {total:,}".replace(",", ".")
                lines.append(qty_price.ljust(20)+total_str.rjust(12))

            lines.append("-"*32)
            lines.append(lr32("Total Item", sum(i["jumlah"] for i in buyer_checkout)))
            lines.append(lr32("Subtotal", f"Rp {subtotal:,}".replace(",", ".")))
            lines.append(lr32(f"PPN ({config.get('ppn')}%)", f"Rp {ppn_amt:,}".replace(",", ".")))
            lines.append(lr32(f"Diskon ({config.get('diskon')}%)", f"-Rp {diskon_amt:,}".replace(",", ".")))
            lines.append(lr32("Total", f"Rp {total_final:,}".replace(",", ".")))
            lines.append(lr32("Tunai", f"Rp {tunai:,}".replace(",", ".")))
            lines.append(lr32("Kembalian", f"Rp {kembalian:,}".replace(",", ".")))
            lines.append(lr32("Pembeli", selected_buyer))
            lines.append("-"*32)
            lines.append(center32(config.get("footer")))
            lines.append(center32("Saya Muhamad Rosif Al Khikam Development Aplikasi ini"))

            qr=qrcode.QRCode(box_size=2,border=1)
            qr.add_data("Saya Muhamad Rosif Al Khikam Development Aplikasi ini")
            qr.make(fit=True)
            img=qr.make_image(fill_color="black", back_color="white")
            buf=BytesIO()
            img.save(buf, format="PNG")
            buf.seek(0)

            struk_text="\n".join(lines)
            st.text(struk_text)
            st.image(buf,width=230)

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
            st.success("✅ Struk dicetak & transaksi disimpan")
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
