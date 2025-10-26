import streamlit as st

# Fungsi navbar sederhana dan elegan
def navbar():
    st.markdown(
        """
        <style>
        /* Navbar container */
        .navbar {
            display: flex;
            justify-content: center;
            background-color: #004c97;
            padding: 10px 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        /* Link style */
        .nav-link {
            color: white;
            text-decoration: none;
            margin: 0 20px;
            font-weight: 600;
            font-size: 18px;
            transition: color 0.3s;
        }
        /* Hover effect */
        .nav-link:hover {
            color: #ffd700;
        }
        </style>

        <div class="navbar">
            <a href="#" class="nav-link">Beranda</a>
            <a href="#" class="nav-link">Tentang</a>
            <a href="#" class="nav-link">Kelas</a>
            <a href="#" class="nav-link">Kontak</a>
        </div>
        """,
        unsafe_allow_html=True
    )

# Panggil navbar
navbar()

# Konten halaman utama
st.title("Selamat Datang di LMS Institut Widya Pratama")
st.write("Ini adalah contoh global navbar elegan tanpa logo, dibuat dengan Streamlit.")
