import logging
import requests
from flask import Flask, jsonify, request, redirect, url_for, render_template
import instaloader

# Setup logging
logging.basicConfig(level=logging.DEBUG)  # Menampilkan semua log dengan level DEBUG

app = Flask(__name__)

# Fungsi untuk mengambil jumlah followers dan following (login diperlukan untuk akun pribadi)
def get_instagram_data(username, password=None):
    L = instaloader.Instaloader()

    # Jika password diberikan, lakukan login
    if password:
        try:
            logging.debug(f"Attempting to login with username: {username}")
            L.login(username, password)  # Login menggunakan username dan password
            logging.debug("Login successful.")
        except Exception as e:
            logging.error(f"Login failed: {e}")
            return {"error": f"Login failed: {e}"}

    try:
        # Mengambil profil setelah login (atau tanpa login untuk akun publik)
        logging.debug(f"Attempting to load profile for username: {username}")
        profile = instaloader.Profile.from_username(L.context, username)
        logging.debug(f"Profile loaded: {username}")
    except Exception as e:
        logging.error(f"Failed to load profile: {e}")
        return {"error": f"Failed to load profile: {e}"}

    # Mendapatkan jumlah followers dan following
    followers_count = profile.followers
    following_count = profile.followees
    logging.debug(f"Followers: {followers_count}, Following: {following_count}")

    return {
        'followers_count': followers_count,
        'following_count': following_count
    }

# Halaman login
@app.route('/')
def login():
    logging.debug("Rendering login page.")
    return render_template('login.html')

# Endpoint untuk memproses login dan mengalihkan ke /get_data
@app.route('/login', methods=['POST'])
def do_login():
    username = request.form.get('username')
    password = request.form.get('password')

    if not username or not password:
        logging.error("Username and password are required.")
        return jsonify({'error': 'Username and password are required'}), 400

    logging.debug(f"Received login request for username: {username}")
    # Mengarahkan ke /get_data dengan parameter username dan password
    return redirect(url_for('get_data', username=username, password=password))

# Endpoint untuk mengambil jumlah followers dan following
@app.route('/get_data', methods=['GET'])
def get_data():
    username = request.args.get('username')
    password = request.args.get('password')

    if not username:
        logging.error("Username is required.")
        return jsonify({'error': 'Username is required'}), 400

    logging.debug(f"Received request for data with username: {username}")
    # Mendapatkan jumlah followers dan following setelah login
    data = get_instagram_data(username, password)
    if 'error' in data:
        logging.error(f"Error fetching data: {data['error']}")
        return jsonify(data), 400

    logging.debug(f"Returning data: Followers: {data['followers_count']}, Following: {data['following_count']}")
    return jsonify({
        'followers_count': data['followers_count'],
        'following_count': data['following_count']
    })

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
