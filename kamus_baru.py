import streamlit as st
import google.generativeai as genai
from PIL import Image
from gtts import gTTS
import os
import streamlit.components.v1 as components

# --- KONFIGURASI HALAMAN UTAMA ---
st.set_page_config(page_title="Kamus Pintar ALAZKA", page_icon="📖", layout="centered")

# --- INISIALISASI PENYIMPANAN WARNA DI SESI APLIKASI ---
if "warna_bg" not in st.session_state:
    st.session_state.warna_bg = "#F5EBE6"

if "warna_teks" not in st.session_state:
    st.session_state.warna_teks = "#2C221E"

# --- GAYA CSS GLOBAL ---
st.markdown(
    f"""
    <style>
    .stApp {{ background-color: {st.session_state.warna_bg} !important; color: {st.session_state.warna_teks} !important; }}
    h1, h2, h3, h4, h5, h6, p, span, label, .streamlit-expanderHeader {{ color: {st.session_state.warna_teks} !important; }}
    div.stButton > button:first-child p {{ color: #FFFFFF !important; }}
    div.stButton > button:first-child {{ background-color: #3D2C24; color: #FFFFFF !important; border-radius: 8px; font-weight: bold; border: none; }}
    div.stButton > button:first-child:hover {{ background-color: #5C4B43; color: #FFFFFF !important; }}
    button[data-testid="baseButton-secondary"], div[data-testid="stCameraInput"] button, .stCameraInput button {{ background-color: #3D2C24 !important; border: none !important; border-radius: 8px !important; }}
    button[data-testid="baseButton-secondary"] *, div[data-testid="stCameraInput"] button *, .stCameraInput button * {{ color: #FFFFFF !important; fill: #FFFFFF !important; font-weight: bold !important; }}
    button[data-testid="baseButton-secondary"]:hover, div[data-testid="stCameraInput"] button:hover {{ background-color: #5C4B43 !important; }}
    div[data-testid="stTextArea"] textarea {{ background-color: #E6F4EA !important; color: #137333 !important; border-radius: 8px !important; border: 1px solid #A8DAB5 !important; }}
    </style>
    """, unsafe_allow_html=True
)

components.html(
    """
    <script>
    const observer = new MutationObserver(() => {
        const buttons = window.parent.document.querySelectorAll('button[data-testid="baseButton-secondary"], .stCameraInput button');
        buttons.forEach(btn => {
            btn.style.backgroundColor = "#3D2C24";
            btn.style.color = "#FFFFFF";
            const elements = btn.querySelectorAll('*');
            elements.forEach(el => { el.style.color = "#FFFFFF"; el.style.fill = "#FFFFFF"; });
        });
    });
    observer.observe(window.parent.document.body, { childList: true, subtree: true });
    </script>
    """, height=0,
)

if "peran" not in st.session_state:
    st.session_state.peran = None

def tampilkan_header_logo():
    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:
        try: st.image(Image.open("logo1.png"), width=70)
        except: st.write("Logo 1")
    with col2:
        st.markdown("<h2 style='text-align: center; margin: 0;'>Kamus Pintar ALAZKA</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; margin: 0;'>Smart English Dictionary & Object Detector</p>", unsafe_allow_html=True)
    with col3:
        try: st.image(Image.open("logo2.png"), width=70)
        except: st.write("Logo 2")

if st.session_state.peran is None:
    tampilkan_header_logo()
    st.markdown("<h4 style='text-align: center; color: #8C4A32; margin-top: 15px;'>✨ Created by : Saiful Hadi ✨</h4>", unsafe_allow_html=True)
    st.write("---")
    sandi = st.text_input("Silakan Masukkan Kata Sandi:", type="password")
    if st.button("Masuk Aplikasi"):
        if sandi == "alazka123":
            st.session_state.peran = "siswa"
            st.rerun()
        elif sandi == "alazka2026":
            st.session_state.peran = "admin"
            st.rerun()
        elif sandi != "":
            st.error("Kunci salah! Silakan coba lagi.")
    st.stop()

# --- BACA KUNCI API ---
kunci_rahasia = st.secrets["GEMINI_API_KEY"]

try:
    genai.configure(api_key=kunci_rahasia)
    model_ai = genai.GenerativeModel('gemini-3.6-flash')
except Exception as e:
    st.error("Koneksi ke sistem AI terputus. Pastikan kunci rahasia sudah terpasang.")
    st.stop()

@st.cache_data(ttl=86400, show_spinner=False)
def memori_terjemahan_ai(perintah_teks):
    hasil = model_ai.generate_content(perintah_teks)
    return hasil.text.strip().replace('"', '').replace("'", "")

if st.session_state.peran == "siswa":
    tampilkan_header_logo()
    st.write("---")
    
    tab_teks, tab_kamera = st.tabs(["✍️ Terjemah Teks / Suara", "📷 Deteksi & Terjemah Objek Foto"])
    
    with tab_teks:
        st.write("---")
        pilihan_bahasa = st.radio("Pilih mode terjemahan:", ("🇮🇩 Indonesia ➡️ 🇬🇧 Inggris", "🇬🇧 Inggris ➡️ 🇮🇩 Indonesia"), horizontal=True)
        st.write("---")
        
        teks_siswa = st.text_area("Ketik atau ucapkan kata/kalimat di sini:", height=100)
        
        if st.button("Terjemahkan Teks ✨"):
            if teks_siswa:
                with st.spinner("AI sedang menerjemahkan..."):
                    try:
                        perintah = f"Translate this Indonesian text to English. ONLY direct translation: {teks_siswa}" if "Inggris" in pilihan_bahasa else f"Translate this English text to Indonesian. ONLY direct translation: {teks_siswa}"
                        bahasa_suara = 'en' if "Inggris" in pilihan_bahasa else 'id'
                        
                        teks_bersih = memori_terjemahan_ai(perintah)
                        st.success("Hasil Terjemahan:")
                        st.write(teks_bersih)
                    except Exception as e:
                        pesan_error = str(e)
                        if "429" in pesan_error or "Quota" in pesan_error:
                            # MODE DETEKTIF: Menampilkan 12 huruf pertama dari kunci yang terbaca
                            st.warning(f"🕵️ Kunci yg sedang dibaca sistem: {kunci_rahasia[:12]}*** | Mesin masih error kuota.")
                        else:
                            st.error(f"Error: {e}")
            else:
                st.warning("Mohon masukkan kata.")

elif st.session_state.peran == "admin":
    tampilkan_header_logo()
    st.info("Mode Admin.")
    if st.button("Keluar (Logout)"):
        st.session_state.peran = None
        st.rerun()
