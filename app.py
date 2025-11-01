# app.py - FINAL Streamlit Kasir Mie Ayam Mas Ragil
import streamlit as st
import json, os
import pandas as pd
from datetime import datetime
import pytz
from io import BytesIO
import qrcode
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

def center32(text):
    return str(text).center(32)

def lr32(left, right, width=32):
    left_s = str(left)
    right_s = str(right)
    space = width - len(left_s) - len(right_s)
    if space < 1:
        left_s = left_s[:width - len(right_s) - 1]
        space = 1
    return left_s + (" " * space) + right_s

# ---------------- initial data ----------------
menu_data = load_json(MENU_FILE, {"makanan": {"Mie Ayam": 15000, "Bakso": 18000}, "minuman": {"Es Teh": 5000}})
checkout = load_json(CHECKOUT_FILE, [])
sales = load_json(SALES_FILE, [])
config = load_json(CONFIG_FILE, {"cashier": "ADMIN RAGIL", "counter": 0, "shop_name": "MIE AYAM MAS RAGIL",
                                  "address": "Jl. Rasa Bahagia No.1","ppn":11,"diskon":2,"footer":"Selalu segar bangsat"})

for s in sales:
    s.setdefault("kode","-")
    s.setdefault("cashier",config.get("cashier","ADMIN RAGIL"))
    s.setdefault("buyer","Umum")
    s.setdefault("items",[])

# ---------------- session defaults ----------------
if "admin_logged" not in st.session_state:
    st.session_state.admin_logged = False
if "buyer_name" not in st.session_state:
    st.session_state.buyer_name = ""
if "selected_buyer" not in st.session_state:
    st.session_state.selected_buyer = ""

# ---------------- struk builder ----------------
def build_struk(items, buyer, total_paid):
    tz = pytz.timezone("Asia/Jakarta")
    now = datetime.now(tz)
    config["counter"] = config.get("counter",0)+1
    save_json(CONFIG_FILE, config)
    kode = f"RG-{now.strftime('%Y%m%d')}-{config['counter']:05d}"

    subtotal = sum(i['harga']*i['jumlah'] for i in items)
    ppn_amt = int(subtotal * config.get("ppn",0)/100)
    diskon_amt = int(subtotal * config.get("diskon",0)/100)
    total_final = subtotal + ppn_amt - diskon_amt
    kembalian = total_paid - total_final

    lines=[]
    lines.append(center32(config.get("shop_name","")))
    lines.append(center32(config.get("address","")))
    lines.append("-"*32)
    lines.append(f"No. Transaksi: {kode}")
    lines.append(f"Kasir: {config.get('cashier')}")
    lines.append(f"Tgl: {now.strftime('%d-%m-%Y %H:%M:%S')} WIB")
    lines.append("-"*32)

    total_items=0
    for d in items:
        name=d["nama"][:32]
        qty=d["jumlah"]
        price=d["harga"]
        subtotal_item=qty*price
        lines.append(name)
        lines.append(lr32(f"{qty} x Rp {price:,}".replace(",", "."), f"Rp {subtotal_item:,}".replace(",", ".")))
        total_items += qty

    lines.append("-"*32)
    lines.append(lr32("Total Item", str(total_items)))
    lines.append(lr32("Subtotal", f"Rp {subtotal:,}".replace(",", ".")))
    lines.append(lr32(f'PPN ({config.get("ppn")}% )', f"Rp {ppn_amt:,}".replace(",", ".")))
    lines.append(lr32(f'Diskon ({config.get("diskon")}% )', f"-Rp {diskon_amt:,}".replace(",", ".")))
    lines.append(lr32("Total", f"Rp {total_final:,}".replace(",", ".")))
    lines.append(lr32("Tunai", f"Rp {total_paid:,}".replace(",", ".")))
    lines.append(lr32("Kembalian", f"Rp {kembalian:,}".replace(",", ".")))
    lines.append(lr32("Pembeli", buyer))
    lines.append("-"*32)
    lines.append(center32(config.get("footer","")))
    return "\n".join(lines), kode

# ---------------- user page ----------------
def user_page():
    st.title("🍜 Menu & Pesanan")
    st.subheader("👤 Nama Pembeli")
    st.session_state.buyer_name = st.text_input("Nama Pembeli", value=st.session_state.buyer_name)
    if not st.session_state.buyer_name:
        st.error("Nama pembeli wajib diisi!")

    st.subheader("📜 Menu")
    kategori = st.selectbox("Kategori", list(menu_data.keys()))
    item = st.selectbox("Menu", list(menu_data[kategori].keys()))
    qty = st.number_input("Jumlah", min_value=1, value=1)
    if st.button("Tambah ke Keranjang"):
        if not st.session_state.buyer_name:
            st.error("Isi nama pembeli dulu!")
        else:
            buyer = st.session_state.buyer_name
            checkout.append({"nama":item,"harga":menu_data[kategori][item],"jumlah":qty,"buyer":buyer})
            save_json(CHECKOUT_FILE, checkout)
            st.success("✅ Ditambahkan ke keranjang")

    st.subheader("🧾 Keranjang Saat Ini")
    if checkout:
        df=pd.DataFrame(checkout)
        df["total"]=df["harga"]*df["jumlah"]
        df["total"]=df["total"].apply(lambda x: f"Rp {x:,}".replace(",", "."))
        st.table(df)
    else:
        st.info("Keranjang kosong")

# ---------------- admin login page ----------------
def admin_login_page():
    st.subheader("🔒 Admin Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username=="admin" and password=="123":
            st.session_state.admin_logged=True
            st.success("Login berhasil")
            st.rerun()
        else:
            st.error("Username/Password salah")

# ---------------- admin main page ----------------
def admin_page():
    st.title("⚙️ Admin Panel")
    menu = st.sidebar.radio("Menu Admin", ["Data Menu","Data Pesanan","Pembayaran","Laporan","Pengaturan Toko"])
    if st.sidebar.button("Logout Admin"):
        st.session_state.admin_logged=False
        st.success("Logout berhasil")
        st.rerun()

    # ----- Data Menu -----
    if menu=="Data Menu":
        st.subheader("📋 Data Menu")
        rows=[]
        for k,items in menu_data.items():
            for n,h in items.items():
                rows.append({"Kategori":k,"Nama":n,"Harga":f"Rp {h:,}".replace(",",".")})
        st.table(pd.DataFrame(rows))

        st.subheader("➕ Tambah/Edit Menu")
        kat=st.selectbox("Kategori", list(menu_data.keys()))
        nama=st.text_input("Nama Menu")
        harga=st.number_input("Harga (Rp)", min_value=0)
        if st.button("Simpan Menu"):
            menu_data[kat][nama]=harga
            save_json(MENU_FILE,menu_data)
            st.success("✅ Menu disimpan")
            st.rerun()

        st.subheader("🗑️ Hapus Menu")
        del_kat=st.selectbox("Pilih Kategori", list(menu_data.keys()))
        del_item=st.selectbox("Pilih Menu", list(menu_data[del_kat].keys()))
        if st.button("Hapus Menu"):
            del menu_data[del_kat][del_item]
            save_json(MENU_FILE,menu_data)
            st.success("✅ Menu dihapus")
            st.rerun()

    # ----- Data Pesanan -----
    elif menu=="Data Pesanan":
        st.subheader("📝 Pesanan Masuk")
        if not checkout:
            st.info("Belum ada pesanan.")
        else:
            df=pd.DataFrame(checkout)
            df["total"]=df["harga"]*df["jumlah"]
            df["total"]=df["total"].apply(lambda x:f"Rp {x:,}".replace(",","."))
            st.table(df)
            if st.button("Hapus Semua Pesanan"):
                checkout.clear()
                save_json(CHECKOUT_FILE,checkout)
                st.success("✅ Semua pesanan dibersihkan")
                st.rerun()

    # ----- Pembayaran -----
    elif menu=="Pembayaran":
        st.header("💳 Pembayaran")
        buyers=list(set([d["buyer"] for d in checkout]))
        if not buyers:
            st.info("Belum ada transaksi")
            return
        selected_buyer=st.selectbox("Pilih Nama Pembeli",buyers)
        st.session_state.selected_buyer=selected_buyer
        buyer_items=[d for d in checkout if d["buyer"]==selected_buyer]
        df=pd.DataFrame(buyer_items)
        df["subtotal"]=df["harga"]*df["jumlah"]
        df["subtotal"]=df["subtotal"].apply(lambda x:f"Rp {x:,}".replace(",","."))
        st.table(df)
        total_paid=st.number_input("Tunai (Rp)", min_value=0)
        if st.button("Cetak Struk"):
            struk_text,kode=build_struk(buyer_items,selected_buyer,total_paid)
            st.text(struk_text)
            # barcode
            code128 = barcode.get('code128', kode, writer=ImageWriter())
            buf_bar=BytesIO()
            code128.write(buf_bar, options={"module_width":0.2,"module_height":15,"font_size":10})
            buf_bar.seek(0)
            st.image(buf_bar,width=230)
            # save sale
            sales.append({"tanggal":datetime.now(pytz.timezone("Asia/Jakarta")).strftime("%Y-%m-%d"),
                          "total":sum(d["harga"]*d["jumlah"] for d in buyer_items),
                          "kode":kode,"cashier":config.get("cashier"),"buyer":selected_buyer,"items":buyer_items})
            save_json(SALES_FILE,sales)
            # remove buyer from checkout
            checkout[:] = [d for d in checkout if d["buyer"]!=selected_buyer]
            save_json(CHECKOUT_FILE,checkout)
            st.success("✅ Transaksi disimpan. Tekan Ctrl+P untuk cetak.")

    # ----- Laporan -----
    elif menu=="Laporan":
        st.subheader("📊 Laporan Harian")
        if not sales:
            st.info("Belum ada transaksi.")
        else:
            df=pd.DataFrame(sales)
            df["Tanggal"]=pd.to_datetime(df["tanggal"]).dt.strftime("%d/%m/%Y")
            df["Pemasukan"]=df["total"].apply(lambda x:f"Rp {x:,}".replace(",",".")) 
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
            st.rerun()

    # ----- Pengaturan Toko -----
    elif menu=="Pengaturan Toko":
        st.subheader("🔧 Pengaturan Toko")
        shop_name=st.text_input("Nama Toko",value=config.get("shop_name"))
        address=st.text_input("Alamat Toko",value=config.get("address"))
        cashier=st.text_input("Nama Kasir",value=config.get("cashier"))
        ppn=st.number_input("PPN (%)",0,20,value=config.get("ppn"))
        diskon=st.number_input("Diskon (%)",0,100,value=config.get("diskon"))
        footer=st.text_input("Footer Struk",value=config.get("footer"))
        col1,col2=st.columns(2)
        with col1:
            if st.button("Simpan Pengaturan"):
                config.update({"shop_name":shop_name,"address":address,"cashier":cashier,
                               "ppn":ppn,"diskon":diskon,"footer":footer})
                save_json(CONFIG_FILE,config)
                st.success("✅ Pengaturan disimpan")
                st.rerun()
        with col2:
            if st.button("Reset Counter"):
                config["counter"]=0
                save_json(CONFIG_FILE,config)
                st.success("✅ Counter direset")

# ---------------- routing ----------------
st.set_page_config(page_title="Mie Ayam Mas Ragil", page_icon="🍜", layout="centered")
st.markdown("<style>body{background:#faf6f0;} footer{visibility:hidden;}</style>",unsafe_allow_html=True)

user_page()  # user menu selalu tampil

if st.session_state.admin_logged:
    admin_page()
else:
    if st.sidebar.button("Admin Login"):
        admin_login_page()
