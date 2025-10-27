import streamlit as st
import json
import os
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

MENU_FILE = "menu.json"
CHECKOUT_FILE = "checkout.json"
STRUK_FOLDER = "struk"

# ========== Fungsi bantu ==========
def load_data(file, default):
    if os.path.exists(file):
        try:
            with open(file, "r") as f:
                return json.load(f)
        except:
            pass
    return default

def save_data(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def init_menu():
    if not os.path.exists(MENU_FILE):
        data = [
            {"nama": "Mie Ayam Original", "harga": 12000},
            {"nama": "Mie Ayam Bakso", "harga": 15000},
            {"nama": "Bakso Campur", "harga": 18000},
            {"nama": "Es Teh Manis", "harga": 5000},
            {"nama": "Es Jeruk", "harga": 6000},
        ]
        save_data(MENU_FILE, data)

def generate_struk(pesanan, nama_pembeli="Pelanggan"):
    """Buat PDF struk pembelian"""
    if not os.path.exists(STRUK_FOLDER):
        os.makedirs(STRUK_FOLDER)
    filename = os.path.join(STRUK_FOLDER, f"struk_{nama_pembeli}.pdf")
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    y = height - 80
    c.setFont("Helvetica-Bold", 16)
    c.drawString(200, y, "Mie Ayam Bakso Mas Ragil 🍜")
    y -= 20
    c.setFont("Helvetica", 10)
    c.drawString(230, y, "Jl. Kenikmatan No. 88, Ragil City")
    y -= 40

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, f"Nama Pembeli: {nama_pembeli}")
    y -= 20
    c.drawString(50, y, "------------------------------------------")
    y -= 20
    c.setFont("Helvetica", 11)
    total = 0
    for item in pesanan:
        nama = item.get("nama", "")
        harga = item.get("harga", 0)
        jumlah = item.get("jumlah", 1)
        subtotal = harga * jumlah
        total += subtotal
        c.drawString(50, y, f"{nama} ({jumlah}x) - Rp{subtotal:,}")
        y -= 18
    y -= 10
    c.drawString(50, y, "------------------------------------------")
    y -= 20
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, f"Total Bayar: Rp{total:,}")
    y -= 40
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(200, y, "Terima kasih atas kunjungan Anda!")
    c.save()
    return filename

# ========== Fungsi utama admin ==========
def run_admin():
    st.sidebar.title("👑 Admin Panel - Mas Ragil")
    menu = st.sidebar.selectbox("Menu", ["Laporan Penjualan", "Kelola Menu", "Data Pesanan", "Pembayaran"])
    st.sidebar.markdown("---")

    init_menu()
    menu_data = load_data(MENU_FILE, [])
    checkout_data = load_data(CHECKOUT_FILE, [])

    # LAPORAN PENJUALAN
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

    # KELOLA MENU
    elif menu == "Kelola Menu":
        st.title("🍜 Kelola Menu Restoran")
        df = pd.DataFrame(menu_data)
        st.dataframe(df, use_container_width=True)

        st.subheader("➕ Tambah Menu Baru")
        nama = st.text_input("Nama Menu Baru")
        harga = st.number_input("Harga (Rp)", min_value=0, step=1000)
        if st.button("Simpan Menu"):
            if nama and harga > 0:
                menu_data.append({"nama": nama, "harga": harga})
                save_data(MENU_FILE, menu_data)
                st.success(f"Menu '{nama}' berhasil ditambahkan!")
            else:
                st.warning("Harap isi nama dan harga dengan benar.")
        if st.button("🔄 Refresh Data"):
            st.rerun()

    # DATA PESANAN
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

    # PEMBAYARAN
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
            if st.button("✅ Tandai Lunas & Cetak Struk"):
                filename = generate_struk(checkout_data, nama_pembeli or "Pelanggan")
                save_data(CHECKOUT_FILE, [])  # Kosongkan data setelah pembayaran
                st.success(f"Pembayaran berhasil dan struk telah dibuat: `{filename}`")
                with open(filename, "rb") as f:
                    st.download_button("⬇️ Download Struk PDF", f, file_name=os.path.basename(filename))
