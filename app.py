import streamlit as st

st.set_page_config(page_title="Login - Mie Ayam Bakso Mas Ragil", page_icon="🍜", layout="centered")

# ======== STYLE ==========
st.markdown("""
<style>
body {
    background-color: #00291b;
}
.login-card {
    background-color: #00422d;
    width: 350px;
    margin: 5rem auto;
    padding: 2.5rem 2rem;
    border-radius: 25px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.4);
    color: white;
    text-align: center;
    font-family: 'Poppins', sans-serif;
}
.logo {
    font-size: 2.5rem;
    margin-bottom: 10px;
}
.app-title {
    font-weight: 700;
    font-size: 1.4rem;
    color: #fff;
}
.subtitle {
    color: #f0f0f0;
    font-size: 0.9rem;
    margin-bottom: 2rem;
}
input, .stTextInput>div>div>input {
    background-color: #005c3c !important;
    color: white !important;
    border-radius: 8px !important;
}
.stTextInput>label {
    color: #fff !important;
    font-weight: 500;
}
.stCheckbox>label {
    color: #fff !important;
}
.stButton>button {
    background-color: #ff7a00;
    color: white;
    border: none;
    padding: 0.7rem;
    border-radius: 10px;
    font-size: 1rem;
    width: 100%;
    margin-top: 10px;
}
.stButton>button:hover {
    background-color: #e66b00;
}
.forgot {
    text-align: right;
    font-size: 0.85rem;
    margin-top: -10px;
    margin-bottom: 20px;
}
.forgot a {
    color: #ff7a00;
    text-decoration: none;
}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ======== LOGIN FORM ==========
st.markdown("<div class='login-card'>", unsafe_allow_html=True)
st.markdown("<div class='logo'>🍜</div>", unsafe_allow_html=True)
st.markdown("<div class='app-title'>Mie Ayam Bakso Mas Ragil</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Silakan login untuk memesan menu favoritmu</div>", unsafe_allow_html=True)

username = st.text_input("Email / ID Pengguna")
password = st.text_input("Password", type="password")

col1, col2 = st.columns([1, 1])
with col1:
    remember = st.checkbox("Remember Me")
with col2:
    st.markdown("<div class='forgot'><a href='#'>Forgot?</a></div>", unsafe_allow_html=True)

login = st.button("Login")

if login:
    if username == "user" and password == "123":
        st.success("Login berhasil! Selamat datang di Mie Ayam Bakso Mas Ragil 🍜")
        st.session_state["logged_in"] = True
    else:
        st.error("Email atau password salah!")

st.markdown("</div>", unsafe_allow_html=True)

# Setelah login nanti akan diarahkan ke halaman menu
if "logged_in" in st.session_state and st.session_state["logged_in"]:
    st.switch_page("kasir_mas_ragil/user_app.py")
