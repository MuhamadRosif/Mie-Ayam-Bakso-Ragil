import streamlit as st

st.set_page_config(page_title="Mie Ayam Bakso Mas Ragil", page_icon="🍜", layout="centered")

# ===== CUSTOM CSS =====
st.markdown("""
<style>
body {
    background: url('https://images.unsplash.com/photo-1606755962773-0e2d7efc4b5b') no-repeat center center fixed;
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
    margin: 7rem auto;
    padding: 2.5rem 2rem;
    background: rgba(255,255,255,0.1);
    backdrop-filter: blur(14px);
    border-radius: 25px;
    box-shadow: 0 0 25px rgba(0,0,0,0.3);
    text-align: center;
    color: #fff;
}
.brand-logo {
    width: 85px;
    margin-bottom: 10px;
}
.brand-name {
    font-weight: 700;
    font-size: 1.5rem;
    color: #ffcc00;
    margin-bottom: 1rem;
}
.subtitle {
    font-size: 0.9rem;
    color: #f1f1f1;
    margin-bottom: 2rem;
}

/* === INPUT FIELD === */
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

/* === LUPA PASSWORD === */
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

/* === BUTTON MASUK (Super Keren) === */
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

/* === SOSMED === */
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

# ===== LOGIN UI =====
st.markdown("<div class='overlay'></div>", unsafe_allow_html=True)
st.markdown("<div class='login-card'>", unsafe_allow_html=True)

st.markdown("<img src='https://cdn-icons-png.flaticon.com/512/3075/3075977.png' class='brand-logo'>", unsafe_allow_html=True)
st.markdown("<div class='brand-name'>Mie Ayam Bakso Mas Ragil</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Pilih peran dan masuk untuk mulai memesan 🍜</div>", unsafe_allow_html=True)

role = st.selectbox("Masuk sebagai", ["Pelanggan", "Admin"])
username = st.text_input("Email / ID Pengguna")
password = st.text_input("Password", type="password")

# ===== Lupa password link =====
st.markdown("<div class='forgot'>Lupa password?</div>", unsafe_allow_html=True)

# ===== Tombol masuk sejajar =====
col1, col2, col3 = st.columns([0.07, 0.86, 0.07])
with col2:
    login = st.button("MASUK")

# ===== LOGIC LOGIN =====
if login:
    if role == "Admin":
        if username == "admin" and password == "123":
            st.success("Login berhasil sebagai ADMIN 👑")
        else:
            st.error("ID atau password admin salah!")
    elif role == "Pelanggan":
        if username == "user" and password == "123":
            st.success("Login berhasil sebagai PELANGGAN 🍜")
        else:
            st.error("Email atau password pelanggan salah!")

# ===== SOSIAL MEDIA =====
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
