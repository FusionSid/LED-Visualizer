import os

from flask import Flask, request, jsonify, render_template

from core.config import shared_config, config_lock, SharedConfig

current_dir = os.path.abspath(os.path.dirname(__file__))
template_dir = os.path.join(current_dir, "html")

webapp = Flask(__name__, template_folder=template_dir)


@webapp.route("/config", methods=["POST"])
def config():
    json = request.get_json(silent=True)
    hue = json.get("hue") if json else None

    if not isinstance(hue, (int, float)) or not (0 <= hue <= 1):
        with config_lock:
            return jsonify(shared_config)

    data: SharedConfig = {"hue": hue}

    with config_lock:
        shared_config.update(data)

    return jsonify(success=True)


@webapp.route("/", methods=["GET"])
def home():
    return render_template("index.html")
