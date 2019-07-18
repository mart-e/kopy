# PoC for work with both mastodon and twitter

import json
from flask import Flask, jsonify, render_template

from .base import StatusManager


def create_app():
    app = Flask(__name__)
    # TODO retrieve from config/autogenerate
    app.secret_key = (
        b"\xd6|fp\x12\xf1\xf2\x12=M~\x1c\xbar\xb8\x0e\xdd\x12\xa36Dp\xa2\x00"
    )

    manager = StatusManager()

    with open("config.json") as f:
        config = json.load(f)

    for name, site_config in config.items():
        if site_config["site_type"] == "twitter":
            from .twitter import TwitterExtractor

            extractor = TwitterExtractor(name)
        elif site_config["site_type"] == "mastodon":
            from .mastodon import MastodonExtractor

            extractor = MastodonExtractor(name)
        else:
            raise NotImplementedError
        extractor.parse_config(site_config)
        manager.extractors.append(extractor)

    @app.route("/fetch")
    @app.route("/fetch/<int:count>")
    def fetch(count=10):
        manager.retrieve_activities(count)
        return jsonify(manager.export_to_json())

    @app.route("/")
    def main():
        return render_template("index.html", manager=manager)

    return app
