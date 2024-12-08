import logging
from flask import Flask, jsonify, request, redirect, url_for, render_template
import instaloader
import time

# Setup logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

# Fungsi untuk mengambil jumlah followers dan following (login diperlukan untuk akun pribadi)
def get_instagram_data(username, password=None):
    L = instaloader.Instaloader()

    if password:
        try:
            logging.debug(f"Attempting to login with username: {username}")
            L.login(username, password)  # Login menggunakan username dan password
            logging.debug("Login successful.")
        except instaloader.exceptions.BadCredentialsException:
            logging.error(f"Login failed: Bad credentials for username: {username}")
            return {"error": "Bad credentials."}
        except instaloader.exceptions.LoginException as e:
            # Menangani LoginException yang bisa mencakup masalah checkpoint
            logging.error(f"Login failed: {e}")
            return {"error": f"Login failed: {str(e)}. Please verify your login through the browser if required."}
        except Exception as e:
            logging.error(f"Login failed: {e}")
            return {"error": f"Login failed: {e}"}

    # Jika sudah login sebelumnya, kita logout untuk mereset sesi
    try:
        logging.debug(f"Attempting to load profile for username: {username}")
        profile = instaloader.Profile.from_username(L.context, username)
        logging.debug(f"Profile loaded: {username}")
    except instaloader.exceptions.LoginRequiredException:
        logging.debug("Session expired or invalid login. Trying to logout and log in again.")
        L.logout()  # Logout jika sesi lama
        time.sleep(2)  # Tunggu sebentar sebelum login ulang
        try:
            L.login(username, password)  # Login ulang
            profile = instaloader.Profile.from_username(L.context, username)
        except Exception as e:
            logging.error(f"Failed to re-login: {e}")
            return {"error": f"Failed to re-login: {e}"}

    except Exception as e:
        logging.error(f"Failed to load profile: {e}")
        return {"error": f"Failed to load profile: {e}"}

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
