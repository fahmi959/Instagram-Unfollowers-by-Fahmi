import logging
import time
import requests
from flask import Flask, jsonify, request, render_template
import instaloader

# Setup logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

# URL QStash dan token API untuk autentikasi
QSTASH_URL = 'https://qstash.upstash.io'  # Ganti dengan URL QStash Anda
QSTASH_TOKEN = 'eyJVc2VySUQiOiIwY2JhNzE1MS1jOGU4LTRlYjAtOGI5Ny00ZmZlOGM2ZjU4NmIiLCJQYXNzd29yZCI6ImRiY2E1NTc5MTJhZDQ1MDNhZWYxYzc4NTdjNDFmMDI4In0='  # Ganti dengan token QStash Anda

# Fungsi untuk mengambil jumlah followers dan following (tanpa login, untuk akun publik)
def get_instagram_data(username):
    L = instaloader.Instaloader()

    try:
        # Mengambil profil tanpa login jika akun publik
        profile = instaloader.Profile.from_username(L.context, username)
    except Exception as e:
        logging.error(f"Failed to load profile: {e}")
        return {"error": f"Failed to load profile: {e}"}

    # Mendapatkan jumlah followers dan following
    followers_count = profile.followers
    following_count = profile.followees

    return {
        'followers_count': followers_count,
        'following_count': following_count
    }

# Fungsi untuk mengirimkan tugas ke QStash
def send_to_qstash(username):
    payload = {
        "username": username
    }

    # Mengirim permintaan POST ke QStash
    response = requests.post(
        QSTASH_URL,
        json=payload,
        headers={"Authorization": f"Bearer {QSTASH_TOKEN}"}
    )

    if response.status_code != 200:
        logging.error(f"Failed to send to QStash: {response.text}")
    else:
        logging.debug(f"Task queued in QStash for {username}")

# Halaman login
@app.route('/')
def login():
    return render_template('login.html')

# Endpoint untuk memproses login
@app.route('/login', methods=['POST'])
def do_login():
    username = request.form.get('username')
    password = request.form.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    # Kirim permintaan ke QStash untuk memproses tugas
    send_to_qstash(username)

    return jsonify({'message': f"Task for {username} has been queued in QStash."}), 200

# Endpoint untuk mengambil jumlah followers dan following tanpa login
@app.route('/get_data', methods=['GET'])
def get_data():
    username = request.args.get('username')

    if not username:
        logging.error("Username is required.")
        return jsonify({'error': 'Username is required'}), 400

    # Mendapatkan jumlah followers dan following langsung
    data = get_instagram_data(username)
    if 'error' in data:
        return jsonify(data), 400

    return jsonify({
        'followers_count': data['followers_count'],
        'following_count': data['following_count']
    })

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
