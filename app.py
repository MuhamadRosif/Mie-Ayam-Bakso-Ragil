# app.py - Mie Ayam & Bakso Mas Ragil (Struk 32 char)
import streamlit as st
import json, os
import pandas as pd
from datetime import datetime
import pytz

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
    "shop_name": "Mie Ayam & Bakso Mas Ragil",
    "address": "Jl. Kertoharjo",
    "cashier": "ADMIN RAGIL",
    "ppn": 11,
    "diskon": 2,
    "footer": "Selalu segar bangsat",
    "counter": 0
})

# ---------------- UI setup ----------------
st.set_page_config(page_title="Mie Ayam & Bakso Mas Ragil", page_icon="🍜", layout="centered")
st.markdown("""<style>body{background:#faf6f0;} footer{visibility:hidden;}</style>""", unsafe_allow_html=True)

# ---------------- session defaults ----------------
if "admin_logged" not in st.session_state:
    st.session_state.admin_logged = False
if "buyer_name" not in st.session_state:
    st.session_state.buyer_name = ""

# ---------------- Admin Login ----------------
def admin_login():
    st.subheader("⚙️ Login Admin")
    user = st.text_input("Username")
    pw = st.text_input("Password", type="password")
    if st.button("Login"):
        if user=="admin" and pw=="123":
            st.session_state.admin_logged = True
            st.success("Login berhasil!"); st.rerun()
        else:
            st.error("Login salah!")

# ---------------- User Page ----------------
def user_page():
    st.title("🍜 Menu & Pemesanan")
    st.subheader("👤 Nama Pembeli (wajib diisi)")
    st.session_state.buyer_name = st.text_input("Nama Pembeli", value=st.session_state.buyer_name)
    
    if not st.session_state.buyer_name.strip():
        st.warning("Isi nama pembeli sebelum memesan.")
    
    st.subheader("📜 Menu")
    kategori = st.selectbox("Kategori", list(menu_data.keys()))
    item = st.selectbox("Menu", list(menu_data[kategori].keys()))
    qty = st.number_input("Jumlah", min_value=1, value=1)
    
    if st.button("Tambah ke Keranjang"):
        if not st.session_state.buyer_name.strip():
            st.error("Nama pembeli harus diisi!")
        else:
            buyer = st.session_state.buyer_name.strip()
            checkout.append({"nama": item, "harga": menu_data[kategori][item], "jumlah": qty, "buyer": buyer})
            save_json(CHECKOUT_FILE, checkout)
            st.success(f"✅ {item} ditambahkan ke keranjang untuk {buyer}")
    
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
    st.sidebar.header("Menu Admin")
    menu = st.sidebar.radio("Pilih Fitur", ["Data Menu","Data Pesanan","Pembayaran","Laporan","Pengaturan Toko"])
    
    # ---------- Data Menu ----------
    if menu=="Data Menu":
        st.header("📋 Data Menu")
        rows=[]
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
            st.success("✅ Menu disimpan"); st.rerun()
        
        st.subheader("🗑️ Hapus Menu")
        del_kat = st.selectbox("Pilih Kategori", list(menu_data.keys()))
        del_item = st.selectbox("Pilih Menu", list(menu_data[del_kat].keys()))
        if st.button("Hapus Menu"):
            del menu_data[del_kat][del_item]
            save_json(MENU_FILE, menu_data)
            st.success("✅ Menu dihapus"); st.rerun()
    
    # ---------- Data Pesanan ----------
    elif menu=="Data Pesanan":
        st.header("📝 Pesanan Masuk")
        if not checkout:
            st.info("Belum ada pesanan.")
        else:
            df = pd.DataFrame(checkout)
            df["total"] = df["harga"]*df["jumlah"]
            df["total"] = df["total"].apply(lambda x:f"Rp {x:,}".replace(",", "."))
            st.table(df)
            if st.button("Hapus Semua Pesanan"):
                checkout.clear()
                save_json(CHECKOUT_FILE, checkout)
                st.success("✅ Semua pesanan dibersihkan"); st.rerun()
    
    # ---------- Pengaturan Toko ----------
    elif menu=="Pengaturan Toko":
        st.header("⚙️ Pengaturan Toko")
        shop = st.text_input("Nama Toko", value=config.get("shop_name"))
        address = st.text_input("Alamat Toko", value=config.get("address"))
        cashier = st.text_input("Nama Kasir", value=config.get("cashier"))
        ppn = st.number_input("PPN (%)", 0, 20, value=config.get("ppn",11))
        diskon = st.number_input("Diskon (%)", 0, 50, value=config.get("diskon",0))
        footer = st.text_input("Footer Struk", value=config.get("footer"))
        if st.button("Simpan Pengaturan Toko"):
            config.update({"shop_name":shop,"address":address,"cashier":cashier,"ppn":ppn,"diskon":diskon,"footer":footer})
            save_json(CONFIG_FILE, config)
            st.success("✅ Pengaturan toko disimpan"); st.rerun()
    
    # ---------- Pembayaran ----------
    elif menu=="Pembayaran":
        st.header("💳 Pembayaran")
        if not checkout:
            st.info("Belum ada transaksi.")
        else:
            buyers = list({c["buyer"] for c in checkout})
            buyer = st.selectbox("Pilih pembeli untuk dibayar", buyers)
            buyer_checkout = [c for c in checkout if c["buyer"]==buyer]
            
            df = pd.DataFrame(buyer_checkout)
            df["subtotal"] = df["harga"]*df["jumlah"]
            df["subtotal"] = df["subtotal"].apply(lambda x:f"Rp {x:,}".replace(",", "."))
            st.table(df[["nama","jumlah","harga","subtotal"]])
            
            subtotal = sum(c["harga"]*c["jumlah"] for c in buyer_checkout)
            ppn_amt = int(subtotal*config.get("ppn",11)/100)
            diskon_amt = int(subtotal*config.get("diskon",0)/100)
            total_final = subtotal+ppn_amt-diskon_amt
            
            st.write(f"Subtotal: Rp {subtotal:,}".replace(",",".")) 
            st.write(f"PPN ({config.get('ppn')}%): Rp {ppn_amt:,}".replace(",",".")) 
            st.write(f"Diskon ({config.get('diskon')}%): -Rp {diskon_amt:,}".replace(",",".")) 
            st.write(f"Total: Rp {total_final:,}".replace(",",".")) 
            
            tunai = st.number_input("Tunai", min_value=0, value=total_final)
            kembalian = tunai-total_final
            st.write(f"Kembalian: Rp {kembalian:,}".replace(",",".")) 
            
            if st.button("🖨️ Cetak Struk"):
                tz = pytz.timezone("Asia/Jakarta")
                now = datetime.now(tz)
                config["counter"] += 1
                kode = f"RG-{now.strftime('%Y%m%d')}-{config['counter']:05d}"
                save_json(CONFIG_FILE, config)
                
                def lr32(left,right):
                    left_s=str(left)
                    right_s=str(right)
                    space = 32 - len(left_s) - len(right_s)
                    if space<1:
                        left_s = left_s[:32-len(right_s)-1]
                        space=1
                    return left_s + " "*space + right_s
                
                lines=[]
                lines.append(config["shop_name"].center(32))
                lines.append(config["address"].center(32))
                lines.append("-"*32)
                lines.append(f"No. Transaksi: {kode}")
                lines.append(f"Kasir: {config['cashier']}")
                lines.append(f"Tgl: {now.strftime('%d-%m-%Y %H:%M:%S')} WIB")
                lines.append("-"*32)
                
                for d in buyer_checkout:
                    lines.append(d["nama"])
                    lines.append(lr32(f"{d['jumlah']} x Rp {d['harga']:,}".replace(",","."), f"Rp {d['jumlah']*d['harga']:,}".replace(",",".")))
                
                lines.append("-"*32)
                lines.append(lr32("Total Item", str(sum(d["jumlah"] for d in buyer_checkout))))
                lines.append(lr32("Subtotal", f"Rp {subtotal:,}".replace(",",".")))
                lines.append(lr32(f"PPN ({config.get('ppn')}%)", f"Rp {ppn_amt:,}".replace(",",".")))
                lines.append(lr32(f"Diskon ({config.get('diskon')}%)", f"-Rp {diskon_amt:,}".replace(",",".")))
                lines.append(lr32("Total", f"Rp {total_final:,}".replace(",",".")))
                lines.append(lr32("Tunai", f"Rp {tunai:,}".replace(",",".")))
                lines.append(lr32("Kembalian", f"Rp {kembalian:,}".replace(",",".")))
                lines.append(f"Pembeli: {buyer}")
                lines.append(config.get("footer","").center(32))
                
                struk_text="\n".join(lines)
                st.text(struk_text)
                
                # save sale
                sales.append({"tanggal":now.strftime("%Y-%m-%d"),"total":total_final,"kode":kode,"cashier":config["cashier"],"buyer":buyer,"items":buyer_checkout.copy()})
                save_json(SALES_FILE, sales)
                
                # remove buyer items from checkout
                checkout[:] = [c for c in checkout if c["buyer"]!=buyer]
                save_json(CHECKOUT_FILE, checkout)
    
    # ---------- Laporan ----------
    elif menu=="Laporan":
        st.header("📊 Laporan")
        if not sales:
            st.info("Belum ada transaksi.")
        else:
            df = pd.DataFrame(sales)
            df["Tanggal"] = pd.to_datetime(df["tanggal"]).dt.strftime("%d/%m/%Y")
            df["Pemasukan"] = df["total"].apply(lambda x:f"Rp {x:,}".replace(",",".")) 
            cols = ["Tanggal","Pemasukan","kode","cashier","buyer"]
            st.table(df[cols])
            total_all = sum(s["total"] for s in sales)
            st.write(f"### 💰 Total: Rp {total_all:,}".replace(",","."))

# ---------------- Main ----------------
st.sidebar.title("🛒 Menu")
st.sidebar.button("Admin Panel", on_click=lambda: st.session_state.update({"admin_logged":False}) if st.session_state.admin_logged==False else st.rerun())

if st.session_state.admin_logged:
    admin_page()
else:
    user_page()
    st.sidebar.info("Untuk admin klik tombol Admin Panel")
