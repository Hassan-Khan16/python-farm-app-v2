from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/receive_prediction', methods=['POST'])
def receive_prediction():
    data = request.get_json()
    # Print the received data to the console for verification
    print("Received data from Server A:", data)
    # Respond back to Server A
    return jsonify({'status': 'received', 'data': data}), 200

if __name__ == '__main__':
    app.run(port=5001, debug=True)  # Run on port 5001 to avoid conflict with Server A