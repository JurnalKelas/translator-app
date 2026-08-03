import streamlit as st
import google.generativeai as genai
from PIL import Image
from gtts import gTTS
import os
import streamlit.components.v1 as components

# --- KONFIGURASI HALAMAN UTAMA ---
st.set_page_config(page_title="Kamus Pintar ALAZKA", page_icon="📖", layout="centered")

# --- INISIALISASI WARNA ---
if "warna_bg" not in st.session_state:
    st.session_state.warna_bg = "#F5EBE6"
if "warna_teks" not in st.session_state:
    st.session_state.warna_teks = "#2C221E"
if "peran" not in st.session_state:
    st.session_state.peran = None

# --- GAYA CSS ---
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

def tampilkan_header_logo():
    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:
        try: st.image(Image.open("logo1.png"), width=70)
        except: st.write("Logo 1")
    with col2:
        st.markdown("<h2 style='text-align: center; margin: 0;'>Kamus Pintar ALAZKA</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; margin: 0;'>Versi 2.0 (Sistem AI Baru)</p>", unsafe_allow_html=True)
    with col3:
        try: st.image(Image.open("logo2.png"), width=70)
        except: st.write("Logo 2")

# --- LOGIN ---
if st.session_state.peran is None:
    tampilkan_header_logo()
    st.write("---")
    sandi = st.text_input("Masukkan Kata Sandi:", type="password")
    if st.button("Masuk Aplikasi"):
        if sandi == "alazka123": st.session_state.peran = "siswa"; st.rerun()
        elif sandi == "alazka2026": st.session_state.peran = "admin"; st.rerun()
        elif sandi != "": st.error("Kunci salah!")
    st.stop()

# --- MENGHUBUNGKAN KE AI ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model_ai = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Sistem gagal membaca Kunci API: {e}")
    st.stop()

@st.cache_data(ttl=86400, show_spinner=False)
def memori_terjemahan_ai(perintah_teks):
    hasil = model_ai.generate_content(perintah_teks)
    return hasil.text.strip().replace('"', '').replace("'", "")

# --- HALAMAN SISWA ---
if st.session_state.peran == "siswa":
    tampilkan_header_logo()
    
    tab_teks, tab_kamera, tab_baca_foto = st.tabs(["✍️ Teks", "📷 Deteksi Benda", "📄 Baca Tulisan"])
    
    with tab_teks:
        pilihan_bahasa = st.radio("Mode:", ("🇮🇩 Indonesia ➡️ 🇬🇧 Inggris", "🇬🇧 Inggris ➡️ 🇮🇩 Indonesia"), horizontal=True)
        teks_siswa = st.text_area("Ketik teks di sini:")
        
        if st.button("Terjemahkan Teks ✨"):
            if teks_siswa:
                with st.spinner("Menerjemahkan..."):
                    try:
                        perintah = f"Translate to English: {teks_siswa}" if "Inggris" in pilihan_bahasa else f"Translate to Indonesian: {teks_siswa}"
                        hasil = memori_terjemahan_ai(perintah)
                        st.success("Hasil:"); st.write(hasil)
                        try:
                            tts = gTTS(text=hasil, lang='en' if "Inggris" in pilihan_bahasa else 'id', slow=False)
                            tts.save("suara.mp3"); st.audio("suara.mp3")
                        except: st.warning("Audio gagal dimuat.")
                    except Exception as e:
                        st.error(f"🚨 INFO ERROR BARU: {e}") # PESAN ERROR SUDAH SAYA GANTI TOTAL
            else:
                st.warning("Masukkan teks dulu.")

    with tab_kamera:
        gambar_unggah = st.file_uploader("Pilih foto benda (Galeri/Kamera)...", type=["jpg", "jpeg", "png"])
        if gambar_unggah and st.button("Tebak Benda ✨"):
            with st.spinner("Menebak benda..."):
                try:
                    gambar_buka = Image.open(gambar_unggah)
                    hasil_objek = model_ai.generate_content(["Identify the main object in this image and provide ONLY its name in Indonesian.", gambar_buka])
                    st.success("Tebakan:"); st.write(hasil_objek.text)
                except Exception as e:
                    st.error(f"🚨 INFO ERROR BARU: {e}")

    with tab_baca_foto:
        gambar_teks = st.file_uploader("Pilih foto tulisan/buku...", type=["jpg", "jpeg", "png"], key="baca_teks")
        if gambar_teks and st.button("Baca Tulisan ✨"):
            with st.spinner("Membaca dan Menerjemahkan..."):
                try:
                    gb = Image.open(gambar_teks)
                    hasil_baca = model_ai.generate_content(["Extract text from image and translate to Indonesian.", gb])
                    st.success("Hasil Pembacaan:"); st.write(hasil_baca.text)
                except Exception as e:
                    st.error(f"🚨 INFO ERROR BARU: {e}")

# --- KELUAR ---
st.write("---")
if st.button("Keluar (Logout)"):
    st.session_state.peran = None
    st.rerun()
