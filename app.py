import streamlit as st

st.set_page_config(page_title="Rumah Makan Mas Ragil 🍜", page_icon="🍜", layout="centered")

# ====== CSS Custom Login Style ======
st.markdown("""
<style>
body {
    background: linear-gradient(180deg, #e9eff5, #f6f8fb);
}
.login-container {
    background: #ffffff;
    border-radius: 10px;
    padding: 30px 40px;
    width: 380px;
    margin: 100px auto;
    box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    text-align: center;
}
.logo {
    width: 80px;
    margin-bottom: 15px;
}
.title {
    font-weight: 700;
    color: #0b3d91;
    font-size: 20px;
}
.subtitle {
    color: #4b6584;
    font-size: 13px;
    margin-bottom: 25px;
}
.stTextInput > div > div > input {
    border-radius: 6px;
    border: 1px solid #ccc;
}
.stButton > button {
    background-color: #0b3d91;
    color: white;
    border-radius: 6px;
    padding: 6px 0;
    width: 100%;
    font-weight: 600;
    transition: 0.3s;
}
.stButton > button:hover {
    background-color: #1565c0;
    transform: scale(1.03);
}
.footer {
    font-size: 13px;
    margin-top: 10px;
}
.footer a {
    color: #1565c0;
    text-decoration: none;
}
.footer a:hover {
    text-decoration: underline;
}
</style>
""", unsafe_allow_html=True)

# ====== UI Login Box ======
st.markdown('<div class="login-container">', unsafe_allow_html=True)

st.image("https://upload.wikimedia.org/wikipedia/commons/3/3b/Logo_Institut_Widya_Pratama.png", width=80)
st.markdown('<div class="title">Rumah Makan Mas Ragil</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Sistem Pemesanan Digital</div>', unsafe_allow_html=True)

username = st.text_input("ID Pengguna")
password = st.text_input("Password", type="password")
role = st.selectbox("Sebagai", ["User", "Admin"])

if st.button("Masuk"):
    if username and password:
        if role == "Admin" and username == "admin" and password == "admin123":
            st.success("Login berhasil sebagai Admin.")
        else:
            st.success(f"Selamat datang, {username} ({role})!")
    else:
        st.error("Masukkan ID Pengguna dan Password.")

st.markdown('<div class="footer"><a href="#">Lupa password?</a></div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
