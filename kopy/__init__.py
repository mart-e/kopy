# PoC for work with both mastodon and twitter

import json
from flask import Flask, render_template

from .base import StatusManager

def create_app():
    app = Flask(__name__)

    manager = StatusManager()

    with open('/home/mart/programmation/kopy/config.json') as f:
        config = json.load(f)

    for name, site_config in config.items():
        if site_config['site_type'] == "twitter":
            from .twitter import TwitterExtractor
            extractor = TwitterExtractor(name)
        elif site_config['site_type'] == "mastodon":
            from .mastodon import MastodonExtractor
            extractor = MastodonExtractor(name)
        else:
            raise NotImplementedError
        extractor.parse_config(site_config)
        manager.extractors.append(extractor)


    @app.route('/')
    def main():
        for extractor in manager.extractors:
            statuses = extractor.get_statuses()
            for status in statuses:
                manager.add(extractor.convert_status(status))
        return render_template('index.html', manager=manager)

    return app
