from flask import json, request, jsonify
from .. import app

@app.route('/')
def hello_world():
    data = request.get_data()
    print("%s", str(data))
    if data:
        json.loads(data)
    return jsonify(code='Hello World!')
