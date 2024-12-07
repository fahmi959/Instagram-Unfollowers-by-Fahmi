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
            code = input("Enter 2FA code: ")
            L.two_factor_login(code)
            L.save_session_to_file()  # Simpan sesi 2FA
            logging.debug("Login with 2FA successful.")
        except Exception as e:
            logging.error(f"Failed to login to Instagram: {e}")
            raise Exception(f"Failed to login to Instagram: {e}")

    try:
        profile = instaloader.Profile.from_username(L.context, username)
        logging.debug(f"Profile loaded: {profile}")
    except Exception as e:
        logging.error(f"Failed to load profile: {e}")
        raise Exception(f"Failed to load profile: {e}")

    followers = set(profile.get_followers())
    following = set(profile.get_followees())

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
        unfollowers = set(data['followers']) - set(data['following'])
        return jsonify({'followers': data['followers'], 'following': data['following'], 'unfollowers': list(unfollowers)})
    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
