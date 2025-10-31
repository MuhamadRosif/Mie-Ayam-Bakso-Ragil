import streamlit as st
import pandas as pd
import os
import json

MENU_FILE = "kasir_mas_ragil/menu.json"
CHECKOUT_FILE = "kasir_mas_ragil/checkout.json"

# Load JSON
def load_json(file):
    if os.path.exists(file) and os.path.getsize(file) > 0:
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# Save JSON
def save_json(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def run_admin():

    st.sidebar.title("Admin Panel")
    menu = st.sidebar.radio("Menu", 
                            ["Laporan Penjualan", "Kelola Menu", "Data Pesanan", "Pembayaran"])

    menu_data = load_json(MENU_FILE)
    checkout_data = load_json(CHECKOUT_FILE)

    # ---------------------------
    # LAPORAN PENJUALAN
    # ---------------------------
    if menu == "Laporan Penjualan":
        st.title("📊 Laporan Penjualan")
        if not checkout_data:
            st.info("Belum ada transaksi.")
        else:
            df = pd.DataFrame(checkout_data)
            df["subtotal"] = df["harga"] * df["jumlah"]
            st.dataframe(df, use_container_width=True)
            st.success(f"💰 Total Pendapatan: Rp {df['subtotal'].sum():,}")

    # ---------------------------
    # KELOLA MENU
    # ---------------------------
    elif menu == "Kelola Menu":
        st.title("🍜 Kelola Menu")

        df = pd.DataFrame(menu_data)
        st.dataframe(df, use_container_width=True)

        st.subheader("➕ Tambah Menu Baru")
        nama = st.text_input("Nama Menu")
        harga = st.number_input("Harga (Rp)", min_value=0, step=1000)

        if st.button("Simpan Menu"):
            if nama and harga > 0:
                new_id = max([m["id"] for m in menu_data]) + 1 if menu_data else 1
                menu_data.append({"id": new_id, "nama": nama, "harga": harga})
                save_json(MENU_FILE, menu_data)
                st.success(f"Menu '{nama}' berhasil ditambahkan!")
                st.rerun()
            else:
                st.warning("Isi nama & harga dengan benar!")

    # ---------------------------
    # DATA PESANAN
    # ---------------------------
    elif menu == "Data Pesanan":
        st.title("🧾 Data Pesanan")
        if not checkout_data:
            st.info("Belum ada pesanan.")
        else:
            df = pd.DataFrame(checkout_data)
            st.dataframe(df, use_container_width=True)

            if st.button("🧹 Hapus Semua"):
                save_json(CHECKOUT_FILE, [])
                st.warning("Data pesanan dihapus!")
                st.rerun()

    # ---------------------------
    # PEMBAYARAN
    # ---------------------------
    elif menu == "Pembayaran":
        st.title("💵 Pembayaran")

        if not checkout_data:
            st.info("Belum ada pesanan.")
        else:
            df = pd.DataFrame(checkout_data)
            df["total"] = df["harga"] * df["jumlah"]
            st.dataframe(df, use_container_width=True)

            nama = st.text_input("Nama Pembeli")

            if st.button("✅ Cetak Struk"):
                total = df["total"].sum()

                text = f"Struk Pembayaran - {nama or 'Pelanggan'}\n"
                text += "="*40 + "\n"
                for i,row in df.iterrows():
                    text += f"{row['nama']} x{row['jumlah']} = Rp {row['total']}\n"
                text += "="*40 + f"\nTOTAL: Rp {total}\n"

                st.text(text)

                filename = f"struk_{(nama or 'Pelanggan').replace(' ','_')}.txt"
                with open(filename, "w", encoding="utf-8") as f: f.write(text)

                with open(filename, "rb") as f:
                    st.download_button("⬇️ Download Struk", f, filename)

                save_json(CHECKOUT_FILE, [])
                st.success("Pembayaran selesai ✅")

if __name__ == "__main__":
    run_admin()
