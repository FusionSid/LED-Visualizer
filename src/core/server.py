import os

from flask import Flask, request, jsonify, render_template

from core.config import shared_config, config_lock, SharedConfig

current_dir = os.path.abspath(os.path.dirname(__file__))
template_dir = os.path.join(current_dir, "html")

webapp = Flask(__name__, template_folder=template_dir)


@webapp.route("/config", methods=["POST"])
def config():
    if (
        not request.json
        or request.json["hue"] is None
        # the hue must be a float except for the case where its 0 (as that means random color)
        or (not isinstance(request.json["hue"], float) and request.json["hue"] != 0)
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
