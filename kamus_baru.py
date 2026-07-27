import streamlit as st
import sqlite3
import pytesseract
import re
from PIL import Image
import os
from gtts import gTTS
from io import BytesIO

# --- KONFIGURASI OTOMATIS ---
if os.name == 'nt':
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# 1. Koneksi Database
conn = sqlite3.connect('translator.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS dictionary
             (source_word TEXT, target_word TEXT)''')
conn.commit()

st.title("Aplikasi Web Translator v7 📸🔊")

# --- Bagian Sidebar ---
st.sidebar.header("Menu Aplikasi")
tab_manual, tab_gambar, tab_db = st.sidebar.tabs(["Manual", "Gambar", "Database"])

with tab_manual:
    with st.form("add_word_form"):
        source = st.text_input("Kata / Frasa Asal (Inggris)")
        target = st.text_input("Terjemahan (Indonesia)")
        submit = st.form_submit_button("Simpan Manual")
        
        if submit and source and target:
            c.execute("INSERT INTO dictionary (source_word, target_word) VALUES (?, ?)",
                      (source.lower().strip(), target.lower().strip()))
            conn.commit()
            st.success("Tersimpan!")

with tab_gambar:
    uploaded_file = st.file_uploader("Unggah gambar", type=['png', 'jpg', 'jpeg'])
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
                            # Pembersihan yang lebih ketat
                            kata_asal = re.sub(r'[^a-z\s]+', '', parts[0].lower()).strip()
                            terjemahan = re.sub(r'[^a-z\s]+', '', parts[1].lower()).strip()
                            
                            if kata_asal and terjemahan:
                                c.execute("SELECT * FROM dictionary WHERE source_word=?", (kata_asal,))
                                if not c.fetchone():
                                    c.execute("INSERT INTO dictionary (source_word, target_word) VALUES (?, ?)",
                                              (kata_asal, terjemahan))
                                    saved_count += 1
                conn.commit()
                st.success(f"{saved_count} frasa/kata berhasil disimpan!")

with tab_db:
    st.write("Isi Kamus Anda Saat Ini:")
    c.execute("SELECT source_word, target_word FROM dictionary")
    rows = c.fetchall()
    
    if rows:
        st.table({"Bahasa Inggris": [r[0] for r in rows], "Bahasa Indonesia": [r[1] for r in rows]})
    else:
        st.info("Database masih kosong.")
        
    st.divider()
    if st.button("🚨 Hapus Semua Data (Reset)"):
        c.execute("DELETE FROM dictionary")
        conn.commit()
        st.success("Database dikosongkan. Silakan refresh.")

# --- Bagian Utama: Terjemahan ---
st.header("Terjemahkan Teks")

# PERBAIKAN: Menghapus emoji agar tidak ada salah baca sistem
arah = st.radio("Pilih Arah Terjemahan:", 
                ("Inggris ke Indonesia", "Indonesia ke Inggris"), 
                horizontal=True)

text_input = st.text_area("Masukkan teks:")

if st.button("Terjemahkan"):
    if text_input:
        if arah == "Inggris ke Indonesia":
            c.execute("SELECT source_word, target_word FROM dictionary ORDER BY LENGTH(source_word) DESC")
            kode_bahasa = 'id'
        else:
            c.execute("SELECT target_word, source_word FROM dictionary ORDER BY LENGTH(target_word) DESC")
            kode_bahasa = 'en'
            
        dictionary_entries = c.fetchall()
        translated_text = text_input
        
        # PERBAIKAN: Logika penggantian kata yang lebih santai
        for source, target in dictionary_entries:
            # Mengganti kata tanpa mempedulikan huruf besar/kecil
            pattern = re.compile(re.escape(source), re.IGNORECASE)
            translated_text = pattern.sub(target, translated_text)
                
        st.info("**Hasil Terjemahan:**")
        st.success(translated_text)
        
        try:
            with st.spinner("Membuat suara..."):
                tts = gTTS(text=translated_text, lang=kode_bahasa)
                sound_file = BytesIO()
                tts.write_to_fp(sound_file)
                st.audio(sound_file)
        except:
            st.error("Gagal memuat suara.")
