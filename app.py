import logging
import time
from flask import Flask, jsonify, request
import instaloader

# Setup logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

# Fungsi untuk mengambil data followers dan following (tanpa login, untuk akun publik)
def get_instagram_data(username):
    L = instaloader.Instaloader()

    try:
        # Mengambil profil tanpa login jika akun publik
        profile = instaloader.Profile.from_username(L.context, username)
    except Exception as e:
        logging.error(f"Failed to load profile: {e}")
        return {"error": f"Failed to load profile: {e}"}

    followers = []
    following = []

    # Ambil followers secara bertahap
    logging.debug("Fetching followers...")
    for i, follower in enumerate(profile.get_followers()):
        followers.append(follower.username)
        if i >= 100:  # Batasi sampai 100 followers
            break
        time.sleep(0.5)  # Delay untuk menghindari pemblokiran

    # Ambil following secara bertahap
    logging.debug("Fetching following...")
    for i, followee in enumerate(profile.get_followees()):
        following.append(followee.username)
        if i >= 100:  # Batasi sampai 100 following
            break
        time.sleep(0.5)  # Delay untuk menghindari pemblokiran

    return {
        'followers': followers,
        'following': following
    }

# Endpoint untuk mengambil data followers dan following tanpa login
@app.route('/get_data', methods=['GET'])
def get_data():
    username = request.args.get('username')

    if not username:
        logging.error("Username is required.")
        return jsonify({'error': 'Username is required'}), 400

    # Mendapatkan data followers dan following
    data = get_instagram_data(username)
    if 'error' in data:
        return jsonify(data), 400

    # Ambil daftar unfollowers (followers yang tidak di-follow back)
    unfollowers = set(data['followers']) - set(data['following'])

    return jsonify({
        'followers': data['followers'],
        'following': data['following'],
        'unfollowers': list(unfollowers)
    })

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
