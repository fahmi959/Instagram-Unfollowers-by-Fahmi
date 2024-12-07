from flask import Flask, jsonify, request
import instaloader
import os

app = Flask(__name__)

# Fungsi untuk login ke Instagram dan mengambil data followers dan following
def get_instagram_data(username, password):
    L = instaloader.Instaloader()

    try:
        L.login(username, password)
    except Exception as e:
        raise Exception(f"Failed to login to Instagram: {e}")

    profile = instaloader.Profile.from_username(L.context, username)

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
        return jsonify({'error': 'Username and password are required'}), 400

    try:
        data = get_instagram_data(username, password)
        unfollowers = set(data['followers']) - set(data['following'])
        return jsonify({'followers': data['followers'], 'following': data['following'], 'unfollowers': list(unfollowers)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
