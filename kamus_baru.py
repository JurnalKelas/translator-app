import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- KONFIGURASI HALAMAN UTAMA ---
st.set_page_config(page_title="Kamus Pintar ALAZKA", page_icon="📖", layout="centered")

# --- SISTEM LOGIN ---
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

# --- AMBIL DAFTAR MESIN DARI GOOGLE ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    mesin_tersedia = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
except Exception as e:
    st.error(f"Koneksi gagal. Laporan: {e}")
    st.stop()

# ==========================================
# HALAMAN KHUSUS SISWA
# ==========================================
if st.session_state.peran == "siswa":
    st.title("📖 ALAZKA Smart English Dictionary")
    st.info("Mohon bersabar, aplikasi kamus sedang dalam perbaikan oleh Admin (Pak Saiful) agar lebih canggih!")

# ==========================================
# HALAMAN KHUSUS ADMIN (MODE PELACAK MESIN)
# ==========================================
elif st.session_state.peran == "admin":
    st.title("🛠️ Mode Perbaikan Mesin Google")
    st.warning("Mari kita tes satu per satu mesin di bawah ini sampai menemukan yang diizinkan oleh Google.")
    
    pilihan_mesin = st.selectbox("Pilih Mesin untuk Dites:", mesin_tersedia)
    kata_uji = st.text_input("Ketik kata untuk dites (misal: school):", "school")
    
    if st.button("🚀 Uji Mesin Ini"):
        with st.spinner(f"Mencoba menerjemahkan menggunakan {pilihan_mesin}..."):
            try:
                model_uji = genai.GenerativeModel(pilihan_mesin)
                hasil = model_uji.generate_content(f"Terjemahkan ke bahasa Indonesia: {kata_uji}")
                st.success(f"🎉 BERHASIL! Mesin '{pilihan_mesin}' berfungsi sangat baik!")
                st.write("**Hasil Terjemahan:**", hasil.text)
                st.info("Tolong kirimkan nama mesin ini ke saya agar aplikasinya bisa kita normalkan kembali!")
            except Exception as e:
                st.error(f"❌ MESIN INI DITOLAK. Pesan Google: {e}")

# --- TOMBOL KELUAR ---
st.write("---")
if st.button("Keluar (Logout)"):
    st.session_state.peran = None
    st.rerun()
