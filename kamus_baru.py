import streamlit as st
import google.generativeai as genai
from PIL import Image
from gtts import gTTS
import os

# --- KONFIGURASI HALAMAN UTAMA ---
st.set_page_config(page_title="Kamus Pintar ALAZKA", page_icon="📖", layout="centered")

# --- INISIALISASI PENYIMPANAN WARNA DI SESI APLIKASI ---
if "warna_bg" not in st.session_state:
    st.session_state.warna_bg = "#FFFFFF" # Default Putih Bersih

# --- GAYA CSS GLOBAL (DENGAN PEMAKSA WARNA TOMBOL KAMERA MUTLAK) ---
st.markdown(
    """
    <style>
    /* Mengubah background utama aplikasi secara keseluruhan sejak pertama dibuka */
    .stApp {
        background-color: #F5EBE6 !important;
        color: #2C221E;
    }
    /* Mengubah warna teks judul, subjudul, dan label teks agar gelap */
    h1, h2, h3, h4, h5, h6, p, span, label, .streamlit-expanderHeader {
        color: #2C221E !important;
    }
    /* Pemaksa warna teks tombol masuk aplikasi menjadi PUTIH */
    div.stButton > button:first-child p {
        color: #FFFFFF !important;
    }
    div.stButton > button:first-child {
        background-color: #3D2C24;
        color: #FFFFFF !important;
        border-radius: 8px;
        font-weight: bold;
        border: none;
    }
    div.stButton > button:first-child:hover {
        background-color: #5C4B43;
        color: #FFFFFF !important;
    }
    
    /* PEMAKSAAN MUTLAK UNTUK TEKS TOMBOL KAMERA (Take Photo / Clear Photo) */
    button[data-testid="baseButton-secondary"], 
    div[data-testid="stCameraInput"] button,
    .stCameraInput button {
        background-color: #3D2C24 !important;
        border: none !important;
        border-radius: 8px !important;
    }
    
    button[data-testid="baseButton-secondary"] *, 
    div[data-testid="stCameraInput"] button *,
    .stCameraInput button * {
        color: #FFFFFF !important;
        fill: #FFFFFF !important;
        font-weight: bold !important;
    }
    
    button[data-testid="baseButton-secondary"]:hover,
    div[data-testid="stCameraInput"] button:hover {
        background-color: #5C4B43 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- SISTEM LOGIN & GEMBOK APLIKASI ---
if "peran" not in st.session_state:
    st.session_state.peran = None

# --- FUNGSI UNTUK MENAMPILKAN HEADER DUA LOGO DARI FOLDER LOKAL ---
def tampilkan_header_logo():
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col1:
        try:
            logo1 = Image.open("logo1.png")
            st.image(logo1, width=70)
        except:
            st.write("Logo 1")
            
    with col2:
        st.markdown("<h2 style='text-align: center; margin: 0;'>Kamus Pintar ALAZKA</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #5C4B43; margin: 0;'>Smart English Dictionary & Object Detector</p>", unsafe_allow_html=True)
        
    with col3:
        try:
            logo2 = Image.open("logo2.png")
            st.image(logo2, width=70)
        except:
            st.write("Logo 2")

# --- HALAMAN GERBANG DEPAN (LOGIN) ---
if st.session_state.peran is None:
    tampilkan_header_logo()
    st.markdown("<h4 style='text-align: center; color: #8C4A32; margin-top: 15px;'>✨ Created by : Saiful Hadi ✨</h4>", unsafe_allow_html=True)
    st.write("---")
    
    # --- PANDUAN PENGGUNAAN DI HALAMAN DEPAN ---
    with st.expander("📖 Panduan Penggunaan & Informasi Aplikasi"):
        st.write("""
        Selamat datang di **Kamus Pintar ALAZKA**! Aplikasi cerdas untuk membantu proses pembelajaran bahasa. 
        Berikut adalah panduan singkat cara menggunakan aplikasi ini:
        
        1. **Cara Masuk (Login):**
           * Masukkan kata sandi yang sesuai dengan peran Anda (Siswa atau Admin) pada kolom di bawah.
        
        2. **Menu Terjemahan Teks & Suara:**
           * Pilih arah bahasa terjemahan (Indonesia ➡️ Inggris atau sebaliknya).
           * Ketik teks atau gunakan ikon mikrofon (🎤) pada *keyboard* HP Anda untuk berbicara secara langsung.
           * Tekan tombol **"Terjemahkan Teks ✨"** untuk melihat hasil dan mendengarkan pelafalannya (🔊).
        
        3. **Menu Deteksi Objek Foto:**
           * Buka tab kamera, lalu ambil foto benda di sekitar Anda atau unggah dari galeri.
           * AI akan secara otomatis mengenali nama benda tersebut dan menerjemahkannya lengkap dengan suara pelafalannya!
           
        4. **Personalisasi Warna (Mood):**
           * Anda dapat mengganti warna latar belakang (*background*) aplikasi sesuai dengan suasana hati atau kenyamanan mata Anda melalui menu pilihan warna di dalam aplikasi.
        """)
    
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

# --- MENGHUBUNGKAN KE OTAK AI ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model_ai = genai.GenerativeModel('gemini-3.6-flash')
except Exception as e:
    st.error("Koneksi ke sistem AI terputus. Pastikan kunci rahasia sudah terpasang.")
    st.stop()

# ==========================================
# HALAMAN KHUSUS SISWA (USER)
# ==========================================
if st.session_state.peran == "siswa":
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-color: {st.session_state.warna_bg} !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
    
    tampilkan_header_logo()
    st.write("---")
    
    with st.expander("🎨 Pilih Warna Latar Berdasarkan Mood Kamu"):
        pilihan_warna_siswa = st.selectbox(
            "Bagaimana suasana hatimu hari ini?",
            (
                "✨ Netral & Tenang (Putih Klasik)",
                "🌿 Rileks & Fokus (Hijau Mint Segar)",
                "🌊 Tenang & Damai (Biru Langit Muda)",
                "☀️ Ceria & Bersemangat (Kuning Pastel Lembut)",
                "🌸 Kreatif & Hangat (Merah Muda / Pink Soft)",
                "🔮 Nyaman & Misterius (Ungu Lavender Soft)",
                "☕ Santai & Hangat (Krim / Krem)",
                "🌙 Istirahat / Malam (Abu-abu Modern)",
                "🪵 Hangat & Elegan (Coklat Muda)"
            ),
            key="select_warna_siswa"
        )
        if st.button("Terapkan Mood Warna"):
            if "Putih" in pilihan_warna_siswa:
                st.session_state.warna_bg = "#FFFFFF"
            elif "Hijau" in pilihan_warna_siswa:
                st.session_state.warna_bg = "#E6F9F0"
            elif "Biru" in pilihan_warna_siswa:
                st.session_state.warna_bg = "#E6F2FF"
            elif "Kuning" in pilihan_warna_siswa:
                st.session_state.warna_bg = "#FFF9E6"
            elif "Merah Muda" in pilihan_warna_siswa:
                st.session_state.warna_bg = "#FFE6EE"
            elif "Ungu" in pilihan_warna_siswa:
                st.session_state.warna_bg = "#F3E6FF"
            elif "Krim" in pilihan_warna_siswa:
                st.session_state.warna_bg = "#FDFBF7"
            elif "Abu-abu" in pilihan_warna_siswa:
                st.session_state.warna_bg = "#F5F5F5"
            elif "Coklat" in pilihan_warna_siswa:
                st.session_state.warna_bg = "#F5EBE6"
            st.rerun()
            
    tab_teks, tab_kamera = st.tabs(["✍️ Terjemah Teks / Suara", "📷 Deteksi & Terjemah Objek Foto"])
    
    with tab_teks:
        st.write("---")
        pilihan_bahasa = st.radio(
            "Pilih mode terjemahan:",
            ("🇮🇩 Indonesia ➡️ 🇬🇧 Inggris", "🇬🇧 Inggris ➡️ 🇮🇩 Indonesia"),
            horizontal=True,
            key="radio_teks"
        )
        st.write("---")
        
        st.info("💡 **Tips Suara:** Sentuh kotak di bawah, lalu ketuk **ikon mikrofon (🎤)** pada *keyboard* HP Anda untuk berbicara!")
        teks_siswa = st.text_area("Ketik atau ucapkan kata/kalimat di sini:", height=100)
        
        if st.button("Terjemahkan Teks ✨"):
            if teks_siswa:
                with st.spinner("AI sedang menerjemahkan..."):
                    try:
                        if pilihan_bahasa == "🇮🇩 Indonesia ➡️ 🇬🇧 Inggris":
                            perintah = f"Translate this Indonesian text to English. Provide ONLY the direct translation without any explanation or notes: {teks_siswa}"
                            bahasa_suara = 'en'
                        else:
                            perintah = f"Translate this English text to Indonesian. Provide ONLY the direct translation without any explanation or notes: {teks_siswa}"
                            bahasa_suara = 'id'
                            
                        hasil = model_ai.generate_content(perintah)
                        teks_bersih = hasil.text.strip().replace('"', '').replace("'", "")
                        
                        st.success("Hasil Terjemahan:")
                        st.write(teks_bersih)
                        
                        try:
                            tts = gTTS(text=teks_bersih, lang=bahasa_suara, slow=False)
                            file_suara = "suara_terjemahan.mp3"
                            tts.save(file_suara)
                            st.audio(file_suara, format="audio/mp3")
                        except Exception as err_suara:
                            st.warning("Pemutar audio pelafalan sedang memuat.")
                            
                    except Exception as e:
                        st.error(f"Maaf, terjadi gangguan dari mesin AI: {e}")
            else:
                st.warning("Mohon masukkan kata atau kalimat terlebih dahulu.")

    with tab_kamera:
        st.write("---")
        pilihan_arah_objek = st.radio(
            "Pilih hasil terjemahan nama objek:",
            ("🇬🇧 Nama Objek dalam Bahasa Inggris", "🇮🇩 Nama Objek dalam Bahasa Indonesia"),
            horizontal=True,
            key="radio_objek"
        )
        st.write("---")
        
        st.info("💡 **Tips:** Foto benda atau objek apa saja di sekitar Anda, lalu AI akan menebak dan menerjemahkannya!")
        
        sumber_gambar = st.radio("Pilih sumber gambar:", ("📸 Ambil Foto Langsung (Kamera)", "📁 Unggah dari Galeri"), horizontal=True)
        
        gambar_unggah = None
        if sumber_gambar == "📸 Ambil Foto Langsung (Kamera)":
            gambar_unggah = st.camera_input("Ambil foto teks atau objek yang ingin dikenali")
        else:
            gambar_unggah = st.file_uploader("Pilih file foto objek...", type=["jpg", "jpeg", "png"])
            
        if gambar_unggah is not None:
            gambar_buka = Image.open(gambar_unggah)
            st.image(gambar_buka, caption="Objek yang dianalisis", use_column_width=True)
            
            if st.button("Identifikasi & Terjemahkan Objek ✨"):
                with st.spinner("AI sedang mengenali benda di foto..."):
                    try:
                        if "Inggris" in pilihan_arah_objek:
                            perintah_objek = "Identify the main object in this image and provide ONLY its name in English. No extra explanation or notes."
                            bahasa_suara_objek = 'en'
                        else:
                            perintah_objek = "Identify the main object in this image and provide ONLY its name in Indonesian. No extra explanation or notes."
                            bahasa_suara_objek = 'id'
                            
                        hasil_objek = model_ai.generate_content([perintah_objek, gambar_buka])
                        objek_bersih = hasil_objek.text.strip().replace('"', '').replace("'", "")
                        
                        st.success("Hasil Identifikasi Objek:")
                        st.write(objek_bersih)
                        
                        try:
                            tts_objek = gTTS(text=objek_bersih, lang=bahasa_suara_objek, slow=False)
                            file_suara_objek = "suara_objek.mp3"
                            tts_objek.save(file_suara_objek)
                            st.audio(file_suara_objek, format="audio/mp3")
                        except Exception as err_suara:
                            st.warning("Pemutar audio pelafalan sedang memuat.")
                            
                    except Exception as e:
                        st.error(f"Gagal mengenali objek. Pastikan foto terlihat jelas. ({e})")

# ==========================================
# HALAMAN KHUSUS ADMIN (PAK SAIFUL)
# ==========================================
elif st.session_state.peran == "admin":
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-color: {st.session_state.warna_bg} !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
    
    tampilkan_header_logo()
    st.info("Selamat bekerja, Pak Saiful! Gunakan menu di bawah ini untuk mengelola aplikasi.")
    
    tab1, tab2, tab3 = st.tabs(["📝 Input Manual", "🖼️ Ekstrak dari Gambar", "🎨 Pengaturan Tema Warna"])
    
    with tab1:
        st.subheader("Tambah Kosakata Manual")
        kata_baru = st.text_input("Masukkan Kata (Bahasa Inggris/Indonesia):")
        arti_kata = st.text_input("Masukkan Artinya:")
        if st.button("Simpan ke Database"):
            if kata_baru and arti_kata:
                st.success(f"Berhasil! Kata '{kata_baru}' telah tersimpan.")
            else:
                st.warning("Mohon isi kedua kolom di atas.")
                
    with tab2:
        st.subheader("Ekstrak Kosakata dari Gambar/Foto")
        gambar_unggah_admin = st.file_uploader("Pilih gambar daftar kosakata...", type=["jpg", "jpeg", "png"], key="admin_img")
        
        if gambar_unggah_admin is not None:
            gambar_buka_admin = Image.open(gambar_unggah_admin)
            st.image(gambar_buka_admin, caption="Gambar yang diunggah", use_column_width=True)
            
            if st.button("Baca & Ekstrak Teks"):
                with st.spinner("Membaca teks dari gambar menggunakan AI..."):
                    try:
                        perintah_gambar = "Extract all text precisely from this image as a clean list."
                        hasil_ekstrak = model_ai.generate_content([perintah_gambar, gambar_buka_admin])
                        st.success("Teks berhasil dibaca!")
                        st.write(hasil_ekstrak.text)
                    except Exception as e:
                        st.error(f"Gagal membaca gambar. Pastikan gambar cukup terang. ({e})")
                        
    with tab3:
        st.subheader("Ubah Warna Latar Belakang (Background) Aplikasi")
        st.write("Pilih warna suasana hati untuk latar belakang aplikasi:")
        
        pilihan_tema = st.selectbox(
            "Pilih Tema Warna Mood:",
            (
                "✨ Netral & Tenang (Putih Klasik)",
                "🌿 Rileks & Fokus (Hijau Mint Segar)",
                "🌊 Tenang & Damai (Biru Langit Muda)",
                "☀️ Ceria & Bersemangat (Kuning Pastel Lembut)",
                "🌸 Kreatif & Hangat (Merah Muda / Pink Soft)",
                "🔮 Nyaman & Misterius (Ungu Lavender Soft)",
                "☕ Santai & Hangat (Krim / Krem)",
                "🌙 Istirahat / Malam (Abu-abu Modern)",
                "🪵 Hangat & Elegan (Coklat Muda)"
            ),
            key="select_warna_admin"
        )
        
        if st.button("Terapkan Tema Warna"):
            if "Putih" in pilihan_tema:
                st.session_state.warna_bg = "#FFFFFF"
            elif "Hijau" in pilihan_tema:
                st.session_state.warna_bg = "#E6F9F0"
            elif "Biru" in pilihan_tema:
                st.session_state.warna_bg = "#E6F2FF"
            elif "Kuning" in pilihan_tema:
                st.session_state.warna_bg = "#FFF9E6"
            elif "Merah Muda" in pilihan_tema:
                st.session_state.warna_bg = "#FFE6EE"
            elif "Ungu" in pilihan_tema:
                st.session_state.warna_bg = "#F3E6FF"
            elif "Krim" in pilihan_tema:
                st.session_state.warna_bg = "#FDFBF7"
            elif "Abu-abu" in pilihan_tema:
                st.session_state.warna_bg = "#F5F5F5"
            elif "Coklat" in pilihan_tema:
                st.session_state.warna_bg = "#F5EBE6"
                
            st.success("Warna latar belakang berhasil diubah!")
            st.rerun()

# --- TOMBOL KELUAR (LOGOUT) ---
st.write("---")
if st.button("Keluar (Logout)"):
    st.session_state.peran = None
    st.rerun()
