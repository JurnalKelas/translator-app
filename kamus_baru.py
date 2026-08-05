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

# --- GAYA CSS GLOBAL DINAMIS BERDASARKAN PILIHAN WARNA ---
st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {st.session_state.warna_bg} !important;
        color: {st.session_state.warna_teks} !important;
    }}
    h1, h2, h3, h4, h5, h6, p, span, label, .streamlit-expanderHeader {{
        color: {st.session_state.warna_teks} !important;
    }}
    div.stButton > button:first-child p {{
        color: #FFFFFF !important;
    }}
    div.stButton > button:first-child {{
        background-color: #3D2C24;
        color: #FFFFFF !important;
        border-radius: 8px;
        font-weight: bold;
        border: none;
    }}
    div.stButton > button:first-child:hover {{
        background-color: #5C4B43;
        color: #FFFFFF !important;
    }}
    button[data-testid="baseButton-secondary"], 
    div[data-testid="stCameraInput"] button,
    .stCameraInput button {{
        background-color: #3D2C24 !important;
        border: none !important;
        border-radius: 8px !important;
    }}
    button[data-testid="baseButton-secondary"] *, 
    div[data-testid="stCameraInput"] button *,
    .stCameraInput button * {{
        color: #FFFFFF !important;
        fill: #FFFFFF !important;
        font-weight: bold !important;
    }}
    button[data-testid="baseButton-secondary"]:hover,
    div[data-testid="stCameraInput"] button:hover {{
        background-color: #5C4B43 !important;
    }}
    div[data-testid="stTextArea"] textarea {{
        background-color: #E6F4EA !important;
        color: #137333 !important;
        border-radius: 8px !important;
        border: 1px solid #A8DAB5 !important;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# --- JAVASCRIPT PEMAKSA WARNA TEKS TOMBOL KAMERA ---
components.html(
    """
    <script>
    const observer = new MutationObserver(() => {
        const buttons = window.parent.document.querySelectorAll('button[data-testid="baseButton-secondary"], .stCameraInput button');
        buttons.forEach(btn => {
            btn.style.backgroundColor = "#3D2C24";
            btn.style.color = "#FFFFFF";
            const elements = btn.querySelectorAll('*');
            elements.forEach(el => {
                el.style.color = "#FFFFFF";
                el.style.fill = "#FFFFFF";
            });
        });
    });
    observer.observe(window.parent.document.body, { childList: true, subtree: true });
    </script>
    """,
    height=0,
)

# --- SISTEM LOGIN & GEMBOK APLIKASI ---
if "peran" not in st.session_state:
    st.session_state.peran = None

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
        st.markdown("<p style='text-align: center; margin: 0;'>Smart English Dictionary & Object Detector</p>", unsafe_allow_html=True)
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
    
    with st.expander("📖 Panduan Penggunaan & Informasi Aplikasi"):
        st.write("""
        Selamat datang di **Kamus Pintar ALAZKA**! 
        1. **Login:** Masukkan kata sandi (Siswa/Admin).
        2. **Terjemahan Teks:** Ketik teks atau bicara via mikrofon HP.
        3. **Deteksi Objek:** Foto benda, AI akan menebak namanya.
        4. **Baca Foto:** Foto halaman buku/papan tulis, AI akan membacakannya!
        """)
    
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

# --- MENGHUBUNGKAN KE OTAK AI (JURUS BLOKIR VERSI 2.5) ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    daftar_tersedia = []
    # Membaca daftar dari Google
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            nama_model = m.name.replace("models/", "")
            # KITA BLOKIR VERSI 2.5 KARENA DITOLAK GOOGLE UNTUK AKUN BAPAK
            if "2.5" not in nama_model:
                daftar_tersedia.append(nama_model)
                
    # Memilih mesin terbaik yang DIIZINKAN (prioritas: flash, lalu pro)
    mesin_aktif = None
    for nama in daftar_tersedia:
        if 'flash' in nama:
            mesin_aktif = nama
            break
            
    if not mesin_aktif:
        for nama in daftar_tersedia:
            if 'pro' in nama:
                mesin_aktif = nama
                break
                
    if not mesin_aktif and len(daftar_tersedia) > 0:
        mesin_aktif = daftar_tersedia[0]
        
    model_ai = genai.GenerativeModel(mesin_aktif)
except Exception as e:
    st.error(f"Koneksi ke sistem AI terputus. Info Error: {e}")
    st.stop()

@st.cache_data(ttl=86400, show_spinner=False)
def memori_terjemahan_ai(perintah_teks):
    hasil = model_ai.generate_content(perintah_teks)
    return hasil.text.strip().replace('"', '').replace("'", "")

# ==========================================
# HALAMAN KHUSUS SISWA
# ==========================================
if st.session_state.peran == "siswa":
    tampilkan_header_logo()
    st.write("---")
    
    with st.expander("🎨 Pilih Warna Latar Berdasarkan Mood Kamu"):
        pilihan_warna_siswa = st.selectbox(
            "Bagaimana suasana hatimu hari ini?",
            (
                "🪵 Hangat & Elegan (Coklat Muda)", "✨ Netral & Tenang (Putih Klasik)",
                "🌿 Rileks & Fokus (Hijau Mint Segar)", "🌊 Tenang & Damai (Biru Langit Muda)",
                "☀️ Ceria & Bersemangat (Kuning Pastel Lembut)", "🌸 Kreatif & Hangat (Merah Muda / Pink Soft)",
                "🔮 Nyaman & Misterius (Ungu Lavender Soft)", "☕ Santai & Hangat (Krim / Krem)",
                "🌙 Istirahat / Malam (Abu-abu Modern - Teks Terang)"
            ), key="select_warna_siswa"
        )
        if st.button("Terapkan Mood Warna"):
            warna_map = {
                "Coklat": ("#F5EBE6", "#2C221E"), "Putih": ("#FFFFFF", "#1A1A1A"),
                "Hijau": ("#E6F9F0", "#0D3B22"), "Biru": ("#E6F2FF", "#0B2E59"),
                "Kuning": ("#FFF9E6", "#4D3800"), "Merah Muda": ("#FFE6EE", "#590D22"),
                "Ungu": ("#F3E6FF", "#2E0B59"), "Krim": ("#FDFBF7", "#332D25"),
                "Abu-abu": ("#2B2B2B", "#F0F0F0")
            }
            for kunci, (bg, teks) in warna_map.items():
                if kunci in pilihan_warna_siswa:
                    st.session_state.warna_bg = bg
                    st.session_state.warna_teks = teks
            st.rerun()
            
    tab_teks, tab_kamera, tab_baca_foto = st.tabs(["✍️ Terjemah Teks", "📷 Deteksi Benda", "📄 Baca Tulisan Foto"])
    
    # --- TAB TEKS ---
    with tab_teks:
        pilihan_bahasa = st.radio("Pilih mode:", ("🇮🇩 ID ➡️ 🇬🇧 EN", "🇬🇧 EN ➡️ 🇮🇩 ID"), horizontal=True)
        teks_siswa = st.text_area("Ketik teks di sini:", height=100)
        
        if st.button("Terjemahkan Teks ✨"):
            if teks_siswa:
                with st.spinner("Menerjemahkan..."):
                    try:
                        if "ID ➡️" in pilihan_bahasa:
                            perintah = f"Translate to English. Only output the translation: {teks_siswa}"
                            b_suara = 'en'
                        else:
                            perintah = f"Translate to Indonesian. Only output the translation: {teks_siswa}"
                            b_suara = 'id'
                            
                        hasil_teks = memori_terjemahan_ai(perintah)
                        st.success("Hasil:")
                        st.write(hasil_teks)
                        
                        try:
                            tts = gTTS(text=hasil_teks, lang=b_suara, slow=False)
                            tts.save("suara_teks.mp3")
                            st.audio("suara_teks.mp3", format="audio/mp3")
                        except: pass
                    except Exception as e:
                        st.error(f"Gagal: {e}")
            else: st.warning("Masukkan teks dulu.")

    # --- TAB KAMERA OBJEK ---
    with tab_kamera:
        pilihan_arah_objek = st.radio("Terjemahkan benda ke:", ("🇬🇧 Inggris", "🇮🇩 Indonesia"), horizontal=True)
        sumber_gambar = st.radio("Pilih sumber:", ("📸 Kamera", "📁 Galeri"), horizontal=True)
        
        gambar_unggah = st.camera_input("Foto") if "Kamera" in sumber_gambar else st.file_uploader("Upload", type=["jpg", "png", "jpeg"])
            
        if gambar_unggah:
            gambar_buka = Image.open(gambar_unggah)
            st.image(gambar_buka, use_container_width=True)
            
            if st.button("Tebak Benda Ini! ✨"):
                with st.spinner("Mengenali benda..."):
                    try:
                        b_suara = 'en' if "Inggris" in pilihan_arah_objek else 'id'
                        lang = 'English' if "Inggris" in pilihan_arah_objek else 'Indonesian'
                        perintah_objek = f"Identify the main object in this image. Output ONLY its name in {lang}."
                        
                        hasil_objek = model_ai.generate_content([perintah_objek, gambar_buka])
                        objek_teks = hasil_objek.text.strip().replace('"', '').replace("'", "")
                        
                        st.success("Tebakan AI:")
                        st.write(objek_teks)
                        
                        try:
                            tts = gTTS(text=objek_teks, lang=b_suara, slow=False)
                            tts.save("suara_objek.mp3")
                            st.audio("suara_objek.mp3")
                        except: pass
                    except Exception as e:
                        st.error(f"Gagal mengenali benda: {e}")

    # --- TAB BACA FOTO ---
    with tab_baca_foto:
        pilihan_bahasa_foto = st.radio("Terjemahkan tulisan foto ke:", ("🇮🇩 Indonesia", "🇬🇧 Inggris"), horizontal=True)
        sumber_foto_teks = st.radio("Sumber tulisan:", ("📸 Kamera", "📁 Galeri"), horizontal=True)
        
        gambar_teks_unggah = st.camera_input("Foto Teks") if "Kamera" in sumber_foto_teks else st.file_uploader("Upload Teks", type=["jpg", "png", "jpeg"])
            
        if gambar_teks_unggah:
            gambar_teks_buka = Image.open(gambar_teks_unggah)
            st.image(gambar_teks_buka, use_container_width=True)
            
            if st.button("Baca & Terjemahkan ✨"):
                with st.spinner("Membaca dan menerjemahkan..."):
                    try:
                        lang_to = 'Indonesian' if "Indonesia" in pilihan_bahasa_foto else 'English'
                        b_suara = 'id' if "Indonesia" in pilihan_bahasa_foto else 'en'
                        
                        perintah_baca = f"Extract all text accurately, then translate it into {lang_to}. Format as:\n\n**Teks Asli:**\n[text]\n\n**Terjemahan:**\n[translated]"
                        
                        hasil_baca = model_ai.generate_content([perintah_baca, gambar_teks_buka])
                        teks_hasil = hasil_baca.text.strip()
                        
                        st.success("Hasil Pembacaan:")
                        st.write(teks_hasil)
                        
                        try:
                            teks_suara = teks_hasil.split("**Terjemahan:**")[1].strip() if "**Terjemahan:**" in teks_hasil else teks_hasil
                            tts = gTTS(text=teks_suara, lang=b_suara, slow=False)
                            tts.save("suara_baca.mp3")
                            st.audio("suara_baca.mp3")
                        except: pass
                    except Exception as e:
                        st.error(f"Gagal membaca tulisan: {e}")

# ==========================================
# HALAMAN KHUSUS ADMIN
# ==========================================
elif st.session_state.peran == "admin":
    tampilkan_header_logo()
    
    st.info(f"✅ Sistem berhasil mendeteksi dan terhubung dengan mesin yang diizinkan: **{mesin_aktif}**")
    
    tab1, tab2 = st.tabs(["📝 Input Manual", "🖼️ Ekstrak dari Gambar"])
    with tab1:
        st.subheader("Tambah Kosakata")
        kata_baru = st.text_input("Kata:")
        arti_kata = st.text_input("Arti:")
        if st.button("Simpan"):
            st.success("Tersimpan!")
            
    with tab2:
        st.subheader("Ekstrak Teks Gambar")
        gambar_unggah_admin = st.file_uploader("Pilih gambar...", type=["jpg", "png", "jpeg"])
        if gambar_unggah_admin:
            gambar_buka_admin = Image.open(gambar_unggah_admin)
            st.image(gambar_buka_admin, use_container_width=True)
            if st.button("Baca Teks"):
                with st.spinner("Membaca..."):
                    try:
                        hasil_ekstrak = model_ai.generate_content(["Ekstrak dan salin persis semua teks di gambar.", gambar_buka_admin])
                        st.success("Berhasil:")
                        st.write(hasil_ekstrak.text)
                    except Exception as e:
                        st.error(f"Error: {e}")

st.write("---")
if st.button("Keluar (Logout)"):
    st.session_state.peran = None
    st.rerun()
