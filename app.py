# app.py - FINAL VERSION with QR code
import streamlit as st
import json, os
import pandas as pd
from datetime import datetime
import pytz
from io import BytesIO
from PIL import Image
import base64
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
    "cashier": "Hikam",
    "counter": 0,
    "shop_name": "MIE AYAM & BAKSO RAGIL",
    "address": "Jl. Raya Masaran No. 45, Batang",
    "ppn": 11,
    "diskon": 2,
    "footer": "Terima kasih telah berbelanja!"
})

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

# ---------------- UI setup ----------------
st.set_page_config(page_title="Mie Ayam Mas Ragil", page_icon="🍜", layout="wide")
st.markdown("""<style>body{background:#faf6f0;} footer{visibility:hidden;} pre.receipt{font-family:monospace; font-size:12px; white-space:pre;}</style>""", unsafe_allow_html=True)

# ---------------- session defaults ----------------
if "page" not in st.session_state:
    st.session_state.page = "user"
if "admin_logged" not in st.session_state:
    st.session_state.admin_logged = False
if "buyer_name" not in st.session_state:
    st.session_state.buyer_name = ""
if "last_page" not in st.session_state:
    st.session_state.last_page = None
if "show_struk" not in st.session_state:
    st.session_state.show_struk = False
if "struk_data" not in st.session_state:
    st.session_state.struk_data = ""
if "barcode_bytes" not in st.session_state:
    st.session_state.barcode_bytes = None
if "pending_sale" not in st.session_state:
    st.session_state.pending_sale = None

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
        if checkout:
            df = pd.DataFrame(checkout)
            df["Total"] = df["harga"] * df["jumlah"]
            st.dataframe(df, width="stretch")
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
    menu = st.sidebar.radio("Menu Admin", ["Data Menu","Pembayaran","Laporan","Pengaturan Toko"])
    if st.sidebar.button("Logout Admin"):
        st.session_state.admin_logged = False
        st.session_state.page = "user"
        st.success("Logout berhasil")
        st.rerun()

    # ---------------- Data Menu ----------------
    if menu == "Data Menu":
        st.header("📋 Data Menu")
        rows = []
        for k, items in menu_data.items():
            for n, h in items.items():
                rows.append({"Kategori": k, "Nama": n, "Harga": f"Rp {h:,}".replace(",", ".")})
        st.dataframe(pd.DataFrame(rows), width="stretch")

    # ---------------- Pembayaran ----------------
    elif menu == "Pembayaran":
        st.header("💳 Pembayaran")
        if not checkout:
            st.info("Belum ada transaksi")
            return

        buyers = sorted(set([c["buyer"] for c in checkout if c.get("buyer")]))
        selected_buyer = st.selectbox("Pilih Pembeli", buyers)
        buyer_checkout = [c for c in checkout if c["buyer"]==selected_buyer]

        subtotal = sum(i["harga"]*i["jumlah"] for i in buyer_checkout)
        diskon_amt = int(subtotal * config.get("diskon",2)/100)
        total_final = subtotal - diskon_amt

        st.write(f"Total: Rp {total_final:,}".replace(",", "."))
        tunai = st.number_input("Tunai", min_value=0, value=total_final)
        kembalian = tunai - total_final
        st.write(f"Kembalian: Rp {kembalian:,}".replace(",", "."))

        if st.button("🖨️ Tampilkan Struk"):
            tz = pytz.timezone("Asia/Jakarta")
            now = datetime.now(tz)
            config["counter"] += 1
            save_json(CONFIG_FILE, config)
            kode = f"RG-{now.strftime('%Y%m%d')}-{config['counter']:05d}"

            # ---------------- build receipt lines ----------------
            lines = []
            lines.append(center32(config.get("shop_name")))
            lines.append(center32(config.get("address")))
            lines.append("-"*32)
            lines.append(lr32("Nama Pembeli", selected_buyer))
            lines.append(lr32("No. Transaksi", kode))
            lines.append(lr32("Kasir", config.get("cashier")))
            lines.append(lr32("Tanggal", now.strftime("%d/%m/%Y %H:%M:%S")))
            lines.append("-"*32)
            lines.append(f"{'Item':<20}{'Qty':>3}{'Harga':>8}")
            lines.append("-"*32)
            for i in buyer_checkout:
                name = i["nama"][:20]
                qty = i["jumlah"]
                price = i["harga"]
                line_item = f"{name:<20}{qty:>3}{'Rp ' + f'{price:,}'.replace(',', '.'):>8}"
                lines.append(line_item)
            lines.append("-"*32)
            lines.append(lr32("Total Bayar", f"Rp {total_final:,}".replace(",", ".")))
            lines.append(lr32("Tunai", f"Rp {tunai:,}".replace(",", ".")))
            lines.append(lr32("Kembalian", f"Rp {kembalian:,}".replace(",", ".")))
            lines.append("-"*32)
            lines.append(center32(config.get("footer")))

            struk_text = "\n".join(lines)

            # ---------------- generate QR code ----------------
            qr = qrcode.QRCode(box_size=3, border=1)
            qr.add_data(kode)
            qr.make(fit=True)
            img_qr = qr.make_image(fill_color="black", back_color="white")
            buf = BytesIO()
            img_qr.save(buf, format="PNG")
            buf.seek(0)
            qr_bytes = buf.getvalue()

            # store pending sale in session
            st.session_state.struk_data = struk_text
            st.session_state.barcode_bytes = qr_bytes
            st.session_state.pending_sale = {
                "tanggal": now.strftime("%Y-%m-%d"),
                "total": total_final,
                "kode": kode,
                "cashier": config.get("cashier"),
                "buyer": selected_buyer,
                "items": buyer_checkout
            }
            st.session_state.show_struk = True
            st.rerun()

        # preview struk
        if st.session_state.show_struk:
            st.subheader("🧾 Pratinjau Struk")
            st.markdown(f"<pre class='receipt'>{st.session_state.struk_data}</pre>", unsafe_allow_html=True)
            st.image(BytesIO(st.session_state.barcode_bytes), width=200)

            if st.button("🖨️ Cetak Struk"):
                st.markdown("<script>window.print();</script>", unsafe_allow_html=True)
                # finalize sale
                pending = st.session_state.pending_sale
                if pending:
                    sales.append(pending)
                    save_json(SALES_FILE, sales)
                    buyer = pending.get("buyer")
                    if buyer:
                        checkout[:] = [c for c in checkout if c.get("buyer") != buyer]
                        save_json(CHECKOUT_FILE, checkout)
                    st.session_state.pending_sale = None
                st.session_state.buyer_name = ""
                st.session_state.show_struk = False
                st.session_state.struk_data = ""
                st.session_state.barcode_bytes = None
                st.success("✅ Struk dicetak. Data pembeli & pesanan direset.")
                st.rerun()

# ---------------- Routing ----------------
if st.session_state.page == "user":
    user_page()
elif st.session_state.page == "admin_login":
    admin_login_page()
elif st.session_state.page == "admin_panel" and st.session_state.admin_logged:
    admin_page()
else:
    st.session_state.page = "user"
    st.rerun()
