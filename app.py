import streamlit as st
import json, os
import pandas as pd
from datetime import datetime
import pytz
from io import BytesIO
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

def center32(text):
    return str(text).center(32)

def lr32(left, right):
    left_s=str(left)
    right_s=str(right)
    space=32-len(left_s)-len(right_s)
    if space<1: left_s=left_s[:32-len(right_s)-1]; space=1
    return left_s+(" "*space)+right_s

# ---------------- initial data ----------------
menu_data = load_json(MENU_FILE, {"makanan":{"Mie Ayam":15000,"Bakso":18000},"minuman":{"Es Teh":5000}})
checkout = load_json(CHECKOUT_FILE, [])
sales = load_json(SALES_FILE, [])
config = load_json(CONFIG_FILE,{
    "cashier":"Hikam",
    "counter":0,
    "shop_name":"MIE AYAM & BAKSO RAGIL",
    "address":"Jl. Raya Masaran No. 45, Batang",
    "ppn":11,
    "diskon":10,
    "footer":"Kelompok 5 - Jaya Jaya"
})

# ---------------- UI setup ----------------
st.set_page_config(page_title="Mie Ayam Mas Ragil", page_icon="🍜", layout="wide")
st.markdown("""
<style>
body{background:#faf6f0;}
footer{visibility:hidden;}
pre.receipt{font-family:'Courier New', monospace;font-size:12px;white-space:pre-wrap;word-wrap:break-word;}
</style>
""", unsafe_allow_html=True)

# ---------------- session defaults ----------------
for key, default in [("page","user"),("admin_logged",False),("buyer_name",""),("last_page",None),
                     ("show_struk",False),("struk_data",""),("qr_bytes",None),("pending_sale",None)]:
    if key not in st.session_state: st.session_state[key]=default

# ---------------- build struk Alfamart + QR "Hikam - Dev" ----------------
def build_struk(buyer_checkout,buyer_name,cashier,config,tunai=None):
    tz=pytz.timezone("Asia/Jakarta")
    now=datetime.now(tz)
    config["counter"]+=1
    save_json(CONFIG_FILE,config)
    kode=f"RG-{now.strftime('%Y%m%d')}-{config['counter']:05d}"

    lines=[]
    lines.append(center32(config.get("shop_name")))
    lines.append(center32(config.get("address")))
    lines.append("-"*32)
    lines.append(lr32("Nama Pembeli",buyer_name))
    lines.append(lr32("No.Transaksi",kode))
    lines.append(lr32("Kasir",cashier))
    lines.append(lr32("Tanggal",now.strftime("%d/%m/%Y %H:%M:%S")))
    lines.append("-"*32)
    lines.append(f"{'Item':<16}{'Qty':>3}{'Harga':>13}")
    lines.append("-"*32)

    subtotal=0
    for i in buyer_checkout:
        name=i["nama"][:16]
        qty=i["jumlah"]
        price=i["harga"]*qty
        subtotal+=price
        lines.append(f"{name:<16}{qty:>3}{'Rp '+f'{price:,}'.replace(',','.') :>13}")

    ppn_amt=int(subtotal*config.get("ppn",11)/100)
    diskon_amt=int(subtotal*config.get("diskon",10)/100)
    total_final=subtotal+ppn_amt-diskon_amt
    if tunai is None: tunai=total_final
    kembalian=tunai-total_final

    lines.append("-"*32)
    lines.append(lr32("Total Bayar",f"Rp {total_final:,}".replace(",", ".")))
    lines.append(lr32("Tunai",f"Rp {tunai:,}".replace(",", ".")))
    lines.append(lr32("Kembalian",f"Rp {kembalian:,}".replace(",", ".")))
    lines.append("-"*32)
    lines.append(center32(config.get("footer")))

    qr=qrcode.QRCode(box_size=2,border=1)
    qr.add_data("Hikam - Dev")
    qr.make(fit=True)
    img_qr=qr.make_image(fill_color="black",back_color="white")
    buf=BytesIO()
    img_qr.save(buf,format="PNG")
    buf.seek(0)
    qr_bytes=buf.getvalue()

    struk_text="\n".join(lines)
    return struk_text,qr_bytes,kode,total_final

# ---------------- Pages ----------------
def user_page():
    if st.session_state.last_page!="user": st.session_state.buyer_name=""
    st.session_state.last_page="user"
    st.title("🍜 Menu & Pesanan")
    st.subheader("👤 Nama Pembeli (wajib diisi)")
    st.session_state.buyer_name=st.text_input("Nama Pembeli",value=st.session_state.buyer_name)
    disable_order=not st.session_state.buyer_name
    if disable_order: st.warning("Nama pembeli wajib diisi sebelum memesan")

    col_menu,col_cart=st.columns([2,1])
    with col_menu:
        st.subheader("📜 Menu")
        kategori=st.selectbox("Kategori",list(menu_data.keys()))
        item=st.selectbox("Menu",list(menu_data[kategori].keys()))
        qty=st.number_input("Jumlah",min_value=1,value=1)
        if st.button("Tambah ke Keranjang",disabled=disable_order):
            checkout.append({"nama":item,"harga":menu_data[kategori][item],"jumlah":qty,"buyer":st.session_state.buyer_name})
            save_json(CHECKOUT_FILE,checkout)
            st.success("✅ Ditambahkan ke keranjang")
            st.rerun()
    with col_cart:
        st.subheader("🧾 Keranjang Saat Ini")
        with st.expander("Lihat Keranjang"):
            if checkout:
                df=pd.DataFrame(checkout)
                df["total"]=df["harga"]*df["jumlah"]
                st.dataframe(df,width="stretch")
            else: st.info("Keranjang kosong")
    if not st.session_state.admin_logged:
        if st.sidebar.button("Admin Login"):
            st.session_state.page="admin_login"
            st.rerun()

def admin_login_page():
    st.title("🔒 Admin Login")
    username=st.text_input("Username")
    password=st.text_input("Password",type="password")
    if st.button("Login"):
        if username=="admin" and password=="123":
            st.session_state.admin_logged=True
            st.session_state.page="admin_panel"
            st.success("Login berhasil!")
            st.rerun()
        else: st.error("Username/Password salah")
    if st.button("Kembali ke Menu User"):
        st.session_state.page="user"
        st.rerun()

def admin_page():
    st.sidebar.title("⚙️ Admin Panel")
    menu=st.sidebar.radio("Menu Admin", ["Data Menu","Data Pesanan","Pembayaran","Laporan","Pengaturan Toko"])
    if st.sidebar.button("Logout Admin"):
        st.session_state.admin_logged=False
        st.session_state.page="user"
        st.rerun()

    if menu=="Data Menu":
        st.header("📋 Data Menu")
        rows=[]
        for k,items in menu_data.items():
            for n,h in items.items():
                rows.append({"Kategori":k,"Nama":n,"Harga":f"Rp {h:,}".replace(",",".")})
        st.dataframe(pd.DataFrame(rows),width="stretch")
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

    elif menu=="Data Pesanan":
        st.header("📝 Pesanan Masuk")
        if not checkout: st.info("Belum ada pesanan.")
        else:
            st.dataframe(pd.DataFrame(checkout),width="stretch")
            if st.button("Hapus Semua Pesanan"):
                checkout.clear()
                save_json(CHECKOUT_FILE,checkout)
                st.success("✅ Semua pesanan dibersihkan")
                st.rerun()

    elif menu=="Pembayaran":
        st.header("💳 Pembayaran")
        if not checkout: st.info("Belum ada transaksi"); return
        buyers=sorted(set([c["buyer"] for c in checkout if c.get("buyer")]))
        selected_buyer=st.selectbox("Pilih Pembeli", buyers)
        buyer_checkout=[c for c in checkout if c["buyer"]==selected_buyer]
        st.dataframe(pd.DataFrame(buyer_checkout),width="stretch")
        struk_text, qr_bytes, kode, total_final=build_struk(buyer_checkout,selected_buyer,config.get("cashier"),config)
        tunai=st.number_input("Tunai", min_value=0, value=total_final)
        kembalian=tunai-total_final
        st.write(f"Kembalian: Rp {kembalian:,}".replace(",","."))
        if st.button("🖨️ Tampilkan Struk"):
            st.session_state.struk_data=struk_text
            st.session_state.qr_bytes=qr_bytes
            st.session_state.show_struk=True
            st.session_state.pending_sale={"buyer":selected_buyer,"items":buyer_checkout,"total":total_final,"kode":kode,"cashier":config.get("cashier")}
            st.rerun()
        if st.session_state.show_struk:
            st.markdown(f"<pre class='receipt'>{st.session_state.struk_data}</pre>",unsafe_allow_html=True)
            if st.session_state.qr_bytes: st.image(BytesIO(st.session_state.qr_bytes),width=120)
            if st.button("🖨️ Cetak Struk"):
                sale=st.session_state.pending_sale
                if sale:
                    sales.append(sale)
                    save_json(SALES_FILE,sales)
                    checkout[:] = [c for c in checkout if c.get("buyer") != sale.get("buyer")]
                    save_json(CHECKOUT_FILE,checkout)
                st.session_state.show_struk=False
                st.session_state.struk_data=""
                st.session_state.qr_bytes=None
                st.session_state.pending_sale=None
                st.success("✅ Struk dicetak & transaksi disimpan")
                st.rerun()
            if st.button("🔙 Batal"):
                st.session_state.show_struk=False
                st.session_state.struk_data=""
                st.session_state.qr_bytes=None
                st.session_state.pending_sale=None
                st.rerun()

    elif menu=="Laporan":
        st.header("📊 Laporan Harian")
        if not sales: st.info("Belum ada transaksi.")
        else:
            df=pd.DataFrame(sales)
            df["Tanggal"]=pd.to_datetime(pd.Series([s.get("tanggal") for s in sales],dtype=str)).dt.strftime("%d/%m/%Y")
            df["Pemasukan"]=df["total"].apply(lambda x:f"Rp {x:,}".replace(",","."))
            st.dataframe(df[["Tanggal","Pemasukan","kode","cashier","buyer"]],width="stretch")
            total_all=sum(s["total"] for s in sales)
            st.write(f"### 💰 Total: Rp {total_all:,}".replace(",","."))
            pilih_kode=st.selectbox("Pilih kode transaksi untuk hapus",[s.get("kode") for s in sales])
            if st.button("Hapus Transaksi"):
                sales[:] = [s for s in sales if s.get("kode")!=pilih_kode]
                save_json(SALES_FILE,sales)
                st.success(f"✅ Transaksi {pilih_kode} dihapus")
                st.rerun()

    elif menu=="Pengaturan Toko":
        st.header("🛠️ Pengaturan Toko")
        with st.form("configform"):
            config["shop_name"]=st.text_input("Nama Toko",value=config["shop_name"])
            config["address"]=st.text_input("Alamat",value=config["address"])
            config["cashier"]=st.text_input("Nama Kasir",value=config["cashier"])
            config["ppn"]=st.number_input("PPN (%)",value=config["ppn"],min_value=0,max_value=100)
            config["diskon"]=st.number_input("Diskon (%)",value=config["diskon"],min_value=0,max_value=100)
            config["footer"]=st.text_input("Teks Footer Struk",value=config["footer"])
            if st.form_submit_button("💾 Simpan Pengaturan"):
                save_json(CONFIG_FILE,config)
                st.success("✅ Pengaturan disimpan.")
                st.rerun()

# ---------------- Routing ----------------
if st.session_state.page=="user": user_page()
elif st.session_state.page=="admin_login": admin_login_page()
elif st.session_state.page=="admin_panel" and st.session_state.admin_logged: admin_page()
else: st.session_state.page="user"; st.rerun()
