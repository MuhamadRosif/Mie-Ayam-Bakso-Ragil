import streamlit as st
import json, os
import pandas as pd
from datetime import datetime

MENU_FILE = "menu.json"
CHECKOUT_FILE = "checkout.json"
SALES_FILE = "sales.json"
CONFIG_FILE = "config.json"

# ================== JSON HELPERS ==================
def load_json(file, default):
    if not os.path.exists(file):
        with open(file, "w") as f:
            json.dump(default, f)
    with open(file, "r") as f:
        return json.load(f)

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=2)

# ================== INITIAL DATA ==================
menu_data = load_json(MENU_FILE, {"makanan":{}, "minuman":{}})
checkout = load_json(CHECKOUT_FILE, [])
sales = load_json(SALES_FILE, [])
config = load_json(CONFIG_FILE, {"cashier": "ADMIN RAGIL"})

# ================== UI CONFIG ==================
st.set_page_config(page_title="Mie Ayam Mas Ragil", page_icon="🍜", layout="centered")
st.markdown("""
<style>
body {background:#faf6f0;}
footer{visibility:hidden;}
</style>
""", unsafe_allow_html=True)

# ================== SESSION STATE SETUP ==================
if "role" not in st.session_state:
    st.session_state.role = None

# buyer name stored in session (only for user)
if "buyer_name" not in st.session_state:
    st.session_state.buyer_name = ""

# ================== LOGIN ==================
def login_page():
    st.title("🍜 Mie Ayam Bakso Ragil")
    role = st.selectbox("Masuk sebagai", ["Pelanggan", "Admin"])
    user = st.text_input("Username")
    pw   = st.text_input("Password", type="password")

    if st.button("Masuk"):
        if role == "Admin" and user == "admin" and pw == "123":
            st.session_state.role = "admin"
            st.rerun()
        elif role == "Pelanggan" and user == "user" and pw == "123":
            st.session_state.role = "user"
            st.rerun()
        else:
            st.error("Login salah!")

# ================== USER PAGE ==================
def user_page():
    st.title("🍜 Menu Pesanan")

    # Nama pembeli disediakan di user page saja
    st.subheader("👤 Nama Pembeli (diisi oleh Pelanggan)")
    st.session_state.buyer_name = st.text_input("Nama Pembeli (opsional)", value=st.session_state.buyer_name)

    kategori = st.selectbox("Kategori", list(menu_data.keys()))
    item = st.selectbox("Menu", list(menu_data[kategori].keys()))
    qty = st.number_input("Jumlah", min_value=1, value=1)

    if st.button("Tambah"):
        buyer = st.session_state.buyer_name or "Umum"
        checkout.append({
            "nama": item,
            "harga": menu_data[kategori][item],
            "jumlah": qty,
            "buyer": buyer
        })
        save_json(CHECKOUT_FILE, checkout)
        st.success("✅ Ditambahkan")

    st.subheader("🧾 Pesanan")
    if checkout:
        df = pd.DataFrame(checkout)
        df["total"] = df["harga"] * df["jumlah"]
        df["total"] = df["total"].apply(lambda x: f"Rp {x:,}".replace(",", "."))
        st.table(df)
    else:
        st.info("Belum ada pesanan.")

# ================== ADMIN PAGE ==================
def admin_page():
    st.title("⚙️ Admin Panel")

    # ---- Editable cashier name (stored in config.json) ----
    st.subheader("🔧 Pengaturan Kasir")
    kasir_input = st.text_input("Nama Kasir (ditampilkan di struk)", value=config.get("cashier", "ADMIN RAGIL"))
    if st.button("Simpan Nama Kasir"):
        config["cashier"] = kasir_input.strip() or "ADMIN RAGIL"
        save_json(CONFIG_FILE, config)
        st.success("✅ Nama kasir disimpan")
        st.rerun()

    menu = st.sidebar.radio("Menu", ["Data Menu","Data Pesanan","Pembayaran","Laporan"])

    # -------- Data Menu --------
    if menu == "Data Menu":
        st.subheader("📋 Menu Sekarang")
        rows=[]
        for k, items in menu_data.items():
            for i, h in items.items():
                rows.append({"Kategori":k,"Nama":i,"Harga":f"Rp {h:,}".replace(",",".")})
        st.table(pd.DataFrame(rows))

        st.subheader("➕ Tambah / Edit Menu")
        kat = st.selectbox("Kategori", list(menu_data.keys()))
        nama = st.text_input("Nama Menu")
        harga = st.number_input("Harga", min_value=0)
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

    # -------- Data Pesanan --------
    elif menu == "Data Pesanan":
        st.subheader("📝 Pesanan Masuk")
        if not checkout:
            st.info("Belum ada pesanan.")
        else:
            df = pd.DataFrame(checkout)
            df["total"] = df["harga"] * df["jumlah"]
            df["total"] = df["total"].apply(lambda x: f"Rp {x:,}".replace(",", "."))
            st.table(df)
            if st.button("Hapus Semua"):
                checkout.clear()
                save_json(CHECKOUT_FILE, checkout)
                st.success("✅ Pesanan dibersihkan")
                st.rerun()

    # -------- Pembayaran --------
    elif menu == "Pembayaran":
        if not checkout:
            st.info("Belum ada transaksi.")
        else:
            # Tampilkan tabel ringkasan
            df = pd.DataFrame(checkout)
            df["total"] = df["harga"] * df["jumlah"]
            df["total"] = df["total"].apply(lambda x: f"Rp {x:,}".replace(",", "."))
            st.table(df)

            # Nama pembeli ambil dari checkout (jika ada) -- buyer diinput cuma di user page
            buyer_name = checkout[0].get("buyer", "Umum") if checkout else "Umum"
            st.markdown(f"**Pembeli:** {buyer_name}")

            total = sum(item["harga"]*item["jumlah"] for item in checkout)

            # Buat struk ala Alfamart dengan format tanggal dd-mm-YYYY HH:MM:SS
            now = datetime.now()
            kode_transaksi = now.strftime("AC%y%m%d%H%M%S")
            cashier_name = config.get("cashier", "ADMIN RAGIL")

            lines = []
            lines.append("    PT. RAGIL JAYA MAKMUR")
            lines.append("      MIE AYAM & BAKSO RAGIL")
            lines.append("   JL. RASA BAHAGIA NO.1, JAKARTA")
            lines.append("  NPWP: 12.345.678.9-012.000")
            lines.append("")
            lines.append(f"Bon")
            lines.append(f"No. Transaksi: {kode_transaksi}")
            lines.append(f"Kasir: {cashier_name}")
            lines.append(f"Tgl. {now.strftime('%d-%m-%Y')}  {now.strftime('%H:%M:%S')}")
            lines.append("--------------------------------")
            # items
            for d in checkout:
                name_item = d["nama"][:20].ljust(20)
                qty = d["jumlah"]
                price = d["harga"]
                subtotal = price * qty
                # format like: NAME...............  1 x Rp 10.000   10.000
                item_line = f"{name_item} {str(qty).rjust(2)} x Rp {price:,}".replace(",", ".")
                lines.append(item_line)
                lines.append(f"  Subtotal: Rp {subtotal:,}".replace(",", "."))
            lines.append("--------------------------------")
            lines.append(f"Total Item : {len(checkout)}")
            lines.append(f"Total Harga: Rp {total:,}".replace(",", "."))
            lines.append(f"Tunai      : Rp {total:,}".replace(",", "."))
            lines.append(f"Kembalian  : Rp 0")
            lines.append(f"PPN (11%)  : Sudah termasuk")
            lines.append("--------------------------------")
            lines.append(f"Pembeli: {buyer_name}")
            lines.append("")
            lines.append("Kritik & Saran Hubungi:")
            lines.append("WA: 08xx-xxxx-xxxx")
            lines.append("IG: @mieayambaksoragil")
            lines.append("WWW: mieayambakso.example")
            lines.append("")
            lines.append("Terima kasih telah berbelanja")
            struk_text = "\n".join(lines)

            # --- Tombol Cetak Struk: tampilkan di app & finalize transaksi ---
            if st.button("🖨️ Cetak Struk"):
                st.subheader("🧾 Struk Pembayaran (Tampil di Aplikasi)")
                st.text(struk_text)

                # Simpan transaksi lengkap ke sales (hindari duplikat: hanya jika checkout tidak kosong)
                if checkout:
                    sales.append({
                        "tanggal": now.strftime("%Y-%m-%d"),
                        "total": total,
                        "kode": kode_transaksi,
                        "cashier": cashier_name,
                        "buyer": buyer_name,
                        "items": checkout.copy()
                    })
                    save_json(SALES_FILE, sales)

                    # Kosongkan checkout setelah cetak
                    checkout.clear()
                    save_json(CHECKOUT_FILE, checkout)

                    st.success("✅ Transaksi selesai — struk siap dicetak (Ctrl+P)")

            # --- Tombol Download Struk: buat file dan tunggu klik ---
            filename = f"struk_{kode_transaksi}.txt"
            with open(filename, "w") as f:
                f.write(struk_text)

            with open(filename, "rb") as f:
                clicked_download = st.download_button("⬇️ Download Struk", f, file_name=filename)
                if clicked_download:
                    # Jika user menekan download, finalize transaksi (simpan + clear)
                    if checkout:
                        sales.append({
                            "tanggal": now.strftime("%Y-%m-%d"),
                            "total": total,
                            "kode": kode_transaksi,
                            "cashier": cashier_name,
                            "buyer": buyer_name,
                            "items": checkout.copy()
                        })
                        save_json(SALES_FILE, sales)

                        checkout.clear()
                        save_json(CHECKOUT_FILE, checkout)

                        st.success("✅ Struk didownload & transaksi disimpan")

    # -------- Laporan --------
    elif menu == "Laporan":
        st.subheader("📊 Laporan Harian")
        sales_data = load_json(SALES_FILE, [])

        if not sales_data:
            st.info("Belum ada transaksi.")
        else:
            df = pd.DataFrame(sales_data)
            # tampilkan tanggal lebih friendly
            df["Tanggal"] = pd.to_datetime(df["tanggal"]).dt.strftime("%d/%m/%Y")
            df["Pemasukan"] = df["total"].apply(lambda x: f"Rp {x:,}".replace(",","."))
            st.table(df[["Tanggal","Pemasukan","kode","cashier","buyer"]])

            total_all = sum(s["total"] for s in sales_data)
            st.write(f"### 💰 Total: **Rp {total_all:,}**")

            # Hapus transaksi berdasarkan kode transaksi (lebih aman daripada tanggal)
            st.subheader("🗑️ Hapus Transaksi")
            pilih_kode = st.selectbox(
                "Pilih kode transaksi yang mau dihapus",
                [s.get("kode", f"no-{i}") for i,s in enumerate(sales_data)]
            )
            if st.button("Hapus Transaksi"):
                sales_data = [s for s in sales_data if s.get("kode") != pilih_kode]
                save_json(SALES_FILE, sales_data)
                st.success(f"✅ Transaksi {pilih_kode} berhasil dihapus")
                st.rerun()

# ================== ROUTING ==================
if st.session_state.role == "admin":
    st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"role":None}))
    admin_page()

elif st.session_state.role == "user":
    st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"role":None}))
    user_page()

else:
    login_page()
