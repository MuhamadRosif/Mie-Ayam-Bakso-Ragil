import streamlit as st
import json, os
import pandas as pd

MENU_FILE = "menu.json"
CHECKOUT_FILE = "checkout.json"

# ================== LOAD / SAVE DATA ==================
def load_json(file):
    try:
        with open(file, "r") as f:
            data = json.load(f)
            if not isinstance(data, dict):
                raise ValueError("menu.json rusak, harus dict")
            return data
    except:
        # Reset default menu kalau file rusak
        default_menu = {
            "makanan": {
                "Mie Ayam": 15000,
                "Bakso Urat": 18000,
                "Mie Ayam Bakso": 20000,
                "Bakso Telur": 19000
            },
            "minuman": {
                "Es Teh Manis": 5000,
                "Es Jeruk": 7000,
                "Teh Hangat": 5000,
                "Jeruk Hangat": 6000
            }
        }
        with open(file, "w") as f:
            json.dump(default_menu, f, indent=2)
        return default_menu
        checkout = load_json(CHECKOUT_FILE, [])

# ================== UI CONFIG ==================
st.set_page_config(page_title="Mie Ayam Mas Ragil", page_icon="🍜", layout="centered")

st.markdown("""
<style>
body {
    background: url('https://images.unsplash.com/photo-1606755962773-0e2d7efc4b5b') no-repeat center center fixed;
    background-size: cover; font-family: 'Poppins', sans-serif;
}
.overlay {background:rgba(0,0,0,0.6); position:fixed; top:0; left:0; width:100%; height:100%;}
.login-card {
    position:relative; z-index:1; max-width:400px; margin:5rem auto; padding:3rem 2rem;
    background:rgba(255,183,77,0.18); backdrop-filter:blur(14px); border-radius:25px;
    box-shadow:0 0 25px rgba(255,150,0,0.3); text-align:center; color:#fff;
}
.header h2 {font-weight:700; color:#ffcc00; text-shadow:0 0 15px rgba(255,200,50,0.6);}
.stTextInput>div>div>input {background:rgba(255,255,255,0.15); color:white;}
.stButton>button {
    width:100%; height:45px; border-radius:12px; border:none; font-weight:700;
    background:linear-gradient(270deg,#ff6b00,#ffb300);
}
footer{visibility:hidden;}
</style>
""", unsafe_allow_html=True)

# ================== LOGIN ==================
if "role" not in st.session_state: st.session_state.role = None

def login_page():
    st.markdown("<div class='overlay'></div>", unsafe_allow_html=True)
    st.markdown("<div class='login-card'>", unsafe_allow_html=True)
    st.markdown("<h2>Selamat Datang<br>Mie Ayam Bakso Ragil 🍜</h2>", unsafe_allow_html=True)

    role = st.selectbox("Masuk sebagai", ["Pelanggan", "Admin"])
    user = st.text_input("Username")
    pw   = st.text_input("Password", type="password")

    if st.button("MASUK"):
        if role=="Admin" and user=="admin" and pw=="123":
            st.session_state.role = "admin"; st.rerun()
        elif role=="Pelanggan" and user=="user" and pw=="123":
            st.session_state.role = "user"; st.rerun()
        else:
            st.error("Login salah!")

    st.markdown("</div>", unsafe_allow_html=True)

# ================== USER PAGE ==================
def user_page():
    st.title("🍜 Menu Pesanan")

    kategori = st.selectbox("Pilih Kategori", list(menu_data.keys()))
    item = st.selectbox("Pilih Menu", list(menu_data[kategori].keys()))
    qty = st.number_input("Jumlah", min_value=1, value=1)

    if st.button("Tambah ke Pesanan"):
        checkout.append({"nama": item, "harga": menu_data[kategori][item], "jumlah": qty})
        save_json(CHECKOUT_FILE, checkout)
        st.success("Ditambahkan!")

    st.subheader("🧾 Pesanan Anda")
    if checkout:
        df = pd.DataFrame(checkout)
        df["total"] = df["harga"] * df["jumlah"]
        st.table(df)
        st.write(f"Total: **Rp {df['total'].sum():,}**")
    else:
        st.info("Belum ada pesanan.")

# ================== ADMIN PAGE ==================
def admin_page():
    st.title("⚙️ Admin Panel")

    menu = st.sidebar.radio("Menu", ["Data Menu", "Data Pesanan", "Pembayaran"])

    # ----- Kelola menu -----
    if menu == "Data Menu":
        st.subheader("📋 Menu Sekarang")

        # Convert dict → table
        menu_list = []
        for kategori, items in menu_data.items():
            for nama, harga in items.items():
                menu_list.append({
                    "Kategori": kategori,
                    "Nama": nama,
                    "Harga": harga
                })

        st.table(pd.DataFrame(menu_list))

        st.subheader("➕ Tambah Menu")
        kat = st.selectbox("Kategori", list(menu_data.keys()))
        nama = st.text_input("Nama Menu")
        harga = st.number_input("Harga", min_value=0)

        if st.button("Simpan Menu"):
            if nama.strip()=="" or harga <= 0:
                st.warning("Isi nama & harga yang benar!")
            else:
                menu_data[kat][nama] = harga
                save_json(MENU_FILE, menu_data)
                st.success("Menu ditambahkan!")
                st.rerun()

    # ----- Data Pesanan -----
    elif menu == "Data Pesanan":
        st.subheader("📝 Pesanan Masuk")

        if not checkout:
            st.info("Belum ada pesanan.")
        else:
            df = pd.DataFrame(checkout)
            st.table(df)

            if st.button("Hapus Semua"):
                save_json(CHECKOUT_FILE, [])
                st.success("Data pesanan dibersihkan!")
                st.rerun()

    # ----- Pembayaran -----
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
                    txt += f"{d['nama']} x{d['jumlah']} = Rp{d['harga']*d['jumlah']}\n"
                txt += "="*30 + f"\nTotal: Rp{total:,}\n"

                with open("struk.txt","w") as f: f.write(txt)
                st.download_button("Download Struk", open("struk.txt","rb"), "struk.txt")
                save_json(CHECKOUT_FILE, [])
                st.success("Pembayaran selesai!")
                st.rerun()

# ================== ROUTING ==================
if st.session_state.role=="admin":
    st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"role":None}))
    admin_page()
elif st.session_state.role=="user":
    st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"role":None}))
    user_page()
else:
    login_page()
