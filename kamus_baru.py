import streamlit as st
import sqlite3
import pytesseract
import re
from PIL import Image
import os
from gtts import gTTS
from io import BytesIO
import base64
import google.generativeai as genai

# --- KONFIGURASI OTOMATIS ---
if os.name == 'nt':
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# 1. SETUP GEMINI AI (Terkunci pada mesin yang berhasil)
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # Menggunakan mesin yang sudah Anda buktikan berhasil
    model = genai.GenerativeModel('gemini-3.5-flash-lite')
    gemini_ready = True
except Exception as e:
    gemini_ready = False

# 2. KONEKSI DATABASE LOKAL
conn = sqlite3.connect('translator.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS dictionary
             (source_word TEXT, target_word TEXT)''')
try:
    c.execute("ALTER TABLE dictionary ADD COLUMN image_data TEXT")
except:
    pass
conn.commit()

st.title("Aplikasi Web Translator v18 🚀✨")
st.caption("Ditenagai oleh Gemini 3.5 Flash Lite & Kamus Visual Lokal")

# --- Bagian Sidebar ---
st.sidebar.header("Menu Aplikasi")
tab_manual, tab_gambar, tab_db = st.sidebar.tabs(["Manual", "Gambar", "Database"])

with tab_manual:
    with st.form("add_word_form"):
        source = st.text_input("Kata / Frasa Asal (Inggris)")
        target = st.text_input("Terjemahan (Indonesia)")
        gambar_kamus = st.file_uploader("Unggah Ilustrasi (Opsional)", type=['png', 'jpg', 'jpeg'])
        submit = st.form_submit_button("Simpan ke Kamus Lokal")
        
        if submit and source and target:
            image_b64 = ""
            if gambar_kamus is not None:
                image_bytes = gambar_kamus.getvalue()
                image_b64 = base64.b64encode(image_bytes).decode('utf-8')
                
            c.execute("INSERT INTO dictionary (source_word, target_word, image_data) VALUES (?, ?, ?)",
                      (source.lower().strip(), target.lower().strip(), image_b64))
            conn.commit()
            st.success("Tersimpan beserta gambarnya!")

with tab_gambar:
    uploaded_file = st.file_uploader("Unggah gambar daftar teks", type=['png', 'jpg', 'jpeg'])
    if uploaded_file is not None:
        img = Image.open(uploaded_file)
        st.image(img, use_container_width=True)
        
        if st.button("Ekstrak & Simpan"):
            with st.spinner('Membaca teks...'):
                extracted_text = pytesseract.image_to_string(img)
                lines = extracted_text.split('\n')
                saved_count = 0
                for line in lines:
                    pemisah = '=' if '=' in line else ':' if ':' in line else None
                    if pemisah:
                        parts = line.split(pemisah)
                        if len(parts) == 2:
                            kata_asal = re.sub(r'[^a-z\s]+', '', parts[0].lower()).strip()
                            terjemahan = re.sub(r'[^a-z\s]+', '', parts[1].lower()).strip()
                            if kata_asal and terjemahan:
                                c.execute("SELECT * FROM dictionary WHERE source_word=?", (kata_asal,))
                                if not c.fetchone():
                                    c.execute("INSERT INTO dictionary (source_word, target_word, image_data) VALUES (?, ?, ?)",
                                              (kata_asal, terjemahan, ""))
                                    saved_count += 1
                conn.commit()
                st.success(f"{saved_count} frasa/kata berhasil disimpan!")

with tab_db:
    st.write("Isi Kamus Visual Anda Saat Ini:")
    c.execute("SELECT source_word, target_word, image_data FROM dictionary")
    rows = c.fetchall()
    if rows:
        st.table({"Bahasa Inggris": [r[0] for r in rows], "Bahasa Indonesia": [r[1] for r in rows]})
    else:
        st.info("Database masih kosong.")
        
    st.divider()
    if st.button("🚨 Hapus Semua Data (Reset)") :
        c.execute("DELETE FROM dictionary")
        conn.commit()
        st.success("Database dikosongkan. Silakan refresh.")

# --- Bagian Utama: Terjemahan Cerdas ---
st.header("Terjemahkan dengan AI")

arah = st.radio("Pilih Arah Terjemahan:", 
                ("Inggris ke Indonesia", "Indonesia ke Inggris"), 
                horizontal=True)

tempat_gambar = st.empty()
text_input = st.text_area("Masukkan teks atau kalimat panjang:")

if st.button("Terjemahkan"):
    if text_input:
        if arah == "Inggris ke Indonesia":
            c.execute("SELECT source_word, target_word, image_data FROM dictionary ORDER BY LENGTH(source_word) DESC")
            kode_bahasa = 'id'
            prompt_ai = f"Terjemahkan teks berikut ini dari bahasa Inggris ke bahasa Indonesia dengan tata bahasa yang natural, baku, namun mudah dipahami. Jangan tambahkan komentar apa pun, langsung berikan hasil terjemahannya saja:\n\n{text_input}"
        else:
            c.execute("SELECT target_word, source_word, image_data FROM dictionary ORDER BY LENGTH(target_word) DESC")
            kode_bahasa = 'en'
            prompt_ai = f"Terjemahkan teks berikut ini dari bahasa Indonesia ke bahasa Inggris dengan grammar yang tepat dan natural. Jangan tambahkan komentar apa pun, langsung berikan hasil terjemahannya saja:\n\n{text_input}"
            
        dictionary_entries = c.fetchall()
        gambar_ditemukan = []
        
        for source, target, img_data in dictionary_entries:
            pattern = re.compile(r'(?i)\b' + re.escape(source) + r'\b')
            if pattern.search(text_input) and img_data:
                gambar_ditemukan.append((target, img_data))
        
        if gambar_ditemukan:
            with tempat_gambar.container():
                cols = st.columns(min(len(gambar_ditemukan), 3))
                for idx, (kata, img_b64) in enumerate(gambar_ditemukan):
                    with cols[idx % 3]:
                        img_bytes = base64.b64decode(img_b64)
                        st.image(img_bytes, use_container_width=True)
        st.write("---") 

        st.success("**Hasil Terjemahan:**")
        hasil_terjemahan = ""
        
        with st.spinner("AI sedang merangkai kalimat..."):
            if gemini_ready:
                try:
                    response = model.generate_content(prompt_ai)
                    hasil_terjemahan = response.text.strip()
                    st.write(hasil_terjemahan)
                except Exception as e:
                    st.error("Koneksi ke AI terputus. Silakan coba lagi.")
                    hasil_terjemahan = text_input
            else:
                st.error("Sistem AI gagal disiapkan. Pastikan API Key di Streamlit Secrets benar.")
                hasil_terjemahan = text_input
        
        if hasil_terjemahan:
            try:
                with st.spinner("Membuat suara..."):
                    tts = gTTS(text=hasil_terjemahan, lang=kode_bahasa)
                    sound_file = BytesIO()
                    tts.write_to_fp(sound_file)
                    st.audio(sound_file)
            except:
                st.error("Gagal memuat suara.")
