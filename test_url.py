from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/receive_prediction', methods=['POST'])
def receive_prediction():
    data = request.get_json()
    print("Received data from Server A:", data)
    return jsonify({'status': 'received', 'data': data}), 200

if __name__ == '__main__':
    app.run(port=5001, debug=True)  