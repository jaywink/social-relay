import json

from federation.hostmeta.generators import generate_host_meta, generate_legacy_webfinger, generate_hcard
from flask import render_template, request, Response, abort
from flask.ext.bower import Bower
import redis
from rq import Queue
from rq_dashboard import RQDashboard

from social_relay import app


r = redis.Redis(host=app.config.get("REDIS_HOST"), port=app.config.get("REDIS_PORT"), db=app.config.get("REDIS_DB"))

public_queue = Queue("receive", connection=r)


# RQ DASHBOARD
if app.config.get("RQ_DASHBOARD"):
    # Snippet from https://github.com/nvie/rq-dashboard/issues/75#issuecomment-90843823
    # Prepare the authentication for the RQ dashboard
    def _basic_http_auth():
        auth = request.authorization
        return auth and auth.password == app.config.get("RQ_DASHBOARD_PASSWORD") and \
               auth.username == app.config.get("RQ_DASHBOARD_USERNAME")

    # And we register it
    RQDashboard(app, auth_handler=_basic_http_auth)

    # NOTE: RQ Dashboard is registered as a blueprint and thus we can setup a Flask error handler for our case.
    # When the configured RQ Dashboard auth_handler returns False, a 401 HTTPException is thrown out,
    # so we can intercept it. Thus, we setup an error handler for the rq_dashboard blueprint.
    def _auth_exception_handler(error):
        return '', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'}

    app.error_handler_spec.setdefault('rq_dashboard', {})[401] = _auth_exception_handler


# Bower
Bower(app)


# Main routes
@app.route('/')
def index():
    return render_template('index.html', config=app.config)


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
