import streamlit as st
import json, os
import pandas as pd

MENU_FILE = "menu.json"
CHECKOUT_FILE = "checkout.json"

# ================== SAFE LOAD JSON ==================
def safe_load(file, default):
    try:
        if not os.path.exists(file):
            with open(file, "w") as f: json.dump(default, f, indent=2)
        with open(file, "r") as f:
            data = json.load(f)

        # Jika file rusak / salah tipe, reset
        if type(data) != type(default):
            raise ValueError
            
        return data
    except:
        with open(file, "w") as f: json.dump(default, f, indent=2)
        return default

menu_data = safe_load(MENU_FILE, {"makanan": {}, "minuman": {}})
checkout = safe_load(CHECKOUT_FILE, [])

def save_json(file, data):
    with open(file, "w") as f: json.dump(data, f, indent=2)

# ================== UI ==================
st.set_page_config(page_title="Mie Ayam Mas Ragil", page_icon="🍜", layout="centered")

# ================== LOGIN SESSION ==================
if "role" not in st.session_state:
    st.session_state.role = None

def login_page():
    st.title("🍜 Mie Ayam Bakso Mas Ragil")
    st.subheader("Silakan Login")

    role = st.selectbox("Masuk sebagai", ["Pelanggan", "Admin"])
    user = st.text_input("Username")
    pw = st.text_input("Password", type="password")

    if st.button("MASUK"):
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
    st.title("🍽️ Menu Pesanan")

    kategori = st.selectbox("Pilih Kategori", list(menu_data.keys()))
    if menu_data[kategori]:
        item = st.selectbox("Pilih Menu", list(menu_data[kategori].keys()))
        qty = st.number_input("Jumlah", min_value=1, value=1)

        if st.button("Tambah ke Pesanan"):
            checkout.append({
                "nama": item,
                "harga": menu_data[kategori][item],
                "jumlah": qty
            })
            save_json(CHECKOUT_FILE, checkout)
            st.success(f"{item} ditambahkan!")
    else:
        st.warning("Kategori kosong, minta admin menambahkan menu.")

    st.subheader("🧾 Pesanan Anda")
    if checkout:
        df = pd.DataFrame(checkout)
        df["total"] = df["harga"] * df["jumlah"]
        st.table(df)
        st.write(f"**Total: Rp {df['total'].sum():,}**")
    else:
        st.info("Belum ada pesanan.")

# ================== ADMIN PAGE ==================
def admin_page():
    st.title("⚙️ Admin Panel")

    menu = st.sidebar.radio("Menu Admin", ["Data Menu", "Data Pesanan", "Pembayaran", "Laporan"])

    # ====== DATA MENU ======
    if menu == "Data Menu":
        st.subheader("📋 Menu Sekarang")

        menu_list = []
        for kategori, items in menu_data.items():
            for nama, harga in items.items():
                menu_list.append({
                    "Kategori": kategori,
                    "Nama": nama,
                    "Harga": f"Rp {harga:,}".replace(",", ".")
                })

        if menu_list:
            df = pd.DataFrame(menu_list)
            st.table(df)
        else:
            st.info("Belum ada menu.")

        st.write("---")
        st.subheader("✏️ Edit / ❌ Hapus Menu")

        kategori_edit = st.selectbox("Pilih Kategori", list(menu_data.keys()))
        if menu_data[kategori_edit]:
            nama_edit = st.selectbox("Pilih Menu", list(menu_data[kategori_edit].keys()))
            harga_sekarang = menu_data[kategori_edit][nama_edit]
            harga_baru = st.number_input("Harga Baru (Rp)", value=harga_sekarang, min_value=0)

            col1, col2 = st.columns(2)
            if col1.button("💾 Simpan Perubahan"):
                menu_data[kategori_edit][nama_edit] = harga_baru
                save_json(MENU_FILE, menu_data)
                st.success("✅ Harga menu berhasil diupdate!")
                st.rerun()

            if col2.button("🗑️ Hapus Menu"):
                del menu_data[kategori_edit][nama_edit]
                save_json(MENU_FILE, menu_data)
                st.success("🗑️ Menu berhasil dihapus!")
                st.rerun()
        else:
            st.warning("Kategori ini kosong.")

        st.write("---")
        st.subheader("➕ Tambah Menu Baru")
        kat = st.selectbox("Kategori Baru", list(menu_data.keys()))
        nama = st.text_input("Nama Menu")
        harga = st.number_input("Harga (Rp)", min_value=0)

        if st.button("Simpan Menu Baru"):
            if nama.strip() == "":
                st.error("Nama menu tidak boleh kosong")
            else:
                menu_data[kat][nama] = harga
                save_json(MENU_FILE, menu_data)
                st.success("✅ Menu berhasil ditambahkan!")
                st.rerun()

    # ====== DATA PESANAN ======
    elif menu == "Data Pesanan":
        st.subheader("📝 Pesanan Masuk")

        if not checkout:
            st.info("Belum ada pesanan.")
        else:
            df = pd.DataFrame(checkout)
            df["Total"] = df["harga"] * df["jumlah"]
            df["Harga"] = df["harga"].apply(lambda x: f"Rp {x:,}".replace(",", "."))
            df["Total"] = df["Total"].apply(lambda x: f"Rp {x:,}".replace(",", "."))
            df = df[["nama","jumlah","Harga","Total"]]

            st.table(df)

            if st.button("Hapus Semua Pesanan"):
                checkout.clear()
                save_json(CHECKOUT_FILE, checkout)
                st.success("🧹 Semua pesanan dihapus!")
                st.rerun()

        # ====== PEMBAYARAN ======
    elif menu == "Pembayaran":
        if not checkout:
            st.info("Belum ada transaksi.")
        else:
            df = pd.DataFrame(checkout)
            df["Total"] = df["harga"] * df["jumlah"]
            df["Harga"] = df["harga"].apply(lambda x: f"Rp {x:,}".replace(",", "."))
            df["Total"] = df["Total"].apply(lambda x: f"Rp {x:,}".replace(",", "."))
            df = df[["nama","jumlah","Harga","Total"]]
            st.table(df)

            nama = st.text_input("Nama Pembeli", placeholder="Nama pelanggan")
            bayar = st.number_input("Jumlah Uang (Tunai)", min_value=0)

            total_belanja = sum(item["harga"] * item["jumlah"] for item in checkout)
            st.write(f"### Total: **Rp {total_belanja:,}**")

            if st.button("Cetak Struk"):
                kembalian = bayar - total_belanja

                from datetime import datetime
                now = datetime.now().strftime("%d/%m/%Y %H:%M")

                txt = ""
                txt += "MIE AYAM & BAKSO MAS RAGIL\n"
                txt += "Jl. Kenyang No.1, Indonesia\n"
                txt += "Telp: 0812-0000-0000\n"
                txt += "-"*40 + "\n"
                txt += f"Tanggal : {now}\nKasir   : Admin\n"
                txt += "-"*40 + "\n"

                for d in checkout:
                    txt += f"{d['nama']:<14} x{d['jumlah']}   {(d['harga']*d['jumlah']):,}\n"

                txt += "-"*40 + "\n"
                txt += f"TOTAL       Rp {total_belanja:,}\n"
                txt += f"TUNAI       Rp {bayar:,}\n"
                txt += f"KEMBALIAN   Rp {kembalian:,}\n"
                txt += "-"*40 + "\n"
                txt += "TERIMA KASIH 🙏\n"
                txt += "Barang yang dibeli tidak\n"
                txt += "dapat dikembalikan.\n"
                txt += "-"*40 + "\n"

                with open("struk.txt","w") as f: f.write(txt)
                st.download_button("Download Struk", open("struk.txt","rb"), "struk.txt")

                # simpan ke sales.json
                sales = load_json("sales.json", [])
                from datetime import datetime
                sales.append({"tanggal": datetime.now().strftime("%Y-%m-%d"), "total": total_belanja})
                save_json("sales.json", sales)

                checkout.clear()
                save_json(CHECKOUT_FILE, checkout)
                st.success("✅ Pembayaran selesai!")
                st.rerun()

# ================== ROUTING ==================
if st.session_state.role == "admin":
    st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"role": None}))
    admin_page()
elif st.session_state.role == "user":
    st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"role": None}))
    user_page()
else:
    login_page()
