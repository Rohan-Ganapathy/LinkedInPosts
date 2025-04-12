from flask import Flask, request, jsonify
import requests
import json
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "LinkedIn Post API is live!"

@app.route('/linkedin/post', methods=['POST'])
def post_to_linkedin():
    data = request.get_json()

    access_token = data.get('access_token')
    message_text = data.get('message_text')
    sub = data.get('sub', "ExgjUI84Az")  # Use default if not provided

    if not access_token or not message_text:
        return jsonify({"error": "Missing access_token or message_text"}), 400

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    url = "https://api.linkedin.com/v2/ugcPosts"

    post_data = {
        "author": f"urn:li:person:{sub}",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": message_text
                },
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }

    response = requests.post(url, headers=headers, data=json.dumps(post_data))

    if response.status_code == 201:
        return jsonify({"status": "Post created successfully!"})
    else:
        return jsonify({"error": response.text}), response.status_code
