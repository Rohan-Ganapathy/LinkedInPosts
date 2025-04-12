from flask import Flask, request, jsonify

# ✅ Define the app FIRST
app = Flask(__name__)

# ✅ Now define routes
@app.route('/')
def home():
    return "Flask API is running!"

@app.route('/api/data', methods=['POST'])
def receive_data():
    data = request.get_json()
    user = data.get('user')
    message = data.get('message')

    print(f"User: {user} sent message: {message}")
    return jsonify({
        "status": "received",
        "user": user,
        "message": message
    })
