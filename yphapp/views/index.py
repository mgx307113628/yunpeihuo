from flask import json, request, jsonify
from .. import app

@app.route('/')
def hello_world():
    data = request.get_json(True)
    print(type(data))
    return jsonify(code='Hello World!')
