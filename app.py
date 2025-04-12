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
    image_url = data.get('image_url')  # URL of the image to fetch
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

    # Step 2: Download image from the provided URL
    temp_image_path = "temp_image.jpg"
    try:
        response = requests.get(image_url, stream=True)
        if response.status_code == 200:
            with open(temp_image_path, "wb") as image_file:
                for chunk in response.iter_content(1024):
                    image_file.write(chunk)
        else:
            return jsonify({"error": "Failed to download image", "details": response.text}), response.status_code
    except Exception as e:
        return jsonify({"error": "Error downloading image", "details": str(e)}), 500

    # Step 3: Upload image to LinkedIn
    with open(temp_image_path, "rb") as image_file:
        upload_response = requests.put(upload_url, headers={"Authorization": f"Bearer {access_token}"}, data=image_file)

    if upload_response.status_code != 201 and upload_response.status_code != 200:
        return jsonify({"error": "Failed to upload image", "details": upload_response.text}), upload_response.status_code

    # Remove temporary image file
    os.remove(temp_image_path)

    # Step 4: Create post with image URN
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
