from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "Server is running! 🚀"

@app.route('/test')
def test():
    return jsonify({
        'status': 'working',
        'message': 'Simple test endpoint'
    })

if __name__ == '__main__':
    print("🚀 Starting simple test server...")
    app.run(host='0.0.0.0', port=5000, debug=True)