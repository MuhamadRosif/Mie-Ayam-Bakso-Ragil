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

    menu = st.sidebar.radio("Menu Admin", ["Data Menu", "Data Pesanan", "Pembayaran"])

    # ====== DATA MENU ======
    if menu == "Data Menu":
        st.subheader("📋 Menu Sekarang")

        menu_list = []
        for kategori, items in menu_data.items():
            for nama, harga in items.items():
                menu_list.append({"Kategori": kategori, "Nama": nama, "Harga": harga})
        
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
            harga_baru = st.number_input("Harga Baru", value=menu_data[kategori_edit][nama_edit])

            col1, col2 = st.columns(2)
            if col1.button("💾 Simpan Perubahan"):
                menu_data[kategori_edit][nama_edit] = harga_baru
                save_json(MENU_FILE, menu_data)
                st.success("Menu berhasil diupdate!")
                st.rerun()

            if col2.button("🗑️ Hapus Menu"):
                del menu_data[kategori_edit][nama_edit]
                save_json(MENU_FILE, menu_data)
                st.success("Menu berhasil dihapus!")
                st.rerun()
        else:
            st.warning("Kategori ini masih kosong.")

        st.write("---")
        st.subheader("➕ Tambah Menu Baru")
        kat = st.selectbox("Kategori Baru", list(menu_data.keys()))
        nama = st.text_input("Nama Menu")
        harga = st.number_input("Harga", min_value=0)

        if st.button("Simpan Menu Baru"):
            if nama.strip() == "":
                st.error("Nama menu tidak boleh kosong")
            else:
                menu_data[kat][nama] = harga
                save_json(MENU_FILE, menu_data)
                st.success("Menu ditambahkan!")
                st.rerun()

    # ====== DATA PESANAN ======
    elif menu == "Data Pesanan":
        st.subheader("📝 Pesanan Masuk")

        if not checkout:
            st.info("Belum ada pesanan.")
        else:
            st.table(pd.DataFrame(checkout))

            if st.button("Hapus Semua Pesanan"):
                checkout.clear()
                save_json(CHECKOUT_FILE, checkout)
                st.success("Pesanan dihapus!")
                st.rerun()

    # ====== PEMBAYARAN ======
    elif menu == "Pembayaran":
        if not checkout:
            st.info("Belum ada transaksi.")
        else:
            df = pd.DataFrame(checkout)
            df["total"] = df["harga"] * df["jumlah"]
            st.table(df)

            nama = st.text_input("Nama Pembeli")
            total = df["total"].sum()

            if st.button("Cetak Struk"):
                txt = f"Struk Pembelian - {nama or 'Pelanggan'}\n" + "="*30 + "\n"
                for d in checkout:
                    txt += f"{d['nama']} x{d['jumlah']} = Rp{d['harga'] * d['jumlah']}\n"
                txt += "="*30 + f"\nTotal: Rp{total:,}\n"

                with open("struk.txt","w") as f: f.write(txt)
                st.download_button("Download Struk", open("struk.txt","rb"), "struk.txt")

                checkout.clear()
                save_json(CHECKOUT_FILE, checkout)
                st.success("Pembayaran selesai!")

# ================== ROUTING ==================
if st.session_state.role == "admin":
    st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"role": None}))
    admin_page()
elif st.session_state.role == "user":
    st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"role": None}))
    user_page()
else:
    login_page()
