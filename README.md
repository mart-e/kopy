# Kopy ☕

Minimal web app to display statuses from Twitter and Mastodon in a unified
interface.

**Still very early stage, lot of missing features, mostly for testing**

![Kopy-screenshot](https://www.odoo.com/r/3mI)

## Dependencies

- [flask](http://flask.pocoo.org/) for the web app
- [tweepy](http://tweepy.org/) for Twitter API
- [Mastodon.py](https://github.com/halcy/Mastodon.py) for Mastodon API

## Configuration

- Create a [Twitter app](https://developer.twitter.com/en/apps)
- Create a Mastodon app (on `/settings/applications` of your instance)
- Create a file named `config.json` (based on `config.json.example`) with tokens

## Run

```
$ export FLASK_APP=kopy
$ flask run
```
