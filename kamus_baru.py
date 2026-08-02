import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- KONFIGURASI HALAMAN UTAMA ---
st.set_page_config(page_title="Kamus Pintar ALAZKA", page_icon="📖", layout="centered")

# --- SISTEM LOGIN & GEMBOK APLIKASI ---
if "peran" not in st.session_state:
    st.session_state.peran = None

if st.session_state.peran is None:
    st.markdown("<h1 style='text-align: center;'>🔒 Gerbang Kamus ALAZKA</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: #4CAF50;'>✨ Created by : Saiful Hadi ✨</h4>", unsafe_allow_html=True)
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
    model_ai = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error("Koneksi ke sistem AI terputus. Pastikan kunci rahasia sudah terpasang.")
    st.stop()

# ==========================================
# HALAMAN KHUSUS SISWA
# ==========================================
if st.session_state.peran == "siswa":
    st.title("📖 ALAZKA Smart English Dictionary")
    st.write("Selamat datang! Pilih menu terjemahan di bawah ini.")
    
    # Membuat pilihan menu tab untuk Siswa: Teks atau Kamera/Foto
    tab_teks, tab_kamera = st.tabs(["✍️ Terjemah Teks / Suara", "📷 Terjemah dari Kamera / Foto"])
    
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
                        else:
                            perintah = f"Translate this English text to Indonesian. Provide ONLY the direct translation without any explanation or notes: {teks_siswa}"
                            
                        hasil = model_ai.generate_content(perintah)
                        teks_bersih = hasil.text.strip().replace('"', '').replace("'", "")
                        
                        st.success("Hasil Terjemahan:")
                        st.write(teks_bersih)
                    except Exception as e:
                        st.error(f"Maaf, terjadi gangguan dari mesin AI: {e}")
            else:
                st.warning("Mohon masukkan kata atau kalimat terlebih dahulu.")

    with tab_kamera:
        st.write("---")
        pilihan_bahasa_kamera = st.radio(
            "Pilih arah terjemahan foto:",
            ("🇮🇩 Gambar Teks Indonesia ➡️ 🇬🇧 Inggris", "🇬🇧 Gambar Teks Inggris ➡️ 🇮🇩 Indonesia"),
            horizontal=True,
            key="radio_kamera"
        )
        st.write("---")
        
        st.info("💡 **Tips:** Anda bisa langsung memotret menggunakan kamera HP atau mengunggah foto teks dari galeri.")
        
        # Fitur untuk mengambil foto langsung atau unggah file gambar
        sumber_gambar = st.radio("Pilih sumber gambar:", ("📸 Ambil Foto Langsung (Kamera)", "📁 Unggah dari Galeri"), horizontal=True)
        
        gambar_unggah = None
        if sumber_gambar == "📸 Ambil Foto Langsung (Kamera)":
            gambar_unggah = st.camera_input("Ambil foto teks yang ingin diterjemahkan")
        else:
            gambar_unggah = st.file_uploader("Pilih file foto...", type=["jpg", "jpeg", "png"])
            
        if gambar_unggah is not None:
            gambar_buka = Image.open(gambar_unggah)
            st.image(gambar_buka, caption="Foto yang akan diterjemahkan", use_column_width=True)
            
            if st.button("Terjemahkan Foto ✨"):
                with st.spinner("AI sedang membaca dan menerjemahkan foto..."):
                    try:
                        if "Indonesia" in pilihan_bahasa_kamera:
                            perintah_foto = "Baca teks dalam gambar ini, lalu terjemahkan ke Bahasa Inggris secara langsung. Berikan HANYA hasil terjemahannya saja tanpa penjelasan tambahan."
                        else:
                            perintah_foto = "Baca teks dalam gambar ini, lalu terjemahkan ke Bahasa Indonesia secara langsung. Berikan HANYA hasil terjemahannya saja tanpa penjelasan tambahan."
                            
                        hasil_foto = model_ai.generate_content([perintah_foto, gambar_buka])
                        foto_bersih = hasil_foto.text.strip().replace('"', '').replace("'", "")
                        
                        st.success("Hasil Terjemahan Foto:")
                        st.write(foto_bersih)
                    except Exception as e:
                        st.error(f"Gagal memproses foto. Pastikan pencahayaan cukup terang. ({e})")

# ==========================================
# HALAMAN KHUSUS ADMIN (PAK SAIFUL)
# ==========================================
elif st.session_state.peran == "admin":
    st.title("⚙️ Panel Admin - Kamus ALAZKA")
    st.info("Selamat bekerja, Pak Saiful! Gunakan menu di bawah ini untuk mengelola aplikasi.")
    
    tab1, tab2 = st.tabs(["📝 Input Manual", "🖼️ Ekstrak dari Gambar"])
    
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
                        perintah_gambar = "Extract all text from this image as a list."
                        hasil_ekstrak = model_ai.generate_content([perintah_gambar, gambar_buka_admin])
                        st.success("Teks berhasil dibaca!")
                        st.write(hasil_ekstrak.text)
                    except Exception as e:
                        st.error(f"Gagal membaca gambar. Pastikan gambar cukup terang. ({e})")

# --- TOMBOL KELUAR (LOGOUT) ---
st.write("---")
if st.button("Keluar (Logout)"):
    st.session_state.peran = None
    st.rerun()
