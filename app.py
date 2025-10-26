import streamlit as st
import pandas as pd
import os
from kasir_mas_ragil import admin_app, user_app

# -----------------------
# File pengguna
# -----------------------
USERS_FILE = "users.csv"
if not os.path.exists(USERS_FILE):
    df = pd.DataFrame(columns=["username","password","role"])
    df.to_csv(USERS_FILE,index=False)

# -----------------------
# Session default
# -----------------------
if "login" not in st.session_state:
    st.session_state.login = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "role" not in st.session_state:
    st.session_state.role = ""

st.title("🍜 Kasir Mie Ayam & Bakso Mas Ragil")

tab = st.radio("Pilih:", ["Login", "Registrasi"], horizontal=True)

if tab=="Registrasi":
    st.subheader("📝 Registrasi User Baru")
    new_user = st.text_input("Username")
    new_pass = st.text_input("Password", type="password")
    if st.button("Daftar"):
        if new_user.strip()=="" or new_pass.strip()=="":
            st.warning("Isi username dan password dengan benar!")
        else:
            df = pd.read_csv(USERS_FILE)
            if new_user in df["username"].values:
                st.error("Username sudah digunakan.")
            else:
                df = pd.concat([df, pd.DataFrame([{"username":new_user,"password":new_pass,"role":"user"}])], ignore_index=True)
                df.to_csv(USERS_FILE,index=False)
                st.success("Registrasi berhasil! Silakan login.")

elif tab=="Login":
    st.subheader("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Masuk"):
        df = pd.read_csv(USERS_FILE)
        user_row = df[(df["username"]==username) & (df["password"]==password)]
        if not user_row.empty:
            st.session_state.login = True
            st.session_state.username = username
            st.session_state.role = user_row.iloc[0]["role"]
            st.experimental_rerun()
        else:
            st.error("Username atau password salah.")

# -----------------------
# Redirect setelah login
# -----------------------
if st.session_state.login:
    if st.session_state.role=="admin":
        admin_app.run_admin()
    else:
        user_app.run_user()
