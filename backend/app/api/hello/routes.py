from flask import jsonify
from app.api.hello import bp


@bp.route("/hello", methods=["GET"])
def hello_world():
    return jsonify({"message": "Hello World from Flask!"})
