import os
import json
import pandas as pd
import streamlit as st

MENU_FILE = "menu.json"
CHECKOUT_FILE = "checkout.json"

# ---------------------------
# Fungsi untuk load & save JSON
# ---------------------------
def save_data(filename, data):
    """
    Simpan data ke file JSON dengan aman.
    Non-serializable objects akan dikonversi ke string.
    """
    def safe_serializer(obj):
        try:
            json.dumps(obj)
            return obj
        except TypeError:
            return str(obj)

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, default=safe_serializer, ensure_ascii=False, indent=4)

def load_data(filename, default=[]):
    """
    Load data dari file JSON. Jika file tidak ada, return default.
    """
    if not os.path.exists(filename):
        return default
    with open(filename, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return default

# ---------------------------
# Inisialisasi menu default
# ---------------------------
def init_menu():
    """
    Jika menu.json belum ada atau kosong, isi dengan menu default.
    """
    menu_data = load_data(MENU_FILE, [])
    if not menu_data:
        default_menu = [
            {"nama": "Mie Ayam", "harga": 15000},
            {"nama": "Bakso", "harga": 12000},
            {"nama": "Es Teh", "harga": 5000},
        ]
        save_data(MENU_FILE, default_menu)

# ---------------------------
# Generate struk (PDF sederhana)
# ---------------------------
def generate_struk(checkout_data, nama_pembeli):
    """
    Buat file struk sederhana (text-based PDF).
    """
    filename = f"struk_{nama_pembeli.replace(' ', '_')}.txt"
    total = sum(item["harga"] * item["jumlah"] for item in checkout_data)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"Struk Pembayaran - {nama_pembeli}\n")
        f.write("="*30 + "\n")
        for item in checkout_data:
            f.write(f"{item['nama']} x{item['jumlah']} = Rp {item['harga']*item['jumlah']}\n")
        f.write("="*30 + "\n")
        f.write(f"Total: Rp {total}\n")
    return filename

# ---------------------------
# Main Admin App
# ---------------------------
def run_admin():
    st.title("Dashboard Admin 🍜")


    # Inisialisasi menu dan load data
    init_menu()
    menu_data = load_data(MENU_FILE, [])
    checkout_data = load_data(CHECKOUT_FILE, [])

    # ---------------------------
    # Laporan Penjualan
    # ---------------------------
    if menu == "Laporan Penjualan":
        st.title("📊 Laporan Penjualan")
        if not checkout_data:
            st.info("Belum ada transaksi yang tercatat.")
        else:
            df = pd.DataFrame(checkout_data)
            df["subtotal"] = df["harga"] * df["jumlah"]
            total = df["subtotal"].sum()
            st.dataframe(df, use_container_width=True)
            st.markdown(f"### 💰 Total Pendapatan: Rp {total:,}")

    # ---------------------------
    # Kelola Menu
    # ---------------------------
    elif menu == "Kelola Menu":
        st.title("🍜 Kelola Menu Restoran")
        df = pd.DataFrame(menu_data)
        st.dataframe(df, use_container_width=True)

        st.subheader("➕ Tambah Menu Baru")
        nama = st.text_input("Nama Menu Baru")
        harga = st.number_input("Harga (Rp)", min_value=0, step=1000)
        if st.button("Simpan Menu"):
            if nama and harga > 0:
                menu_data.append({"nama": nama, "harga": harga})  # Hanya simpan data JSON-friendly
                save_data(MENU_FILE, menu_data)
                st.success(f"Menu '{nama}' berhasil ditambahkan!")
            else:
                st.warning("Harap isi nama dan harga dengan benar.")
        if st.button("🔄 Refresh Data"):
            st.rerun()

    # ---------------------------
    # Data Pesanan
    # ---------------------------
    elif menu == "Data Pesanan":
        st.title("🧾 Data Pesanan Pelanggan")
        if not checkout_data:
            st.info("Belum ada pesanan dari pelanggan.")
        else:
            df = pd.DataFrame(checkout_data)
            st.dataframe(df, use_container_width=True)
            st.markdown(f"Total pesanan: **{len(df)} item**")
            if st.button("🧹 Hapus Semua Data Pesanan"):
                save_data(CHECKOUT_FILE, [])
                st.warning("Semua data pesanan telah dihapus!")
                st.rerun()

    # ---------------------------
    # Pembayaran
    # ---------------------------
    elif menu == "Pembayaran":
        st.title("💵 Proses Pembayaran")
        if not checkout_data:
            st.info("Belum ada pesanan untuk dibayar.")
        else:
            df = pd.DataFrame(checkout_data)
            grouped = df.groupby("nama").sum(numeric_only=True).reset_index()
            grouped["Total"] = grouped["harga"] * grouped["jumlah"]
            st.dataframe(grouped[["nama", "jumlah", "harga", "Total"]], use_container_width=True)

            nama_pembeli = st.text_input("Nama Pembeli untuk Struk")
            if st.button("✅ Tampilkan & Cetak Struk"):
                total = sum(item["harga"] * item["jumlah"] for item in checkout_data)
                struk_text = f"Struk Pembayaran - {nama_pembeli or 'Pelanggan'}\n"
                struk_text += "="*40 + "\n"
                for item in checkout_data:
                    struk_text += f"{item['nama']} x{item['jumlah']} = Rp {item['harga']*item['jumlah']}\n"
                struk_text += "="*40 + "\n"
                struk_text += f"Total: Rp {total}\n"

                st.subheader("📄 Struk Pembayaran")
                st.text(struk_text)

                filename = f"struk_{(nama_pembeli or 'Pelanggan').replace(' ', '_')}.txt"
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(struk_text)

                with open(filename, "rb") as f:
                    st.download_button("⬇️ Download Struk", f, file_name=os.path.basename(filename))

                save_data(CHECKOUT_FILE, [])
                st.success("Pembayaran berhasil dan data pesanan telah dikosongkan!")

# ---------------------------
# Jalankan Admin App
# ---------------------------
if __name__ == "__main__":
    run_admin()
