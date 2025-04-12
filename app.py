from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

@app.route('/')
def home():
    return "LinkedIn Post API is live!"

@app.route('/linkedin/post', methods=['POST'])
def post_to_linkedin():
    data = request.get_json()

    access_token = data.get('access_token')
    message_text = data.get('message_text')
    image_path = data.get('image_path')  # Path to the image file
    sub = data.get('sub', "ExgjUI84Az")  # Use default if not provided

    if not access_token or not message_text:
        return jsonify({"error": "Missing access_token or message_text"}), 400

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "LinkedIn-Version": "202404"
    }

    # Step 1: Initialize image upload
    initialize_upload_url = "https://api.linkedin.com/rest/images?action=initializeUpload"
    initialize_upload_payload = {
        "initializeUploadRequest": {
            "owner": f"urn:li:person:{sub}"
        }
    }

    init_response = requests.post(
        initialize_upload_url,
        headers=headers,
        data=json.dumps(initialize_upload_payload)
    )

    if init_response.status_code != 200:
        return jsonify({"error": "Failed to initialize image upload", "details": init_response.text}), init_response.status_code

    upload_details = init_response.json()
    upload_url = upload_details["value"]["uploadUrl"]
    image_urn = upload_details["value"]["image"]

    # Step 2: Upload image to LinkedIn
    with open(image_path, "rb") as image_file:
        upload_response = requests.put(upload_url, headers={"Authorization": f"Bearer {access_token}"}, data=image_file)
    
    if upload_response.status_code != 201 and upload_response.status_code != 200:
        return jsonify({"error": "Failed to upload image", "details": upload_response.text}), upload_response.status_code

    # Step 3: Create post with image URN
    post_url = "https://api.linkedin.com/v2/ugcPosts"
    post_payload = {
        "author": f"urn:li:person:{sub}",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": message_text
                },
                "shareMediaCategory": "IMAGE",
                "media": [
                    {
                        "status": "READY",
                        "media": image_urn
                    }
                ]
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }

    post_response = requests.post(
        post_url,
        headers=headers,
        data=json.dumps(post_payload)
    )

    if post_response.status_code == 201:
        return jsonify({"status": "Post created successfully!"})
    else:
        return jsonify({"error": "Failed to create post", "details": post_response.text}), post_response.status_code
