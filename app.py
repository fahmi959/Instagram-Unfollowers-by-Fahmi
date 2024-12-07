import logging
import time
from flask import Flask, jsonify, request
import instaloader

# Setup logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

# Fungsi untuk login ke Instagram dan mengambil data followers dan following
def get_instagram_data(username, password):
    L = instaloader.Instaloader()

    # Coba muat sesi yang sudah ada (jika ada)
    try:
        L.load_session_from_file(username)
        logging.debug("Session loaded from file.")
    except FileNotFoundError:
        try:
            logging.debug(f"Trying to login with username: {username}")
            L.login(username, password)
            L.save_session_to_file()  # Simpan sesi login untuk penggunaan berikutnya
            logging.debug("Login successful and session saved.")
        except instaloader.TwoFactorAuthRequiredException:
            # Menangani 2FA
            return {"error": "2FA required. Please provide 2FA code manually."}
        except Exception as e:
            logging.error(f"Failed to login to Instagram: {e}")
            raise Exception(f"Failed to login to Instagram: {e}")

    try:
        profile = instaloader.Profile.from_username(L.context, username)
        logging.debug(f"Profile loaded: {profile}")
    except Exception as e:
        logging.error(f"Failed to load profile: {e}")
        raise Exception(f"Failed to load profile: {e}")

    # Ambil semua followers dan following (tanpa batasan 50)
    followers = set(profile.get_followers())  # Ambil semua followers
    following = set(profile.get_followees())  # Ambil semua following

    return {
        'followers': [f.username for f in followers],
        'following': [f.username for f in following]
    }

# Endpoint untuk mengambil data followers dan following
@app.route('/get_data', methods=['GET'])
def get_data():
    username = request.args.get('username')
    password = request.args.get('password')

    if not username or not password:
        logging.error("Username and password are required.")
        return jsonify({'error': 'Username and password are required'}), 400

    try:
        logging.debug(f"Received request for username: {username}")
        time.sleep(5)  # Tambahkan jeda 5 detik antara permintaan untuk menghindari pemblokiran
        data = get_instagram_data(username, password)
        
        # Jika 2FA diperlukan, kembalikan error
        if 'error' in data:
            return jsonify(data), 400
        
        # Ambil daftar unfollowers (followers yang tidak di-follow back)
        unfollowers = set(data['followers']) - set(data['following'])

        # Kembalikan data followers, following, dan unfollowers dalam format JSON
        return jsonify({
            'followers': data['followers'],
            'following': data['following'],
            'unfollowers': list(unfollowers)
        })
    
    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    # Menjalankan Flask di server dengan debug mode
    app.run(debug=True, host='0.0.0.0', port=5000)
