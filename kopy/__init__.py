# PoC for work with both mastodon and twitter

import json
from flask import Flask, render_template


def create_app():
    app = Flask(__name__)

    page_content = ""

    with open('/home/mart/programmation/kopy/config.json') as f:
        config = json.load(f)

    for name, site_config in config.items():
        page_content += f"""
        <h2>Statuses from {name}</h2>
        <ul>
        """
        if site_config['site_type'] == "twitter":
            from .twitter import TwitterExtractor
            extractor = TwitterExtractor(name)
        elif site_config['site_type'] == "mastodon":
            from .mastodon import MastodonExtractor
            extractor = MastodonExtractor(name)
        else:
            raise NotImplementedError

        extractor.parse_config(site_config)
        statuses = extractor.get_statuses()
        for status in statuses:
            page_content += extractor.format_status(status)
        page_content += "</ul>"

    @app.route('/')
    def main():
        return render_template('main.html', statuses)

    return app
