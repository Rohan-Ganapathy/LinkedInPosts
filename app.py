@app.route('/api/data', methods=['POST'])
def receive_data():
    data = request.get_json()
    user = data.get('user')
    message = data.get('message')
    
    # Now you can do anything with `user` and `message`
    print(f"User: {user} sent message: {message}")
    
    return jsonify({"status": "received", "user": user, "message": message})
