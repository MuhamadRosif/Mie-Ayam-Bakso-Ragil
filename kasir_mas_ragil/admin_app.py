import streamlit as st
import json
import os
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import A5
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas

MENU_FILE = "menu.json"
CHECKOUT_FILE = "checkout.json"
PAYMENT_FILE = "payments.json"

# ------------------ Helper Functions ------------------
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

# ------------------ Cetak Struk PDF ------------------
def generate_receipt(order_list, total):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A5)
    width, height = A5

    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width/2, height - 2*cm, "Mie Ayam Bakso Mas Ragil 🍜")
    c.setFont("Helvetica", 10)
    c.drawCentredString(width/2, height - 2.5*cm, "Jl. Kenikmatan No.88, Kuliner City")

    y = height - 3.5*cm
    c.setFont("Helvetica-Bold", 11)
    c.drawString(2*cm, y, "Daftar Pesanan:")
    y -= 0.5*cm

    c.setFont("Helvetica", 10)
    for item in order_list:
        c.drawString(2*cm, y, f"- {item['nama']} x{item['jumlah']} = Rp {item['subtotal']:,}")
        y -= 0.4*cm

    y -= 0.5*cm
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2*cm, y, f"Total: Rp {total:,}")
    y -= 1*cm

    c.setFont("Helvetica", 9)
    c.drawCentredString(width/2, y, "Terima kasih telah berkunjung 🙏")
    c.drawCentredString(width/2, y-0.4*cm, "Selamat menikmati makanan Anda!")
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

# ------------------ Main Admin Function ------------------
def run_admin():
    st.sidebar.title("👑 Admin Panel - Mas Ragil")
    menu = st.sidebar.selectbox(
        "Menu", ["Laporan Penjualan", "Kelola Menu", "Data Pesanan", "Pembayaran"]
    )
    st.sidebar.markdown("---")

    init_menu()
    menu_data = load_data(MENU_FILE, [])
    checkout_data = load_data(CHECKOUT_FILE, [])
    payment_data = load_data(PAYMENT_FILE, [])

    # =========================
    # LAPORAN PENJUALAN
    # =========================
    if menu == "Laporan Penjualan":
        st.title("📊 Laporan Penjualan")

        if not payment_data:
            st.info("Belum ada transaksi yang tercatat.")
        else:
            df = pd.DataFrame(payment_data)
            total = df["total"].sum()
            st.dataframe(df, use_container_width=True)
            st.markdown(f"### 💰 Total Pendapatan: Rp {total:,}")

    # =========================
    # KELOLA MENU
    # =========================
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

    # =========================
    # DATA PESANAN
    # =========================
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

    # =========================
    # PEMBAYARAN
    # =========================
    elif menu == "Pembayaran":
        st.title("💸 Proses Pembayaran")

        if not checkout_data:
            st.info("Belum ada pesanan yang siap dibayar.")
        else:
            df = pd.DataFrame(checkout_data)
            df["subtotal"] = df["harga"] * df["jumlah"]
            total = df["subtotal"].sum()

            st.dataframe(df, use_container_width=True)
            st.markdown(f"### Total Pembayaran: Rp {total:,}")

            nama_pelanggan = st.text_input("Nama Pelanggan")
            metode = st.selectbox("Metode Pembayaran", ["Tunai", "QRIS", "Transfer Bank"])

            if st.button("✅ Konfirmasi Pembayaran"):
                if nama_pelanggan.strip() != "":
                    payment_data.append({
                        "pelanggan": nama_pelanggan,
                        "total": total,
                        "metode": metode
                    })
                    save_data(PAYMENT_FILE, payment_data)
                    save_data(CHECKOUT_FILE, [])  # Kosongkan pesanan setelah dibayar

                    st.success("Pembayaran berhasil disimpan ✅")

                    # Cetak Struk
                    buffer = generate_receipt(checkout_data, total)
                    st.download_button(
                        label="🧾 Cetak Struk (PDF)",
                        data=buffer,
                        file_name=f"Struk_{nama_pelanggan}.pdf",
                        mime="application/pdf"
                    )
                else:
                    st.warning("Masukkan nama pelanggan terlebih dahulu.")
