# app.py - FINAL (Struk thermal + Code128 + WIB timezone + full sidebar pengaturan)
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
    "shop_name": "Mie Ayam & Bakso Mas Ragil Pusat",
    "address": "Jalan Kertoharjo",
    "ppn": 11,
    "diskon": 2,
    "footer": "Selalu Segar Bangsat"
})

# normalize old sales entries
for s in sales:
    s.setdefault("kode", "-")
    s.setdefault("cashier", config.get("cashier"))
    s.setdefault("buyer", "Umum")
    s.setdefault("items", [])

# ---------------- UI setup ----------------
st.set_page_config(page_title="Mie Ayam Mas Ragil", page_icon="🍜", layout="centered")
st.markdown("""<style>body{background:#faf6f0;} footer{visibility:hidden;}</style>""", unsafe_allow_html=True)

if "role" not in st.session_state: st.session_state.role = None
if "buyer_name" not in st.session_state: st.session_state.buyer_name = ""

# ---------------- Login ----------------
def login_page():
    st.title("🍜 Mie Ayam Bakso Ragil")
    role = st.selectbox("Masuk sebagai", ["Pelanggan","Admin"])
    user = st.text_input("Username")
    pw = st.text_input("Password", type="password")
    if st.button("Masuk"):
        if role=="Admin" and user=="admin" and pw=="123":
            st.session_state.role="admin"; st.rerun()
        elif role=="Pelanggan" and user=="user" and pw=="123":
            st.session_state.role="user"; st.rerun()
        else: st.error("Login salah!")

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
        df["total"] = df["harga"]*df["jumlah"]
        df["total"] = df["total"].apply(lambda x:f"Rp {x:,}".replace(",","."))
        st.table(df)
    else: st.info("Keranjang kosong")

# ---------------- Admin page ----------------
def admin_page():
    st.title("⚙️ Admin Panel")
    st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"role": None}))

    menu = st.sidebar.radio("Menu Admin", ["Data Menu","Data Pesanan","Pembayaran","Laporan","Pengaturan Toko"])

    # ------------------ Pengaturan Toko ------------------
    if menu=="Pengaturan Toko":
        st.header("🔧 Pengaturan Toko")
        shop_name = st.text_input("Nama Toko", value=config["shop_name"])
        address = st.text_input("Alamat Toko", value=config["address"])
        cashier_name = st.text_input("Nama Kasir", value=config["cashier"])
        ppn_val = st.number_input("PPN (%)", 0, 100, config["ppn"])
        diskon_val = st.number_input("Diskon (%)", 0, 100, config["diskon"])
        footer_val = st.text_input("Footer", value=config["footer"])
        if st.button("Simpan Pengaturan"):
            config.update({
                "shop_name":shop_name,
                "address":address,
                "cashier":cashier_name,
                "ppn":ppn_val,
                "diskon":diskon_val,
                "footer":footer_val
            })
            save_json(CONFIG_FILE, config)
            st.success("✅ Pengaturan Toko Disimpan")

    # ------------------ Data Menu ------------------
    elif menu=="Data Menu":
        st.header("📋 Data Menu")
        rows=[]
        for k,items in menu_data.items():
            for n,h in items.items():
                rows.append({"Kategori":k,"Nama":n,"Harga":f"Rp {h:,}".replace(",",".")})
        st.table(pd.DataFrame(rows))

        st.subheader("➕ Tambah/Edit Menu")
        kat = st.selectbox("Kategori", list(menu_data.keys()))
        nama = st.text_input("Nama Menu")
        harga = st.number_input("Harga (Rp)", min_value=0)
        if st.button("Simpan Menu"):
            menu_data[kat][nama] = harga
            save_json(MENU_FILE, menu_data)
            st.success("✅ Menu Disimpan")
            st.rerun()

        st.subheader("🗑️ Hapus Menu")
        del_kat = st.selectbox("Pilih Kategori", list(menu_data.keys()))
        del_item = st.selectbox("Pilih Menu", list(menu_data[del_kat].keys()))
        if st.button("Hapus Menu"):
            del menu_data[del_kat][del_item]
            save_json(MENU_FILE, menu_data)
            st.success("✅ Menu Dihapus")
            st.rerun()

    # ------------------ Data Pesanan ------------------
    elif menu=="Data Pesanan":
        st.header("📝 Pesanan Masuk")
        if not checkout: st.info("Belum ada pesanan")
        else:
            df = pd.DataFrame(checkout)
            df["total"] = df["harga"]*df["jumlah"]
            df["total"] = df["total"].apply(lambda x:f"Rp {x:,}".replace(",","."))
            st.table(df)
            if st.button("Hapus Semua Pesanan"):
                checkout.clear()
                save_json(CHECKOUT_FILE, checkout)
                st.success("✅ Semua Pesanan Dihapus")
                st.rerun()

    # ------------------ Pembayaran ------------------
    elif menu=="Pembayaran":
        st.header("💳 Pembayaran")
        if not checkout: st.info("Belum ada transaksi")
        else:
            df = pd.DataFrame(checkout)
            df["total"] = df["harga"]*df["jumlah"]
            df["total"] = df["total"].apply(lambda x:f"Rp {x:,}".replace(",","."))
            st.table(df)

            buyer_name = checkout[0]["buyer"]
            st.markdown(f"**Pembeli**: {buyer_name}")
            total_item = sum(i["jumlah"] for i in checkout)
            subtotal_all = sum(i["harga"]*i["jumlah"] for i in checkout)
            ppn_amount = int(subtotal_all*config["ppn"]/100)
            diskon_amount = int(subtotal_all*config["diskon"]/100)
            total_final = subtotal_all+ppn_amount-diskon_amount

            tunai = st.number_input("Tunai", min_value=0, value=total_final)
            kembalian = tunai - total_final

            # ------------------ struk helpers ------------------
            def center32(text): return str(text).center(32)
            def lr32(left,right):
                left_s=str(left)
                right_s=str(right)
                space=32-len(left_s)-len(right_s)
                if space<1:
                    left_s=left_s[:32-len(right_s)-1]
                    space=1
                return left_s+" "*space+right_s

            # ------------------ Cetak Struk ------------------
            if st.button("🖨️ Cetak Struk"):
                config["counter"]+=1
                save_json(CONFIG_FILE, config)
                counter=config["counter"]
                kode=f"RG-{datetime.now(pytz.timezone('Asia/Jakarta')).strftime('%Y%m%d')}-{counter:05d}"

                lines=[]
                lines.append(center32(config["shop_name"]))
                lines.append(center32(config["address"]))
                lines.append("-"*32)
                lines.append(f"No. Transaksi: {kode}")
                lines.append(f"Kasir: {config['cashier']}")
                lines.append(f"Tgl: {datetime.now(pytz.timezone('Asia/Jakarta')).strftime('%d-%m-%Y %H:%M:%S')} WIB")
                lines.append("-"*32)
                for d in checkout:
                    name = d["nama"][:32]
                    qty = d["jumlah"]
                    price = d["harga"]
                    subtotal_item = qty*price
                    lines.append(name)
                    lines.append(lr32(f"{qty} x Rp {price:,}".replace(",", "."), f"Rp {subtotal_item:,}".replace(",", ".")))
                lines.append("-"*32)
                lines.append(lr32("Total Item", str(total_item)))
                lines.append(lr32("Subtotal", f"Rp {subtotal_all:,}".replace(",", ".")))
                lines.append(lr32(f"PPN ({config['ppn']}%)", f"Rp {ppn_amount:,}".replace(",", ".")))
                lines.append(lr32(f"Diskon ({config['diskon']}%)", f"-Rp {diskon_amount:,}".replace(",", ".")))
                lines.append(lr32("Total", f"Rp {total_final:,}".replace(",", ".")))
                lines.append(lr32("Tunai", f"Rp {tunai:,}".replace(",", ".")))
                lines.append(lr32("Kembalian", f"Rp {kembalian:,}".replace(",", ".")))
                lines.append(lr32("Pembeli", buyer_name))
                lines.append(center32(config["footer"]))
                struk_text="\n".join(lines)
                st.text(struk_text)

                # generate barcode
                code128 = barcode.get('code128', kode, writer=ImageWriter())
                buf_bar = BytesIO()
                code128.write(buf_bar, options={"module_width":0.2,"module_height":15,"font_size":10})
                buf_bar.seek(0)
                barcode_png=buf_bar.getvalue()
                st.image(barcode_png, width=230)

                # save sale
                sales.append({
                    "tanggal": datetime.now(pytz.timezone('Asia/Jakarta')).strftime('%Y-%m-%d'),
                    "total": total_final,
                    "kode": kode,
                    "cashier": config['cashier'],
                    "buyer": buyer_name,
                    "items": checkout.copy()
                })
                save_json(SALES_FILE, sales)

                # clear checkout
                checkout.clear()
                save_json(CHECKOUT_FILE, checkout)
                st.success("✅ Transaksi selesai & struk siap dicetak")

    # ------------------ Laporan ------------------
    elif menu=="Laporan":
        st.header("📊 Laporan Harian")
        if not sales: st.info("Belum ada transaksi")
        else:
            df=pd.DataFrame(sales)
            df["Tanggal"]=pd.to_datetime(df["tanggal"]).dt.strftime("%d/%m/%Y")
            df["Pemasukan"]=df["total"].apply(lambda x:f"Rp {x:,}".replace(",","."))
            cols=["Tanggal","Pemasukan"]
            for c in ["kode","cashier","buyer"]:
                if c in df.columns: cols.append(c)
            st.table(df[cols])
            total_all=sum(s["total"] for s in sales)
            st.write(f"### 💰 Total: Rp {total_all:,}".replace(",", "."))

            st.subheader("🗑️ Hapus Transaksi")
            pilih_kode = st.selectbox("Pilih kode transaksi yang mau dihapus",[s.get("kode",f"no-{i}") for i,s in enumerate(sales)])
            if st.button("Hapus Transaksi"):
                sales[:] = [s for s in sales if s.get("kode")!=pilih_kode]
                save_json(SALES_FILE, sales)
                st.success(f"✅ Transaksi {pilih_kode} dihapus")
                st.rerun()

# ---------------- routing ----------------
if st.session_state.role=="admin": admin_page()
elif st.session_state.role=="user": user_page()
else: login_page()
