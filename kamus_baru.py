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
    st.write("Selamat datang! Pilih mode terjemahan, lalu ketik atau gunakan tombol mikrofon di layar.")
    
    # --- MENU PILIHAN BAHASA ---
    st.write("---")
    pilihan_bahasa = st.radio(
        "Pilih mode terjemahan:",
        ("🇮🇩 Indonesia ➡️ 🇬🇧 Inggris", "🇬🇧 Inggris ➡️ 🇮🇩 Indonesia"),
        horizontal=True
    )
    st.write("---")
    
    # --- TOMBOL MIKROFON KHUSUS DI LAYAR ---
    st.markdown("### 🎤 Input Suara Langsung")
    
    # Komponen HTML & JavaScript untuk tombol rekam suara di layar
    komponen_suara = """
    <div style="display: flex; gap: 10px; align-items: center; margin-bottom: 15px;">
        <button onclick="mulaiRekam()" style="background-color: #ff4b4b; color: white; border: none; padding: 10px 20px; border-radius: 8px; font-weight: bold; cursor: pointer; font-size: 16px;">🎙️ Klik untuk Berbicara</button>
        <span id="statusSuara" style="font-style: italic; color: gray;">Tekan tombol lalu ucapkan kata/kalimat...</span>
    </div>
    <textarea id="hasilSuara" rows="3" style="width: 100%; padding: 8px; border-radius: 5px; border: 1px solid #ccc;" placeholder="Hasil suara akan muncul di sini secara otomatis..."></textarea>
    
    <script>
    function mulaiRekam() {
        const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        recognition.lang = 'id-ID'; // Mengatur bahasa Indonesia, bisa mendengarkan Inggris juga
        recognition.interimResults = false;
        
        document.getElementById("statusSuara").innerText = "Mendengarkan... Silakan bicara sekarang!";
        
        recognition.onresult = function(event) {
            const hasilKata = event.results[0][0].transcript;
            document.getElementById("hasilSuara").value = hasilKata;
            document.getElementById("statusSuara").innerText = "Suara berhasil direkam!";
            // Memicu sinkronisasi ke Streamlit
            const textarea = document.getElementById("hasilSuara");
            textarea.dispatchEvent(new Event('input', { bubbles: true }));
        };
        
        recognition.onerror = function(event) {
            document.getElementById("statusSuara").innerText = "Gagal mendeteksi suara. Coba lagi.";
        };
        
        recognition.start();
    }
    </script>
    """
    components.html(komponen_suara, height=140)
    
    st.write("Atau ketik manual di bawah ini:")
    teks_siswa = st.text_area("Ketik kata atau kalimat:", height=80)
    
    # Tombol Eksekusi Terjemahan
    if st.button("Terjemahkan ✨"):
        # Mengambil teks dari input (bisa dari hasil suara atau ketikan manual)
        target_teks = teks_siswa if teks_siswa else ""
        
        if target_teks:
            with st.spinner("AI sedang menerjemahkan..."):
                try:
                    if pilihan_bahasa == "🇮🇩 Indonesia ➡️ 🇬🇧 Inggris":
                        perintah = f"Tugasmu hanya menerjemahkan teks berikut ke Bahasa Inggris. Berikan HANYA hasil terjemahannya saja tanpa penjelasan tambahan. Teks: {target_teks}"
                    else:
                        perintah = f"Tugasmu hanya menerjemahkan teks berikut ke Bahasa Indonesia. Berikan HANYA hasil terjemahannya saja tanpa penjelasan tambahan. Teks: {target_teks}"
                        
                    hasil = model_teks.generate_content(perintah)
                    st.success("Hasil Terjemahan:")
                    st.write(hasil.text)
                except Exception as e:
                    st.error(f"Maaf, terjadi gangguan dari mesin AI: {e}")
        else:
            st.warning("Mohon ucapkan sesuatu lewat tombol mikrofon atau ketik kata terlebih dahulu.")

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
