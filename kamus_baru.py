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

# --- MENGHUBUNGKAN KE OTAK AI DENGAN PELACAK OTOMATIS ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    # Bertanya ke server Google mesin apa yang tersedia
    mesin_tersedia = []
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            mesin_tersedia.append(m.name)
            
    if len(mesin_tersedia) == 0:
        st.error("Kunci sah, tapi Google tidak mengaktifkan mesin AI apa pun untuk akun ini.")
        st.stop()
        
    # Otomatis memilih mesin pertama yang didukung oleh Google
    nama_mesin_terpilih = mesin_tersedia[0]
    
    # Prioritaskan mesin tipe 'flash' atau 'pro' jika ada di daftar
    for nama in mesin_tersedia:
        if "flash" in nama or "pro" in nama:
            nama_mesin_terpilih = nama
            break
            
    model_teks = genai.GenerativeModel(nama_mesin_terpilih)
    model_gambar = genai.GenerativeModel(nama_mesin_terpilih)
    
    # Menampilkan informasi keberhasilan khusus di layar admin
    if st.session_state.peran == "admin":
        st.success(f"Berhasil terhubung secara otomatis menggunakan mesin: {nama_mesin_terpilih}")

except Exception as e:
    st.error(f"Koneksi awal gagal. Laporan sistem: {e}")
    st.stop()

# ==========================================
# HALAMAN KHUSUS SISWA
# ==========================================
if st.session_state.peran == "siswa":
    st.title("📖 ALAZKA Smart English Dictionary")
    st.write("Selamat datang! Ketik kata atau kalimat yang ingin kamu terjemahkan di bawah ini.")
    
    teks_siswa = st.text_area("Teks yang ingin diterjemahkan:", height=100)
    
    if st.button("Terjemahkan Teks ✨"):
        if teks_siswa:
            with st.spinner("Sedang berpikir..."):
                try:
                    perintah = f"Terjemahkan teks berikut ke bahasa Indonesia (jika bahasa Inggris) atau ke bahasa Inggris (jika bahasa Indonesia), dan berikan sedikit penjelasan atau contoh kalimatnya jika perlu. Teks: {teks_siswa}"
                    hasil = model_teks.generate_content(perintah)
                    st.success("Hasil Terjemahan:")
                    st.write(hasil.text)
                except Exception as e:
                    st.error(f"Sistem Google Menolak! Laporan error: {e}")
        else:
            st.warning("Ketik sesuatu dulu di kotak teks ya!")

# ==========================================
# HALAMAN KHUSUS ADMIN (PAK SAIFUL)
# ==========================================
elif st.session_state.peran == "admin":
    st.title("⚙️ Panel Admin - Kamus ALAZKA")
    st.info("Selamat bekerja, Pak Saiful! Gunakan menu di bawah ini untuk memperkaya database kamus.")
    
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
        gambar_unggah = st.file_uploader("Pilih gambar daftar kosakata...", type=["jpg", "jpeg", "png"])
        
        if gambar_unggah is not None:
            gambar_buka = Image.open(gambar_unggah)
            st.image(gambar_buka, caption="Gambar yang diunggah", use_column_width=True)
            
            if st.button("Baca & Ekstrak Teks"):
                with st.spinner("Membaca teks dari gambar..."):
                    try:
                        perintah_gambar = "Keluarkan semua teks yang ada di gambar ini dalam format daftar (list)."
                        hasil_ekstrak = model_gambar.generate_content([perintah_gambar, gambar_buka])
                        st.success("Teks berhasil dibaca!")
                        st.write(hasil_ekstrak.text)
                    except Exception as e:
                        st.error(f"Gagal membaca gambar. Laporan error: {e}")

# --- TOMBOL KELUAR (LOGOUT) ---
st.write("---")
if st.button("Keluar (Logout)"):
    st.session_state.peran = None
    st.rerun()
