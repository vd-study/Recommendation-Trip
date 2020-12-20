from flask import Flask, request, jsonify
from recommendation_system import *

app = Flask(__name__)


@app.route('/upload', methods=['POST'])
def upload_file_get():
    if request.method == 'POST':
        user_id = request.json["userId"]
        return jsonify(get_user_trip(user_id))


@app.route("/")
def info_to_user():
    return "Hello !!!"


if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0', port=4567)
