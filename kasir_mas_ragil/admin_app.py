import streamlit as st
import json
import pandas as pd
import os

MENU_FILE = "menu.json"
CHECKOUT_FILE = "checkout.json"
ADMIN_PASS = "12345"  # ubah password admin di sini

# ---------------------------
# Load & Save JSON
# ---------------------------
def load_json(file):
    if not os.path.exists(file):
        return {}
    with open(file, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

menu_data = load_json(MENU_FILE)
checkout_data = load_json(CHECKOUT_FILE)

# ---------------------------
# UI Sidebar
# ---------------------------
mode = st.sidebar.selectbox("Mode Aplikasi", ["Pelanggan", "Admin"])

# =====================================
# MODE PELANGGAN
# =====================================
if mode == "Pelanggan":
    st.title("🍜 Kasir Mie Ayam Bakso Ragil")

    st.subheader("📋 Menu")
    for kategori, items in menu_data.items():
        st.write(f"### ✅ {kategori.upper()}")
        for nama, harga in items.items():
            col1, col2, col3 = st.columns([4,2,2])
            col1.write(nama)
            col2.write(f"Rp {harga}")
            if col3.button("Tambah", key=f"{kategori}_{nama}"):
                checkout_data.append({"nama": nama, "harga": harga, "jumlah": 1})
                save_json(CHECKOUT_FILE, checkout_data)
                st.success(f"{nama} ditambahkan!")

    st.divider()
    st.subheader("🛒 Keranjang Belanja")

    if not checkout_data:
        st.info("Belum ada pesanan.")
    else:
        df = pd.DataFrame(checkout_data)
        st.table(df)
        total = sum(item["harga"] * item["jumlah"] for item in checkout_data)
        st.write(f"### 💰 Total: Rp {total}")

        if st.button("✅ Checkout"):
            nama = st.text_input("Nama Pembeli")
            st.write("Klik tombol di bawah untuk cetak struk:")

            if st.button("🧾 CETAK STRUK"):
                struk = f"Struk Pembayaran - {nama or 'Pelanggan'}\n"
                struk += "="*40 + "\n"
                for item in checkout_data:
                    struk += f"{item['nama']} = Rp {item['harga']} x {item['jumlah']}\n"
                struk += "="*40 + f"\nTOTAL: Rp {total}\n"

                filename = f"struk_{(nama or 'pelanggan')}.txt"
                with open(filename, "w") as f:
                    f.write(struk)

                st.download_button("⬇️ Download Struk", open(filename,"rb"), file_name=filename)
                save_json(CHECKOUT_FILE, [])
                st.success("Pesanan selesai!")

# =====================================
# MODE ADMIN
# =====================================
elif mode == "Admin":
    st.title("🔐 Admin Panel")

    pwd = st.text_input("Masukkan Password Admin", type="password")
    if pwd != ADMIN_PASS:
        st.warning("Masukkan password untuk akses admin.")
        st.stop()

    menu_admin = st.sidebar.radio("Menu Admin", [
        "Kelola Menu",
        "Data Pesanan"
    ])

    # --------------------- KELola MENU ---------------------
    if menu_admin == "Kelola Menu":
        st.subheader("📦 Semua Menu")

        rows = []
        for kategori, items in menu_data.items():
            for nama, harga in items.items():
                rows.append({"Kategori": kategori, "Nama": nama, "Harga (Rp)": harga})

        st.dataframe(pd.DataFrame(rows), use_container_width=True)
        st.divider()

        st.subheader("➕ Tambah Menu")
        kategori = st.selectbox("Kategori", ["makanan", "minuman"])
        nama = st.text_input("Nama menu")
        harga = st.number_input("Harga", 0, step=1000)

        if st.button("💾 Simpan Menu"):
            if nama and harga>0:
                menu_data[kategori][nama] = harga
                save_json(MENU_FILE, menu_data)
                st.success("Menu ditambahkan!")
                st.rerun()
            else:
                st.error("Isi nama & harga dengan benar!")

    # --------------------- DATA PESANAN ---------------------
    elif menu_admin == "Data Pesanan":
        st.subheader("🧾 Riwayat Pesanan")

        if not checkout_data:
            st.info("Belum ada pesanan tersimpan.")
        else:
            st.table(pd.DataFrame(checkout_data))
            if st.button("🧹 Kosongkan Pesanan"):
                save_json(CHECKOUT_FILE, [])
                st.success("Data pesanan dikosongkan!")
                st.rerun()
