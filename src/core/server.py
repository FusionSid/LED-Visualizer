import os

from flask import Flask, request, jsonify, render_template

from core.config import shared_config, config_lock, SharedConfig

current_dir = os.path.abspath(os.path.dirname(__file__))
template_dir = os.path.join(current_dir, "html")

webapp = Flask(__name__, template_folder=template_dir)


@webapp.route("/config", methods=["GET", "POST"])
def config():
    if (
        request.method != "POST"
        or not request.json
        or not request.json["hue"]
        or not isinstance(request.json["hue"], float)
    ):
        with config_lock:
            return jsonify(shared_config)

    data: SharedConfig = {"hue": request.json["hue"]}

    with config_lock:
        shared_config.update(data)

    return jsonify(success=True)


@webapp.route("/", methods=["GET"])
def home():
    return render_template("index.html")
