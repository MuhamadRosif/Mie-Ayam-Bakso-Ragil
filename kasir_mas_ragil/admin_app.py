import streamlit as st
import json
import os
import pandas as pd

# ==========================
#   KONFIG LOGIN
# ==========================
USERS = {
    "admin": "admin123",
    "kasir": "kasir123"
}

MENU_FILE = "menu.json"
ORDER_FILE = "checkout.json"

# ==========================
#   FUNGSI JSON
# ==========================
def load(file):
    if not os.path.exists(file):
        return {}
    with open(file, "r", encoding="utf-8") as f:
        return json.load(f)

def save(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

menu = load(MENU_FILE)
orders = load(ORDER_FILE)

# ==========================
#   LOGIN PAGE
# ==========================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None

if not st.session_state.logged_in:
    st.title("🔐 Login Kasir & Admin")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Masuk"):
        if username in USERS and USERS[username] == password:
            st.session_state.logged_in = True
            st.session_state.role = username
            st.success(f"Selamat datang, {username} 👋")
            st.rerun()
        else:
            st.error("Username / password salah")

    st.stop()

# Logout
st.sidebar.button("⏻ Logout", on_click=lambda: st.session_state.update({"logged_in": False}))

role = st.session_state.role

# ==========================
#   MENU KASIR
# ==========================
if role == "kasir":
    st.title("🍜 Kasir - Mie Ayam Bakso Ragil")

    for kategori, items in menu.items():
        st.write(f"### ✅ {kategori.upper()}")
        for nama, harga in items.items():
            col1, col2, col3 = st.columns([5,3,2])
            col1.write(nama)
            col2.write(f"Rp {harga:,}")
            if col3.button("Tambah", key=f"{kategori}_{nama}"):
                orders.append({"nama": nama, "harga": harga, "jumlah": 1})
                save(ORDER_FILE, orders)
                st.success(f"{nama} ditambahkan!")

    st.divider()
    st.subheader("🛒 Keranjang Pesanan")

    if not orders:
        st.info("Belum ada pesanan.")
    else:
        df = pd.DataFrame(orders)
        st.table(df)
        total = sum(i["harga"] * i["jumlah"] for i in orders)
        st.write(f"### 💰 Total: Rp {total:,}")

        nama = st.text_input("Nama Customer")

        if st.button("✅ Selesaikan & Cetak"):
            nota = f"Struk Pesanan - {nama or 'Customer'}\n" + "="*30 + "\n"
            for item in orders:
                nota += f"{item['nama']}  x{item['jumlah']}  = Rp {item['harga']}\n"
            nota += "="*30 + f"\nTOTAL: Rp {total:,}"

            filename = f"struk_{nama or 'customer'}.txt"
            with open(filename, "w") as f:
                f.write(nota)

            st.download_button("⬇️ Download Struk", open(filename,"rb"), file_name=filename)
            save(ORDER_FILE, [])
            st.success("Pesanan selesai ✅")
            st.rerun()

# ==========================
#   MENU ADMIN
# ==========================
elif role == "admin":
    st.title("⚙️ Admin Panel")

    tab1, tab2 = st.tabs(["📦 Kelola Menu", "📑 Data Pesanan"])

    with tab1:
        st.subheader("Menu Saat Ini")
        rows = [{"Kategori": k, "Nama": n, "Harga": h}
                for k, items in menu.items() for n, h in items.items()]
        st.dataframe(pd.DataFrame(rows), use_container_width=True)

        st.divider()
        st.subheader("➕ Tambah Menu")

        kategori = st.selectbox("Kategori", ["makanan", "minuman"])
        nama = st.text_input("Nama Menu Baru")
        harga = st.number_input("Harga", step=1000)

        if st.button("💾 Simpan Menu"):
            if nama and harga > 0:
                menu[kategori][nama] = harga
                save(MENU_FILE, menu)
                st.success("Menu ditambahkan ✅")
                st.rerun()
            else:
                st.error("Nama & harga wajib diisi!")

    with tab2:
        st.subheader("🧾 Riwayat Pesanan")

        if not orders:
            st.info("Belum ada pesanan")
        else:
            st.table(pd.DataFrame(orders))
            if st.button("🧹 Hapus Semua"):
                save(ORDER_FILE, [])
                st.success("Data pesanan dihapus ✅")
                st.rerun()
