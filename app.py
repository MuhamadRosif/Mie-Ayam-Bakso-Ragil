import streamlit as st

# ===============================
# PAGE CONFIG
# ===============================
st.set_page_config(page_title="Login | Rumah Makan Mas Ragil", page_icon="🍜", layout="centered")

# ===============================
# CUSTOM CSS
# ===============================
st.markdown("""
    <style>
        body {
            background-color: #f7f9fc;
        }
        .login-box {
            background-color: #0a2a52; /* biru tua elegan */
            color: white;
            padding: 40px;
            border-radius: 15px;
            width: 360px;
            margin: 100px auto;
            box-shadow: 0px 5px 25px rgba(0,0,0,0.25);
            text-align: center;
        }
        .login-box h2 {
            font-size: 26px;
            margin-bottom: 10px;
        }
        .login-box label {
            float: left;
            color: #c9d6e3;
            font-size: 15px;
        }
        .login-box input {
            width: 100%;
            border: none;
            padding: 10px;
            margin-top: 5px;
            border-radius: 6px;
            outline: none;
        }
        .stSelectbox {
            text-align: left;
        }
        .login-button {
            background-color: #1d4e89;
            color: white;
            border: none;
            padding: 10px 0;
            width: 100%;
            border-radius: 8px;
            font-size: 16px;
            margin-top: 20px;
        }
        .login-button:hover {
            background-color: #2468b0;
            cursor: pointer;
        }
        .forgot {
            font-size: 13px;
            color: #a5b7cc;
            margin-top: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# ===============================
# FORM LOGIN
# ===============================
st.markdown('<div class="login-box">', unsafe_allow_html=True)
st.markdown("<h2>Rumah Makan Mas Ragil</h2>", unsafe_allow_html=True)
st.markdown("<p style='font-size:14px;color:#c9d6e3;margin-bottom:25px;'>Silakan masuk untuk melanjutkan</p>", unsafe_allow_html=True)

username = st.text_input("ID Pengguna", placeholder="Masukkan ID Pengguna")
password = st.text_input("Kata Sandi", type="password", placeholder="Masukkan kata sandi")
role = st.selectbox("Sebagai", ["User", "Admin"])

login_btn = st.button("Masuk", key="login_btn")

if login_btn:
    if username and password:
        if role == "Admin":
            st.success("Login berhasil sebagai Admin ✅")
            st.session_state["page"] = "admin"
            st.switch_page("kasir_mas_ragil/admin_app.py")
        else:
            st.success("Login berhasil sebagai User ✅")
            st.session_state["page"] = "user"
            st.switch_page("kasir_mas_ragil/user_app.py")
    else:
        st.error("Harap isi semua kolom login!")

st.markdown("<p class='forgot'>Lupa password?</p>", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
