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

# --- JAVASCRIPT PEMAKSA WARNA TEKS TOMBOL KAMERA MENJADI PUTIH ---
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
        Selamat datang di **Kamus Pintar ALAZKA**! Aplikasi cerdas untuk membantu proses pembelajaran bahasa. 
        Berikut adalah panduan singkat cara menggunakan aplikasi ini:
        
        1. **Cara Masuk (Login):**
           * Masukkan kata sandi yang sesuai dengan peran Anda (Siswa atau Admin) pada kolom di bawah.
        
        2. **Menu Terjemahan Teks & Suara:**
           * Ketik teks atau gunakan mikrofon untuk berbicara.
        
        3. **Menu Deteksi Objek Foto:**
           * Buka tab kamera, ambil foto benda di sekitar Anda, dan AI akan menebak nama bendanya.
           
        4. **Menu Terjemah Tulisan dari Foto (BARU):**
           * Foto halaman buku paket atau tulisan di papan tulis, dan biarkan AI membacakan serta menerjemahkannya untuk Anda!
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

# --- MENGHUBUNGKAN KE OTAK AI (PENCARIAN OTOMATIS) ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    # AI akan mencari sendiri nama model terbarunya yang aktif
    model_pilihan = "gemini-1.5-flash"
    try:
        daftar_model = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        for m in daftar_model:
            if "1.5-flash" in m:
                model_pilihan = m.replace("models/", "")
                break
    except:
        pass # Gunakan default jika gagal mencari
        
    model_ai = genai.GenerativeModel(model_pilihan)
except Exception as e:
    st.error(f"Koneksi ke sistem AI terputus. Pastikan kunci rahasia sudah terpasang. ({e})")
    st.stop()

# ==========================================
# FUNGSI CACHE (PENGINGAT JAWABAN AI)
# ==========================================
@st.cache_data(ttl=86400, show_spinner=False)
def memori_terjemahan_ai(perintah_teks):
    hasil = model_ai.generate_content(perintah_teks)
    return hasil.text.strip().replace('"', '').replace("'", "")

# ==========================================
# HALAMAN KHUSUS SISWA (USER)
# ==========================================
if st.session_state.peran == "siswa":
    tampilkan_header_logo()
    st.write("---")
    
    with st.expander("🎨 Pilih Warna Latar Berdasarkan Mood Kamu"):
        pilihan_warna_siswa = st.selectbox(
            "Bagaimana suasana hatimu hari ini?",
            (
                "🪵 Hangat & Elegan (Coklat Muda)",
                "✨ Netral & Tenang (Putih Klasik)",
                "🌿 Rileks & Fokus (Hijau Mint Segar)",
                "🌊 Tenang & Damai (Biru Langit Muda)",
                "☀️ Ceria & Bersemangat (Kuning Pastel Lembut)",
                "🌸 Kreatif & Hangat (Merah Muda / Pink Soft)",
                "🔮 Nyaman & Misterius (Ungu Lavender Soft)",
                "☕ Santai & Hangat (Krim / Krem)",
                "🌙 Istirahat / Malam (Abu-abu Modern - Teks Terang)"
            ),
            key="select_warna_siswa"
        )
        if st.button("Terapkan Mood Warna"):
            if "Coklat" in pilihan_warna_siswa:
                st.session_state.warna_bg = "#F5EBE6"
                st.session_state.warna_teks = "#2C221E"
            elif "Putih" in pilihan_warna_siswa:
                st.session_state.warna_bg = "#FFFFFF"
                st.session_state.warna_teks = "#1A1A1A"
            elif "Hijau" in pilihan_warna_siswa:
                st.session_state.warna_bg = "#E6F9F0"
                st.session_state.warna_teks = "#0D3B22"
            elif "Biru" in pilihan_warna_siswa:
                st.session_state.warna_bg = "#E6F2FF"
                st.session_state.warna_teks = "#0B2E59"
            elif "Kuning" in pilihan_warna_siswa:
                st.session_state.warna_bg = "#FFF9E6"
                st.session_state.warna_teks = "#4D3800"
            elif "Merah Muda" in pilihan_warna_siswa:
                st.session_state.warna_bg = "#FFE6EE"
                st.session_state.warna_teks = "#590D22"
            elif "Ungu" in pilihan_warna_siswa:
                st.session_state.warna_bg = "#F3E6FF"
                st.session_state.warna_teks = "#2E0B59"
            elif "Krim" in pilihan_warna_siswa:
                st.session_state.warna_bg = "#FDFBF7"
                st.session_state.warna_teks = "#332D25"
            elif "Abu-abu" in pilihan_warna_siswa:
                st.session_state.warna_bg = "#2B2B2B"
                st.session_state.warna_teks = "#F0F0F0"
            st.rerun()
            
    tab_teks, tab_kamera, tab_baca_foto = st.tabs(["✍️ Terjemah Teks", "📷 Deteksi Benda", "📄 Baca Tulisan Foto"])
    
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
                            
                        teks_bersih = memori_terjemahan_ai(perintah)
                        st.success("Hasil Terjemahan:")
                        st.write(teks_bersih)
                        
                        try:
                            tts = gTTS(text=teks_bersih, lang=bahasa_suara, slow=False)
                            file_suara = "suara_terjemahan.mp3"
                            tts.save(file_suara)
                            st.audio(file_suara, format="audio/mp3")
                        except Exception:
                            st.warning("Pemutar audio pelafalan sedang memuat. Coba tekan tombol lagi.")
                            
                    except Exception as e:
                        pesan_error = str(e)
                        if "429" in pesan_error or "Quota" in pesan_error:
                            st.warning("⏳ Mesin AI sedang melayani banyak siswa. Mohon tunggu sekitar 5 detik, lalu tekan tombolnya lagi ya!")
                        else:
                            st.error(f"Maaf, terjadi gangguan dari mesin AI: {e}")
            else:
                st.warning("Mohon masukkan kata atau kalimat terlebih dahulu.")

    with tab_kamera:
        st.write("---")
        pilihan_arah_objek = st.radio(
            "Pilih hasil terjemahan nama objek benda:",
            ("🇬🇧 Nama Objek dalam Bahasa Inggris", "🇮🇩 Nama Objek dalam Bahasa Indonesia"),
            horizontal=True,
            key="radio_objek"
        )
        st.write("---")
        st.info("💡 **Tips:** Foto benda di sekitar Anda, lalu AI akan menebak nama benda tersebut!")
        
        sumber_gambar = st.radio("Pilih sumber gambar:", ("📸 Ambil Foto Langsung (Kamera)", "📁 Unggah dari Galeri"), horizontal=True, key="sumber_objek")
        
        gambar_unggah = None
        if sumber_gambar == "📸 Ambil Foto Langsung (Kamera)":
            gambar_unggah = st.camera_input("Ambil foto objek yang ingin dikenali", key="kamera_objek")
        else:
            gambar_unggah = st.file_uploader("Pilih file foto objek...", type=["jpg", "jpeg", "png"], key="upload_objek")
            
        if gambar_unggah is not None:
            gambar_buka = Image.open(gambar_unggah)
            st.image(gambar_buka, caption="Objek yang dianalisis", use_container_width=True)
            
            if st.button("Tebak Benda Ini! ✨"):
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
                        
                        st.success("Tebakan AI untuk Benda Ini:")
                        st.write(objek_bersih)
                        
                        try:
                            tts_objek = gTTS(text=objek_bersih, lang=bahasa_suara_objek, slow=False)
                            file_suara_objek = "suara_objek.mp3"
                            tts_objek.save(file_suara_objek)
                            st.audio(file_suara_objek, format="audio/mp3")
                        except Exception:
                            st.warning("Pemutar audio pelafalan sedang memuat.")
                            
                    except Exception as e:
                        st.error(f"Gagal mengenali objek. Pastikan foto terlihat jelas. ({e})")

    with tab_baca_foto:
        st.write("---")
        pilihan_bahasa_foto = st.radio(
            "Pilih bahasa untuk menerjemahkan tulisan:",
            ("🇮🇩 Buku Inggris ➡️ Terjemahkan ke Indonesia", "🇬🇧 Buku Indonesia ➡️ Terjemahkan ke Inggris"),
            horizontal=True,
            key="radio_foto_teks"
        )
        st.write("---")
        st.info("💡 **Tips:** Foto tulisan di buku pelajaran atau papan tulis, AI akan membacanya dan langsung menerjemahkannya!")
        
        sumber_foto_teks = st.radio("Pilih sumber foto:", ("📸 Ambil Foto Tulisan", "📁 Unggah dari Galeri"), horizontal=True, key="sumber_foto_teks")
        
        gambar_teks_unggah = None
        if sumber_foto_teks == "📸 Ambil Foto Tulisan":
            gambar_teks_unggah = st.camera_input("Ambil foto teks yang ingin dibaca", key="kamera_teks")
        else:
            gambar_teks_unggah = st.file_uploader("Pilih file foto tulisan...", type=["jpg", "jpeg", "png"], key="upload_teks")
            
        if gambar_teks_unggah is not None:
            gambar_teks_buka = Image.open(gambar_teks_unggah)
            st.image(gambar_teks_buka, caption="Foto tulisan yang akan dibaca", use_container_width=True)
            
            if st.button("Baca & Terjemahkan Tulisan ✨"):
                with st.spinner("AI sedang mengekstrak teks dari gambar dan menerjemahkannya..."):
                    try:
                        if "Indonesia" in pilihan_bahasa_foto: 
                            perintah_baca = "Extract all the text from this image accurately. Then, translate that text into Indonesian. Format your output EXACTLY like this:\n\n**Teks Asli (Inggris):**\n[insert extracted text here]\n\n**Terjemahan (Indonesia):**\n[insert translated text here]"
                            bahasa_suara_baca = 'id'
                            pemisah = "**Terjemahan (Indonesia):**"
                        else: 
                            perintah_baca = "Extract all the text from this image accurately. Then, translate that text into English. Format your output EXACTLY like this:\n\n**Teks Asli (Indonesia):**\n[insert extracted text here]\n\n**Terjemahan (Inggris):**\n[insert translated text here]"
                            bahasa_suara_baca = 'en'
                            pemisah = "**Terjemahan (Inggris):**"
                            
                        hasil_baca = model_ai.generate_content([perintah_baca, gambar_teks_buka])
                        teks_hasil_baca = hasil_baca.text.strip()
                        
                        st.success("Hasil Pembacaan Dokumen:")
                        st.write(teks_hasil_baca)
                        
                        try:
                            if pemisah in teks_hasil_baca:
                                teks_suara_saja = teks_hasil_baca.split(pemisah)[1].strip()
                            else:
                                teks_suara_saja = teks_hasil_baca
                                
                            tts_baca = gTTS(text=teks_suara_saja, lang=bahasa_suara_baca, slow=False)
                            file_suara_baca = "suara_baca.mp3"
                            tts_baca.save(file_suara_baca)
                            st.audio(file_suara_baca, format="audio/mp3")
                        except Exception:
                            st.warning("Pemutar audio pelafalan sedang memuat.")
                            
                    except Exception as e:
                        st.error(f"Gagal membaca tulisan. Pastikan tulisan di foto terlihat jelas. ({e})")

# ==========================================
# HALAMAN KHUSUS ADMIN (PAK SAIFUL)
# ==========================================
elif st.session_state.peran == "admin":
    tampilkan_header_logo()
    st.info("Selamat bekerja, Pak Saiful! Gunakan menu di bawah ini untuk mengelola aplikasi.")
    
    tab1, tab2, tab3 = st.tabs(["📝 Input Manual", "🖼️ Ekstrak dari Gambar", "🎨 Pengaturan Tema Warna"])
    
    with tab1:
        st.subheader("Tambah Kosakata Manual")
        kata_baru = st.text_input("Masukkan Kata (Bahasa Inggris/Indonesia):")
        arti_kata = st.text_input("Masukkan Artinya:")
        
        gambar_ilustrasi = st.file_uploader("Unggah Gambar Benda/Ilustrasi (Opsional):", type=["jpg", "jpeg", "png"])
        
        if st.button("Simpan ke Database"):
            if kata_baru and arti_kata:
                if gambar_ilustrasi is not None:
                    st.image(gambar_ilustrasi, caption=f"Ilustrasi untuk: {kata_baru}", width=250)
                    st.success(f"Berhasil! Kata '{kata_baru}' beserta gambarnya telah tersimpan.")
                else:
                    st.success(f"Berhasil! Kata '{kata_baru}' telah tersimpan (tanpa gambar).")
            else:
                st.warning("Mohon isi kedua kolom di atas.")
                
    with tab2:
        st.subheader("Ekstrak Kosakata dari Gambar/Foto")
        gambar_unggah_admin = st.file_uploader("Pilih gambar daftar kosakata...", type=["jpg", "jpeg", "png"], key="admin_img")
        
        if gambar_unggah_admin is not None:
            gambar_buka_admin = Image.open(gambar_unggah_admin)
            st.image(gambar_buka_admin, caption="Gambar yang diunggah", use_container_width=True)
            
            if st.button("Baca & Ekstrak Teks"):
                with st.spinner("Membaca teks dari gambar menggunakan AI..."):
                    try:
                        perintah_gambar = "Baca gambar ini dengan sangat teliti. Ekstrak dan salin persis semua teks yang terlihat di gambar. Jangan menambahkan kalimat penutup, jangan menerjemahkan, dan jangan mengarang kata-kata yang tidak ada di gambar. Susun hasilnya dalam bentuk daftar (list) yang rapi."
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
                "🪵 Hangat & Elegan (Coklat Muda)",
                "✨ Netral & Tenang (Putih Klasik)",
                "🌿 Rileks & Fokus (Hijau Mint Segar)",
                "🌊 Tenang & Damai (Biru Langit Muda)",
                "☀️ Ceria & Bersemangat (Kuning Pastel Lembut)",
                "🌸 Kreatif & Hangat (Merah Muda / Pink Soft)",
                "🔮 Nyaman & Misterius (Ungu Lavender Soft)",
                "☕ Santai & Hangat (Krim / Krem)",
                "🌙 Istirahat / Malam (Abu-abu Modern - Teks Terang)"
            ),
            key="select_warna_admin"
        )
        
        if st.button("Terapkan Tema Warna"):
            if "Coklat" in pilihan_tema:
                st.session_state.warna_bg = "#F5EBE6"
                st.session_state.warna_teks = "#2C221E"
            elif "Putih" in pilihan_tema:
                st.session_state.warna_bg = "#FFFFFF"
                st.session_state.warna_teks = "#1A1A1A"
            elif "Hijau" in pilihan_tema:
                st.session_state.warna_bg = "#E6F9F0"
                st.session_state.warna_teks = "#0D3B22"
            elif "Biru" in pilihan_tema:
                st.session_state.warna_bg = "#E6F2FF"
                st.session_state.warna_teks = "#0B2E59"
            elif "Kuning" in pilihan_tema:
                st.session_state.warna_bg = "#FFF9E6"
                st.session_state.warna_teks = "#4D3800"
            elif "Merah Muda" in pilihan_tema:
                st.session_state.warna_bg = "#FFE6EE"
                st.session_state.warna_teks = "#590D22"
            elif "Ungu" in pilihan_tema:
                st.session_state.warna_bg = "#F3E6FF"
                st.session_state.warna_teks = "#2E0B59"
            elif "Krim" in pilihan_tema:
                st.session_state.warna_bg = "#FDFBF7"
                st.session_state.warna_teks = "#332D25"
            elif "Abu-abu" in pilihan_tema:
                st.session_state.warna_bg = "#2B2B2B"
                st.session_state.warna_teks = "#F0F0F0"
                
            st.success("Warna latar belakang dan warna tulisan berhasil disesuaikan!")
            st.rerun()

# --- TOMBOL KELUAR (LOGOUT) ---
st.write("---")
if st.button("Keluar (Logout)"):
    st.session_state.peran = None
    st.rerun()
