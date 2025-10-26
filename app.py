import streamlit as st

st.set_page_config(page_title="Mie Ayam Bakso Mas Ragil", page_icon="🍜", layout="centered")

# ===== CUSTOM CSS =====
st.markdown("""
<style>
body {
    background: url('') no-repeat center center fixed;
    background-size: cover;
    font-family: 'Poppins', sans-serif;
}
.overlay {
    background: rgba(0, 0, 0, 0.6);
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    z-index: 0;
}
.login-card {
    position: relative;
    z-index: 1;
    max-width: 400px;
    margin: 5rem auto;
    padding: 3rem 2rem 2rem 2rem;
    background: rgba(255, 183, 77, 0.18);
    backdrop-filter: blur(14px);
    border-radius: 25px;
    box-shadow: 0 0 25px rgba(255, 150, 0, 0.3);
    text-align: center;
    color: #fff;
    overflow: hidden;
}

/* ======= Header Tengah ======= */
.header {
    margin-bottom: 1.5rem;
    background: linear-gradient(to right, rgba(255,200,80,0.25), rgba(255,180,50,0.08));
    border-radius: 14px;
    padding: 12px 0;
    animation: fadeIn 1.5s ease-in-out;
    box-shadow: 0 0 15px rgba(255,200,80,0.15);
}
.header h2 {
    font-weight: 700;
    color: #ffcc00;
    text-shadow: 0 0 15px rgba(255,200,50,0.6);
    margin: 0;
}
@keyframes fadeIn {
    from {opacity: 0; transform: translateY(-10px);}
    to {opacity: 1; transform: translateY(0);}
}

/* ======= Logo Animasi ======= */
.brand-logo {
    width: 90px;
    margin: 0 auto 15px auto;
    animation: float 3s ease-in-out infinite;
}
@keyframes float {
    0%,100% {transform: translateY(0);}
    50% {transform: translateY(-6px);}
}

/* ======= Input Style ======= */
.stTextInput>div>div>input {
    background-color: rgba(255,255,255,0.15) !important;
    color: white !important;
    border-radius: 10px !important;
    border: 1px solid rgba(255,255,255,0.3);
}
.stTextInput>label, .stSelectbox>label {
    color: #fff !important;
    font-weight: 500;
}
.stSelectbox div[data-baseweb="select"] > div {
    background-color: rgba(255,255,255,0.15);
    color: white;
    border-radius: 10px;
}

/* ======= Lupa Password ======= */
.forgot {
    text-align: right;
    font-size: 0.85rem;
    color: #ffdd57;
    margin-top: -8px;
    margin-bottom: 10px;
    cursor: pointer;
    transition: color 0.3s ease;
}
.forgot:hover {
    color: #ffe97d;
    text-decoration: underline;
}

/* ======= Tombol Masuk ======= */
.stButton>button {
    display: block;
    width: 100%;
    height: 45px;
    border-radius: 12px;
    border: none;
    background: linear-gradient(270deg, #ff6b00, #ffb300);
    background-size: 200% 200%;
    color: white;
    font-size: 1.05rem;
    font-weight: 700;
    letter-spacing: 1px;
    text-shadow: 0 0 6px rgba(255,255,255,0.3);
    box-shadow: 0 4px 10px rgba(255,140,0,0.4);
    transition: all 0.4s ease;
    cursor: pointer;
    margin-top: 0.6rem;
}
.stButton>button:hover {
    background-position: right center;
    transform: translateY(-2px) scale(1.02);
    box-shadow: 0 6px 16px rgba(255,180,0,0.6);
}
.stButton>button:active {
    transform: scale(0.98);
    box-shadow: 0 2px 8px rgba(255,140,0,0.3);
}

/* ======= Sosmed ======= */
.alt {
    margin-top: 1.5rem;
    color: #ccc;
    font-size: 0.9rem;
    text-align: center;
}
.social-icons {
    display: flex;
    justify-content: center;
    gap: 20px;
    margin-top: 0.5rem;
}
.social-icons img {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    cursor: pointer;
    transition: transform 0.2s ease;
    background-color: rgba(255,255,255,0.2);
    padding: 4px;
}
.social-icons img:hover {
    transform: scale(1.15);
    background-color: rgba(255,255,255,0.35);
}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ===== UI =====
st.markdown("<div class='overlay'></div>", unsafe_allow_html=True)
st.markdown("<div class='login-card'>", unsafe_allow_html=True)

# Header di tengah & clean
st.markdown("""
<img src='https://cdn-icons-png.flaticon.com/512/3075/3075977.png' class='brand-logo'>
<div class='header'>
    <h2>Selamat Datang di<br>Mie Ayam Bakso Mas Ragil 🍜</h2>
</div>
""", unsafe_allow_html=True)

# Login form
role = st.selectbox("Masuk sebagai", ["Pelanggan", "Admin"])
username = st.text_input("Email / ID Pengguna")
password = st.text_input("Password", type="password")

st.markdown("<div class='forgot'>Lupa password?</div>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([0.07, 0.86, 0.07])
with col2:
    login = st.button("MASUK")

if login:
    if role == "Admin":
        if username == "admin" and password == "123":
            st.success("Login berhasil sebagai ADMIN 👑")
        else:
            st.error("ID atau password admin salah!")
    else:
        if username == "user" and password == "123":
            st.success("Login berhasil sebagai PELANGGAN 🍜")
        else:
            st.error("Email atau password pelanggan salah!")

# Sosial media
st.markdown("""
<div class='alt'>
    <p>Atau masuk dengan</p>
    <div class='social-icons'>
        <img src='https://cdn-icons-png.flaticon.com/512/281/281764.png' title='Google'>
        <img src='https://cdn-icons-png.flaticon.com/512/733/733547.png' title='Facebook'>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)
