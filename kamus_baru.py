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
    model_teks = genai.GenerativeModel('models/gemma-4-26b-a4b-it')
    model_gambar = genai.GenerativeModel('models/gemma-4-26b-a4b-it')
except Exception as e:
    st.error("Koneksi ke sistem AI terputus. Pastikan kunci rahasia sudah terpasang.")
    st.stop()

# ==========================================
# HALAMAN KHUSUS SISWA
# ==========================================
if st.session_state.peran == "siswa":
    st.title("📖 ALAZKA Smart English Dictionary")
    st.write("Selamat datang! Pilih mode terjemahan, lalu ketik atau rekam suara Anda di bawah ini.")
    
    # --- MENU PILIHAN BAHASA ---
    st.write("---")
    pilihan_bahasa = st.radio(
        "Pilih mode terjemahan:",
        ("🇮🇩 Indonesia ➡️ 🇬🇧 Inggris", "🇬🇧 Inggris ➡️ 🇮🇩 Indonesia"),
        horizontal=True
    )
    st.write("---")
    
    # Pilihan Input: Teks atau Suara
    metode_input = st.radio("Pilih cara memasukkan kata/kalimat:", ("✍️ Ketik Teks", "🎤 Rekam Suara"), horizontal=True)
    
    teks_untuk_diterjemahkan = ""
    
    if metode_input == "✍️ Ketik Teks":
        teks_untuk_diterjemahkan = st.text_area("Ketik kata atau kalimat di sini:", height=100)
    else:
        st.info("Silakan klik tombol mikrofon di bawah untuk mulai merekam suara Anda:")
        rekaman_suara = st.audio_input("Rekam Suara")
        
        if rekaman_suara is not None:
            with st.spinner("AI sedang mendengarkan dan menerjemahkan suara..."):
                try:
                    bytes_audio = rekaman_suara.getvalue()
                    
                    if pilihan_bahasa == "🇮🇩 Indonesia ➡️ 🇬🇧 Inggris":
                        perintah_suara = [
                            "Dengarkan rekaman suara audio berikut. Terjemahkan apa yang diucapkan ke dalam Bahasa Inggris secara akurat. Berikan HANYA hasil terjemahannya saja tanpa penjelasan tambahan, tanpa catatan, dan tanpa pengantar.",
                            {"mime_type": "audio/wav", "data": bytes_audio}
                        ]
                    else:
                        perintah_suara = [
                            "Dengarkan rekaman suara audio berikut. Terjemahkan apa yang diucapkan ke dalam Bahasa Indonesia secara akurat. Berikan HANYA hasil terjemahannya saja tanpa penjelasan tambahan, tanpa catatan, dan tanpa pengantar.",
                            {"mime_type": "audio/wav", "data": bytes_audio}
                        ]
                    
                    hasil_suara = model_teks.generate_content(perintah_suara)
                    st.success("Hasil Terjemahan Suara:")
                    st.write(hasil_suara.text)
                except Exception as e:
                    st.error(f"Gagal memproses suara. Pastikan mikrofon jelas. ({e})")

    # Tombol untuk input teks biasa
    if metode_input == "✍️ Ketik Teks":
        if st.button("Terjemahkan Teks ✨"):
            if teks_untuk_diterjemahkan:
                with st.spinner("AI sedang menerjemahkan..."):
                    try:
                        if pilihan_bahasa == "🇮🇩 Indonesia ➡️ 🇬🇧 Inggris":
                            perintah = f"Tugasmu hanya menerjemahkan teks berikut ke Bahasa Inggris. Berikan HANYA hasil terjemahannya saja. Jangan tulis penjelasan atau pengantar. Teks: {teks_untuk_diterjemahkan}"
                        else:
                            perintah = f"Tugasmu hanya menerjemahkan teks berikut ke Bahasa Indonesia. Berikan HANYA hasil terjemahannya saja. Jangan tulis penjelasan atau pengantar. Teks: {teks_untuk_diterjemahkan}"
                            
                        hasil = model_teks.generate_content(perintah)
                        st.success("Hasil Terjemahan:")
                        st.write(hasil.text)
                    except Exception as e:
                        st.error(f"Maaf, terjadi gangguan dari mesin AI: {e}")
            else:
                st.warning("Mohon ketik kata atau kalimat terlebih dahulu.")

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
        gambar_unggah = st.file_uploader("Pilih gambar daftar kosakata...", type=["jpg", "jpeg", "png"])
        
        if gambar_unggah is not None:
            gambar_buka = Image.open(gambar_unggah)
            st.image(gambar_buka, caption="Gambar yang diunggah", use_column_width=True)
            
            if st.button("Baca & Ekstrak Teks"):
                with st.spinner("Membaca teks dari gambar menggunakan AI..."):
                    try:
                        perintah_gambar = "Keluarkan semua teks yang ada di gambar ini dalam format daftar (list)."
                        hasil_ekstrak = model_gambar.generate_content([perintah_gambar, gambar_buka])
                        st.success("Teks berhasil dibaca!")
                        st.write(hasil_ekstrak.text)
                    except Exception as e:
                        st.error(f"Gagal membaca gambar. Pastikan gambar cukup terang. ({e})")

# --- TOMBOL KELUAR (LOGOUT) ---
st.write("---")
if st.button("Keluar (Logout)"):
    st.session_state.peran = None
    st.rerun()
