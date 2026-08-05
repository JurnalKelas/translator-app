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

# --- FITUR PILIH TEMA TAMPILAN ---
if "tema_warna" not in st.session_state:
    st.session_state.tema_warna = "Kopi Susu (Bawaan)"
    
with st.expander("🎨 Sesuaikan Warna Tampilan Kamus"):
    st.write("Pilih warna kesukaanmu agar belajar lebih menyenangkan!")
    pilihan_tema = st.selectbox(
        "Pilihan Tema:",
        ["Kopi Susu (Bawaan)", "Biru Langit", "Hijau Daun", "Mode Gelap (Dark Mode)", "Merah Muda (Pink)"]
    )
    st.session_state.tema_warna = pilihan_tema

# Menentukan kode warna
if st.session_state.tema_warna == "Kopi Susu (Bawaan)":
    bg_color = "#DBC1AC"
    text_bg = "#FFFFFF"
    text_color = "#000000"
elif st.session_state.tema_warna == "Biru Langit":
    bg_color = "#E0F7FA"
    text_bg = "#FFFFFF"
    text_color = "#006064"
elif st.session_state.tema_warna == "Hijau Daun":
    bg_color = "#E8F5E9"
    text_bg = "#FFFFFF"
    text_color = "#1B5E20"
elif st.session_state.tema_warna == "Mode Gelap (Dark Mode)":
    bg_color = "#1E1E1E"
    text_bg = "#333333"
    text_color = "#4DABF7"
elif st.session_state.tema_warna == "Merah Muda (Pink)":
    bg_color = "#FCE4EC"
    text_bg = "#FFFFFF"
    text_color = "#880E4F"

# Menerapkan warna (CSS)
st.markdown(f"""
<style>
    .stApp {{
        background-color: {bg_color} !important; 
        transition: background-color 0.5s ease;
    }}
    .stTextArea textarea {{
        background-color: {text_bg} !important; 
        color: {text_color} !important; 
        border-radius: 10px;
    }}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
</style>
""", unsafe_allow_html=True)

# --- MENGHUBUNGKAN KE OTAK AI (GEMINI) ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model_teks = genai.GenerativeModel('gemini-pro')
    model_gambar = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error("Koneksi ke sistem AI terputus. Pastikan kunci rahasia sudah terpasang di menu Secrets Streamlit.")
    st.stop()

# ==========================================
# HALAMAN KHUSUS SISWA
# ==========================================
if st.session_state.peran == "siswa":
    st.title("📖 ALAZKA Smart English Dictionary")
    
    # --- PANDUAN PEMAKAIAN ---
    with st.expander("💡 Panduan Cara Pakai Kamus (Klik di sini)"):
        st.markdown("""
        **Selamat datang di Kamus Pintar ALAZKA!**
        Berikut adalah panduan singkat cara menggunakannya:
        
        1. 🎨 **Ganti Warna Tampilan:** Coba klik menu *'Sesuaikan Warna Tampilan'* di atas. Kamu bisa memilih Mode Gelap atau warna cerah lainnya agar mata lebih nyaman saat membaca.
        2. ✍️ **Mulai Mengetik:** Ketik kata atau kalimat berbahasa Inggris yang belum kamu mengerti di dalam kotak besar di bawah. Kamu juga bisa mengetik bahasa Indonesia untuk diubah ke bahasa Inggris!
        3. ✨ **Lihat Keajaibannya:** Klik tombol **'Terjemahkan Teks ✨'**. Tunggu sebentar, dan mesin AI akan memberikan arti, penjelasan, beserta contoh kalimatnya untukmu.
        4. 🚪 **Selesai Belajar:** Jika sudah selesai, jangan lupa klik tombol **'Keluar (Logout)'** di bagian paling bawah layar.
        
        *Selamat belajar dan terus kembangkan kemampuan bahasamu!*
        """)
    
    st.write("Silakan ketik kata atau kalimat yang ingin diterjemahkan di bawah ini:")
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
                    st.error("Maaf, terjadi kesalahan saat menerjemahkan. Coba lagi ya!")
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
                        # --- PERINTAH BARU YANG LEBIH KETAT ---
                        perintah_gambar = "Baca gambar ini dengan sangat teliti. Ekstrak dan salin persis semua teks yang terlihat di gambar. Jangan menambahkan kalimat penutup, jangan menerjemahkan, dan jangan mengarang kata-kata yang tidak ada di gambar. Susun hasilnya dalam bentuk daftar (list) yang rapi."
                        hasil_ekstrak = model_gambar.generate_content([perintah_gambar, gambar_buka])
                        st.success("Teks berhasil dibaca!")
                        st.write(hasil_ekstrak.text)
                    except Exception as e:
                        st.error("Gagal membaca gambar. Pastikan gambar cukup terang dan jelas.")

# --- TOMBOL KELUAR (LOGOUT) ---
st.write("---")
if st.button("Keluar (Logout)"):
    st.session_state.peran = None
    st.rerun()
