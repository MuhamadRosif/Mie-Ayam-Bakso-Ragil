import streamlit as st

st.set_page_config(page_title="Mie Ayam Bakso Mas Ragil", page_icon="🍜", layout="centered")

# ======== STYLE ==========
st.markdown("""
<style>
body {
    background: url('https://images.unsplash.com/photo-1565958011705-44e211f7d6a3') no-repeat center center fixed;
    background-size: cover;
}
.overlay {
    background-color: rgba(0, 0, 0, 0.65);
    width: 100%;
    height: 100vh;
    position: absolute;
    top: 0; left: 0;
    z-index: 0;
}
.login-box {
    position: relative;
    z-index: 1;
    margin: 6rem auto;
    padding: 2.5rem 2rem;
    width: 360px;
    background-color: rgba(20, 20, 20, 0.8);
    border-radius: 20px;
    box-shadow: 0 8px 25px rgba(0,0,0,0.3);
    text-align: center;
    color: white;
    font-family: 'Poppins', sans-serif;
}
.logo {
    font-size: 2.5rem;
    color: #ffcc00;
}
.app-title {
    font-weight: 700;
    font-size: 1.4rem;
    color: #ffcc00;
    margin-bottom: 1rem;
}
.btn-login {
    background-color: #35c759;
    border: none;
    color: white;
    font-size: 1rem;
    padding: 0.7rem;
    border-radius: 10px;
    width: 100%;
    margin-top: 10px;
}
.btn-daftar {
    background-color: white;
    color: #222;
    border: none;
    font-size: 1rem;
    padding: 0.7rem;
    border-radius: 10px;
    width: 100%;
    margin-top: 10px;
}
.social {
    margin-top: 1rem;
    color: #aaa;
}
.social img {
    width: 28px;
    margin: 0 8px;
}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ======== UI ==========
st.markdown("<div class='overlay'></div>", unsafe_allow_html=True)
st.markdown("<div class='login-box'>", unsafe_allow_html=True)
st.markdown("<div class='logo'>🍜</div>", unsafe_allow_html=True)
st.markdown("<div class='app-title'>Mie Ayam Bakso Mas Ragil</div>", unsafe_allow_html=True)

st.markdown("<p>Selamat datang! Silakan masuk untuk mulai memesan.</p>", unsafe_allow_html=True)

login_btn = st.button("MASUK", key="masuk")
register_btn = st.button("DAFTAR", key="daftar")

st.markdown("""
<div class='social'>
    <p>Masuk dengan</p>
    <img src='https://cdn-icons-png.flaticon.com/512/281/281764.png'>
    <img src='https://cdn-icons-png.flaticon.com/512/733/733547.png'>
</div>
""", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# ======== LOGIN LOGIC ==========
if login_btn:
    st.session_state["page"] = "menu"

if "page" in st.session_state and st.session_state["page"] == "menu":
    st.switch_page("kasir_mas_ragil/user_app.py")
