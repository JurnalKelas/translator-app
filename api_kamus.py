from flask import Flask, jsonify
import sqlite3

app = Flask(__name__)

# Ini adalah alamat link (endpoint) yang akan dipanggil oleh Android
@app.route('/api/kamus', methods=['GET'])
def ambil_data_kamus():
    try:
        # 1. Buka koneksi ke database SQLite Anda (sesuaikan nama file database-nya)
        koneksi = sqlite3.connect('database_admin.db')
        kursor = koneksi.cursor()
        
        # 2. Ambil semua data kata dan arti dari tabel
        kursor.execute("SELECT kata, arti FROM tabel_kamus")
        baris_data = kursor.fetchall()
        
        # 3. Proses mengubah tabel menjadi format JSON
        hasil_json = []
        for baris in baris_data:
            hasil_json.append({
                "kata": baris[0],  # Kolom pertama (kata)
                "arti": baris[1]   # Kolom kedua (arti)
            })
            
        koneksi.close()
        
        # 4. Kirim hasilnya ke Android dalam bentuk JSON
        return jsonify({"data": hasil_json})

    except Exception as e:
        return jsonify({"error": str(e)})

# Menjalankan server
if __name__ == '__main__':
    # Server akan menyala di port 8000
    app.run(debug=True, port=8000)
