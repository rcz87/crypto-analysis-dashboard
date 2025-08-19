#!/usr/bin/env python3
"""
Minimal working server for deployment troubleshooting
"""
from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/')
def root():
    return jsonify({
        "message": "CryptoSage AI - Minimal Server",
        "status": "working", 
        "port": os.environ.get('PORT', 5000)
    })

@app.route('/api/gpts/status')
def status():
    return jsonify({
        "status": "operational",
        "service": "minimal_deployment_test",
        "endpoints": ["root", "status"],
        "port": os.environ.get('PORT', 5000)
    })

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)