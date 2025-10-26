import streamlit as st

st.set_page_config(page_title="Login - Mie Ayam Bakso Mas Ragil", page_icon="🍜", layout="centered")

# Styling CSS agar mirip form login LMS
st.markdown("""
<style>
body {
    background-color: #faf8f5;
}
.login-box {
    background-color: #ffffff;
    padding: 2rem 3rem;
    border-radius: 12px;
    box-shadow: 0 0 15px rgba(0,0,0,0.1);
    width: 380px;
    margin: 60px auto;
    border-top: 5px solid #e67e22;
}
h2 {
    text-align: center;
    color: #d35400;
}
.subtext {
    text-align: center;
    font-size: 14px;
    color: #555;
}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- Tampilan utama ---
st.markdown("<div class='login-box'>", unsafe_allow_html=True)
st.markdown("<h2>🍜 Mie Ayam Bakso Mas Ragil</h2>", unsafe_allow_html=True)
st.markdown("<p class='subtext'>Silakan login untuk melanjutkan</p>", unsafe_allow_html=True)
st.markdown("---", unsafe_allow_html=True)

# Form login
with st.form("login_form"):
    username = st.text_input("ID Pengguna")
    password = st.text_input("Password", type="password")
    role = st.selectbox("Masuk Sebagai", ["Pelanggan", "Admin"])
    submitted = st.form_submit_button("Masuk")

    if submitted:
        if role == "Admin" and username == "admin" and password == "123":
            st.success("Login berhasil sebagai Admin!")
        elif role == "Pelanggan" and username == "user" and password == "123":
            st.success("Login berhasil sebagai Pelanggan!")
        else:
            st.error("ID pengguna atau password salah.")

st.markdown("""
<p style='text-align:center;'>
    <a href='#' style='color:#e67e22;'>Lupa password?</a>
</p>
""", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)
