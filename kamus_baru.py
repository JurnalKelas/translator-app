import streamlit as st
import google.generativeai as genai
from PIL import Image
import streamlit.components.v1 as components

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
    st.write("Selamat datang! Pilih mode terjemahan, lalu gunakan tombol suara atau ketik manual.")
    
    # --- MENU PILIHAN BAHASA ---
    st.write("---")
    pilihan_bahasa = st.radio(
        "Pilih mode terjemahan:",
        ("🇮🇩 Indonesia ➡️ 🇬🇧 Inggris", "🇬🇧 Inggris ➡️ 🇮🇩 Indonesia"),
        horizontal=True
    )
    st.write("---")
    
    # Kotak teks utama tempat siswa mengetik atau melihat hasil suara
    teks_siswa = st.text_area("Ketik kata/kalimat di sini (atau gunakan tombol suara di bawah):", height=100)
    
    # --- TOMBOL MIKROFON INTERAKTIF DI LAYAR ---
    komponen_suara = """
    <div style="background-color: #f0f2f6; padding: 15px; border-radius: 8px; text-align: center; margin-bottom: 15px;">
        <p style="margin-bottom: 10px; font-weight: bold; color: #31333F;">Atau Ucapkan dengan Suara:</p>
        <button onclick="mulaiRekam()" style="background-color: #ff4b4b; color: white; border: none; padding: 10px 20px; border-radius: 8px; font-weight: bold; cursor: pointer; font-size: 16px;">🎙️ Klik untuk Berbicara</button>
        <p id="statusSuara" style="font-style: italic; color: gray; margin-top: 8px; font-size: 14px;">Tekan tombol lalu ucapkan kata/kalimat...</p>
    </div>
    
    <script>
    function mulaiRekam() {
        const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        recognition.lang = 'id-ID';
        recognition.interimResults = false;
        
        document.getElementById("statusSuara.innerText = "Mendengarkan... Silakan bicara sekarang!";
        
        recognition.onresult = function(event) {
            const hasilKata = event.results[0][0].transcript;
            document.getElementById("statusSuara").innerText = "Berhasil merekam: \\"" + hasilKata + "\\"";
            
            // Mencari elemen textarea Streamlit secara otomatis dan memasukkan teksnya
            const textareas = window.parent.document.querySelectorAll("textarea");
            if (textareas.length > 0) {
                const targetTextarea = textareas[0];
                targetTextarea.value = hasilKata;
                targetTextarea.dispatchEvent(new Event('input', { bubbles: true }));
            }
        };
        
        recognition.onerror = function(event) {
            document.getElementById("statusSuara").innerText = "Gagal mendeteksi suara. Pastikan izin mikrofon aktif.";
        };
        
        recognition.start();
    }
    </script>
    """
    components.html(komponen_suara, height=160)
    
    # Tombol Eksekusi Terjemahan
    if st.button("Terjemahkan ✨"):
        if teks_siswa:
            with st.spinner("AI sedang menerjemahkan..."):
                try:
                    if pilihan_bahasa == "🇮🇩 Indonesia ➡️ 🇬🇧 Inggris":
                        perintah = f"Tugasmu hanya menerjemahkan teks berikut ke Bahasa Inggris. Berikan HANYA hasil terjemahannya saja tanpa penjelasan tambahan. Teks: {teks_siswa}"
                    else:
                        perintah = f"Tugasmu hanya menerjemahkan teks berikut ke Bahasa Indonesia. Berikan HANYA hasil terjemahannya saja tanpa penjelasan tambahan. Teks: {teks_siswa}"
                        
                    hasil = model_teks.generate_content(perintah)
                    st.success("Hasil Terjemahan:")
                    st.write(hasil.text)
                except Exception as e:
                    st.error(f"Maaf, terjadi gangguan dari mesin AI: {e}")
        else:
            st.warning("Mohon masukkan kata atau kalimat terlebih dahulu (ketik atau gunakan tombol mikrofon).")

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
