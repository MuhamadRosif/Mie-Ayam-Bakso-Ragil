# app.py - FINAL FULL (Alfamart-style struk + admin sidebar + WIB + tunai/kembalian)
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
    "shop_name": "MIE AYAM MAS RAGIL",
    "address": "Jl. Rasa Bahagia No.1",
    "cashier": "ADMIN RAGIL",
    "ppn": 11,
    "diskon": 2,
    "footer": "Selalu Segar Bangsat",
    "counter": 0
})

# normalize old sales entries
for s in sales:
    s.setdefault("kode","-")
    s.setdefault("cashier", config.get("cashier","ADMIN RAGIL"))
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

# ---------------- Login ----------------
def login_page():
    st.title("🍜 Mie Ayam Bakso Ragil")
    role = st.selectbox("Masuk sebagai", ["Pelanggan", "Admin"])
    user = st.text_input("Username")
    pw = st.text_input("Password", type="password")
    if st.button("Masuk"):
        if role=="Admin" and user=="admin" and pw=="123":
            st.session_state.role="admin"; st.rerun()
        elif role=="Pelanggan" and user=="user" and pw=="123":
            st.session_state.role="user"; st.rerun()
        else:
            st.error("Login salah!")

# ---------------- User Page ----------------
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
        df["total"] = df["total"].apply(lambda x: f"Rp {x:,}".replace(",","."))
        st.table(df)
    else:
        st.info("Keranjang kosong")

# ---------------- Admin Page ----------------
def admin_page():
    st.title("⚙️ Admin Panel")
    menu = st.sidebar.radio("Menu Admin", ["Data Menu","Data Pesanan","Pembayaran","Laporan","Pengaturan Toko"])

    # ---------------- Sidebar Pengaturan Toko ----------------
    if menu=="Pengaturan Toko":
        st.header("🏬 Pengaturan Toko")
        shop_name = st.text_input("Nama Toko", value=config.get("shop_name"))
        address = st.text_input("Alamat Toko", value=config.get("address"))
        cashier = st.text_input("Nama Kasir Default", value=config.get("cashier"))
        ppn = st.number_input("PPN (%)", 0, 100, config.get("ppn",11))
        diskon = st.number_input("Diskon (%)", 0, 100, config.get("diskon",2))
        footer = st.text_input("Footer", value=config.get("footer"))
        col1,col2 = st.columns(2)
        with col1:
            if st.button("Simpan Pengaturan"):
                config.update({"shop_name":shop_name,"address":address,"cashier":cashier,"ppn":ppn,"diskon":diskon,"footer":footer})
                save_json(CONFIG_FILE, config)
                st.success("✅ Pengaturan tersimpan")
        with col2:
            if st.button("Reset Counter (0)"):
                config["counter"]=0; save_json(CONFIG_FILE,config); st.success("✅ Counter direset")

    # ---------------- Data Menu ----------------
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
            menu_data[kat][nama]=harga
            save_json(MENU_FILE, menu_data)
            st.success("✅ Menu disimpan")
            st.experimental_rerun()

        st.subheader("🗑️ Hapus Menu")
        del_kat = st.selectbox("Pilih Kategori", list(menu_data.keys()))
        del_item = st.selectbox("Pilih Menu", list(menu_data[del_kat].keys()))
        if st.button("Hapus Menu"):
            del menu_data[del_kat][del_item]
            save_json(MENU_FILE, menu_data)
            st.success("✅ Menu dihapus")
            st.experimental_rerun()

    # ---------------- Data Pesanan ----------------
    elif menu=="Data Pesanan":
        st.header("📝 Pesanan Masuk")
        if not checkout:
            st.info("Belum ada pesanan.")
        else:
            df = pd.DataFrame(checkout)
            df["total"] = df["harga"]*df["jumlah"]
            df["total"] = df["total"].apply(lambda x: f"Rp {x:,}".replace(",","."))
            st.table(df)
            if st.button("Hapus Semua Pesanan"):
                checkout.clear(); save_json(CHECKOUT_FILE,checkout); st.success("✅ Checkout dibersihkan"); st.experimental_rerun()

    # ---------------- Pembayaran ----------------
    elif menu=="Pembayaran":
        st.header("💳 Pembayaran")
        if not checkout:
            st.info("Belum ada transaksi")
        else:
            df = pd.DataFrame(checkout)
            df["subtotal"] = df["harga"]*df["jumlah"]
            df["total"] = df["subtotal"]
            st.table(df[["nama","jumlah","harga","subtotal"]])

            total_item = sum(i["jumlah"] for i in checkout)
            subtotal_all = sum(i["harga"]*i["jumlah"] for i in checkout)
            ppn_amount = int(subtotal_all*config["ppn"]/100)
            diskon_amount = int(subtotal_all*config["diskon"]/100)
            total_final = subtotal_all + ppn_amount - diskon_amount

            st.write(f"**Subtotal:** Rp {subtotal_all:,}".replace(",","."))  
            st.write(f"**PPN ({config['ppn']}%):** Rp {ppn_amount:,}".replace(",","."))  
            st.write(f"**Diskon ({config['diskon']}%):** -Rp {diskon_amount:,}".replace(",","."))  
            st.write(f"**Total:** Rp {total_final:,}".replace(",","."))

            tunai = st.number_input("Tunai", min_value=total_final, value=total_final)
            kembalian = tunai - total_final

            st.write(f"**Kembalian:** Rp {kembalian:,}".replace(",","."))  
            st.write(f"**Nama Pembeli:** {checkout[0]['buyer']}")

            # cetak struk
            if st.button("🖨️ Cetak Struk"):
                tz = pytz.timezone("Asia/Jakarta")
                now = datetime.now(tz)
                config["counter"]+=1
                save_json(CONFIG_FILE,config)
                kode = f"RG-{now.strftime('%Y%m%d')}-{config['counter']:05d}"

                # helper
                def lr32(left,right):
                    space = 32-len(str(left))-len(str(right))
                    if space<1: space=1
                    return f"{str(left)}{' '*space}{str(right)}"
                def center32(text): return str(text).center(32)

                lines=[]
                lines.append(center32(config["shop_name"]))
                lines.append(center32(config["address"]))
                lines.append("-"*32)
                lines.append(f"No. Transaksi: {kode}")
                lines.append(f"Kasir: {config['cashier']}")
                lines.append(f"Tgl: {now.strftime('%d-%m-%Y %H:%M:%S')} WIB")
                lines.append("-"*32)

                for d in checkout:
                    lines.append(d["nama"])
                    lines.append(lr32(f"{d['jumlah']} x Rp {d['harga']:,}".replace(",","."), f"Rp {d['harga']*d['jumlah']:,}".replace(",",".")))

                lines.append("-"*32)
                lines.append(lr32("Total Item", total_item))
                lines.append(lr32("Subtotal", f"Rp {subtotal_all:,}".replace(",",".")))
                lines.append(lr32(f"PPN ({config['ppn']}%)", f"Rp {ppn_amount:,}".replace(",",".")))
                lines.append(lr32(f"Diskon ({config['diskon']}%)", f"-Rp {diskon_amount:,}".replace(",",".")))
                lines.append(lr32("Total", f"Rp {total_final:,}".replace(",",".")))
                lines.append(lr32("Tunai", f"Rp {tunai:,}".replace(",",".")))
                lines.append(lr32("Kembalian", f"Rp {kembalian:,}".replace(",",".")))
                lines.append(f"Pembeli: {checkout[0]['buyer']}")
                lines.append("-"*32)
                lines.append(center32(config["footer"]))

                # generate barcode
                code128 = barcode.get('code128', kode, writer=ImageWriter())
                buf_bar = BytesIO()
                code128.write(buf_bar, options={"module_width":0.2,"module_height":15,"font_size":10})
                buf_bar.seek(0)
                barcode_png = buf_bar.getvalue()

                st.text("\n".join(lines))
                st.image(barcode_png, width=230)

                # save sale
                sales.append({"tanggal":now.strftime("%Y-%m-%d"),"total":total_final,"kode":kode,"cashier":config["cashier"],"buyer":checkout[0]['buyer'],"items":checkout.copy()})
                save_json(SALES_FILE,sales)

                # clear checkout
                checkout.clear(); save_json(CHECKOUT_FILE,checkout)
                st.success("✅ Transaksi selesai, struk tampil & checkout dibersihkan")

    # ---------------- Laporan ----------------
    elif menu=="Laporan":
        st.header("📊 Laporan Harian")
        if not sales:
            st.info("Belum ada transaksi")
        else:
            df = pd.DataFrame(sales)
            df["Tanggal"] = pd.to_datetime(df["tanggal"]).dt.strftime("%d/%m/%Y")
            df["Pemasukan"] = df["total"].apply(lambda x: f"Rp {x:,}".replace(",","."))

            cols=["Tanggal","Pemasukan"]
            for c in ["kode","cashier","buyer"]:
                if c in df.columns: cols.append(c)
            st.table(df[cols])
            total_all=sum(s["total"] for s in sales)
            st.write(f"### 💰 Total: Rp {total_all:,}".replace(",","."))

            st.subheader("🗑️ Hapus Transaksi")
            pilih_kode=st.selectbox("Pilih kode transaksi yang mau dihapus",[s.get("kode",f"no-{i}") for i,s in enumerate(sales)])
            if st.button("Hapus Transaksi"):
                sales[:] = [s for s in sales if s.get("kode")!=pilih_kode]
                save_json(SALES_FILE,sales)
                st.success(f"✅ Transaksi {pilih_kode} dihapus")
                st.experimental_rerun()

# ---------------- routing ----------------
if st.session_state.role=="admin":
    st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"role":None}))
    admin_page()
elif st.session_state.role=="user":
    st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"role":None}))
    user_page()
else:
    login_page()
