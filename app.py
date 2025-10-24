 import streamlit as st

# ===============================
# 🧾 Konfigurasi Halaman
# ===============================
st.set_page_config(
    page_title="Kasir Mie Ayam & Bakso Mas Ragil",
    page_icon="🍜",
    layout="centered"
)

# ===============================
# 🎯 Header Aplikasi
# ===============================
st.title("🍜 Kasir Mie Ayam & Bakso Mas Ragil")
st.caption("💻 Sistem kasir sederhana versi web - dibuat dengan ❤️ pakai Streamlit")

st.divider()

# ===============================
# 📋 Daftar Menu
# ===============================
menu_makanan = {
    "Mie Ayam": 15000,
    "Bakso Urat": 18000,
    "Mie Ayam Bakso": 20000,
    "Bakso Telur": 19000
}

menu_minuman = {
    "Es Teh Manis": 5000,
    "Es Jeruk": 7000,
    "Teh Hangat": 5000,
    "Jeruk Hangat": 6000
}

# ===============================
# 🧮 Input Pesanan
# ===============================
st.header("🧾 Pilih Pesanan Anda")

tab1, tab2 = st.tabs(["🍜 Makanan", "🥤 Minuman"])

pesanan = {}

with tab1:
    st.subheader("🍜 Pilih Makanan")
    for item, harga in menu_makanan.items():
        qty = st.number_input(f"{item} (Rp {harga:,})", min_value=0, max_value=20, step=1, key=f"makanan_{item}")
        if qty > 0:
            pesanan[item] = harga * qty

with tab2:
    st.subheader("🥤 Pilih Minuman")
    for item, harga in menu_minuman.items():
        qty = st.number_input(f"{item} (Rp {harga:,})", min_value=0, max_value=20, step=1, key=f"minuman_{item}")
        if qty > 0:
            pesanan[item] = harga * qty

st.divider()

# ===============================
# 💰 Hitung Total & Pembayaran
# ===============================
if st.button("💵 Hitung Total Pesanan"):
    if not pesanan:
        st.warning("Belum ada pesanan yang dipilih.")
    else:
        total = sum(pesanan.values())

        st.subheader("🧾 Ringkasan Pesanan")
        for item, subtotal in pesanan.items():
            st.write(f"- {item}: Rp {subtotal:,}")

        st.write("---")
        st.write(f"**Total Sebelum Diskon:** Rp {total:,}")

        # Diskon otomatis kalau total di atas 50 ribu
        diskon = 0
        if total >= 50000:
            diskon = int(0.1 * total)
            st.success(f"🎉 Diskon 10% diterapkan! (Rp {diskon:,})")

        total_bayar = total - diskon
        st.info(f"💵 Total yang harus dibayar: **Rp {total_bayar:,}**")

        # Simpan total ke session_state biar bisa dipakai tombol bayar
        st.session_state["total_bayar"] = total_bayar
        st.session_state["pesanan"] = pesanan

# ===============================
# 💳 Proses Pembayaran (dipisah tombolnya)
# ===============================
if "total_bayar" in st.session_state:
    st.divider()
    st.subheader("💳 Proses Pembayaran")

    uang_bayar = st.number_input("Masukkan jumlah uang bayar:", min_value=0, step=1000)

    if st.button("✅ Proses Pembayaran"):
        total_bayar = st.session_state["total_bayar"]
        pesanan = st.session_state["pesanan"]

        if uang_bayar <= 0:
            st.warning("Masukkan nominal uang terlebih dahulu.")
        elif uang_bayar < total_bayar:
            st.error("❌ Uang tidak cukup untuk membayar pesanan.")
        else:
            kembalian = uang_bayar - total_bayar
            st.success(f"✅ Pembayaran berhasil!\nKembalian Anda: **Rp {kembalian:,}**")

            # Struk Pembayaran
            st.write("---")
            st.subheader("🧾 Struk Pembayaran")
            for item, subtotal in pesanan.items():
                st.write(f"- {item}: Rp {subtotal:,}")
            st.write(f"**Total Bayar:** Rp {total_bayar:,}")
            st.write(f"**Uang Diterima:** Rp {uang_bayar:,}")
            st.write(f"**Kembalian:** Rp {kembalian:,}")
            st.caption("Terima kasih telah makan di Mie Ayam & Bakso Mas Ragil 🍜🙏")
