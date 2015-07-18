import json

from federation.hostmeta.generators import generate_host_meta, generate_legacy_webfinger, generate_hcard
from flask import render_template, request, Response, abort
import redis
from rq import Queue

from social_relay import app


r = redis.Redis(host=app.config.get("REDIS_HOST"), port=app.config.get("REDIS_PORT"), db=app.config.get("REDIS_DB"))

public_queue = Queue("receive", connection=r)


@app.route('/')
def show_public_queue():
    items = r.lrange("receive_public", 0, 29)
    return render_template('show_public_queue.html', items=items)


@app.route('/.well-known/host-meta')
def host_meta():
    hostmeta = generate_host_meta("diaspora", webfinger_host=app.config.get("SERVER_HOST"))
    return Response(hostmeta, status=200, mimetype="application/xrd+xml")


@app.route("/webfinger")
def webfinger():
    account = request.args.get("q", "")
    if account != app.config.get("RELAY_ACCOUNT"):
        return abort(404)
    webfinger = generate_legacy_webfinger(
        "diaspora",
        handle=app.config.get("RELAY_ACCOUNT"),
        host=app.config.get("SERVER_HOST"),
        guid=app.config.get("RELAY_GUID"),
        public_key=app.config.get("RELAY_PUBLIC_KEY")
    )
    return Response(webfinger, status=200, mimetype="application/xrd+xml")


@app.route("/hcard/users/<guid>")
def hcard(guid):
    if guid != app.config.get("RELAY_GUID"):
        return abort(404)
    hcard = generate_hcard(
        "diaspora",
        hostname=app.config.get("SERVER_HOST"),
        fullname=app.config.get("RELAY_NAME"),
        firstname=app.config.get("RELAY_NAME"),
        lastname="",
        photo300="",
        photo100="",
        photo50="",
        searchable="false"
    )
    return Response(hcard, status=200)


@app.route("/receive/public", methods=["POST"])
def receive_public():
    payload = request.form["xml"]
    # Queue to rq for processing
    public_queue.enqueue("workers.receive.process", payload)

    # return 200 whatever
    data = {
        'result'  : 'ok',
    }
    js = json.dumps(data)
    return Response(js, status=200, mimetype='application/json')
