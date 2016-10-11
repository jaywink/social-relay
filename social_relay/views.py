# -*- coding: utf-8 -*-
import json

from flask import render_template, request, Response, abort
from flask.ext.bower import Bower
from rq_dashboard import RQDashboard

from federation.hostmeta.generators import (
    generate_host_meta, generate_legacy_webfinger, generate_hcard, get_nodeinfo_well_known_document,
    NODEINFO_DOCUMENT_PATH, NodeInfo
)

from social_relay import app
from social_relay.utils.queues import public_queue
from social_relay.utils.statistics import get_subscriber_stats, get_count_stats, log_receive_statistics


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
    subscriber_stats = get_subscriber_stats()
    incoming, outgoing, distinct_nodes, processing = get_count_stats()
    return render_template(
        'index.html',
        config=app.config,
        subscriber_stats=subscriber_stats,
        incoming_counts=incoming,
        outgoing_counts=outgoing,
        distinct_nodes=distinct_nodes,
        processing=processing,
    )


@app.route('/.well-known/host-meta')
def host_meta():
    hostmeta = generate_host_meta("diaspora", webfinger_host=app.config.get("SERVER_HOST"))
    return Response(hostmeta, status=200, mimetype="application/xrd+xml")


@app.route('/.well-known/nodeinfo')
def nodeinfo_wellknown():
    nodeinfo = get_nodeinfo_well_known_document(app.config.get("SERVER_HOST"))
    return Response(json.dumps(nodeinfo), status=200, mimetype="application/json")


@app.route(NODEINFO_DOCUMENT_PATH)
def nodeinfo():
    nodeinfo = NodeInfo(
        software={"name": "social-relay", "version": app.config.get("VERSION")},
        protocols={"inbound": ["diaspora"], "outbound": ["diaspora"]},
        services={"inbound": [], "outbound": []},
        open_registrations=False,
        usage={"users": {}},
        metadata={"nodeName": app.config.get("RELAY_NAME")},
        skip_validate=True
    )
    return Response(nodeinfo.render(), status=200, mimetype="application/json")


@app.route("/webfinger")
def webfinger():
    account = request.args.get("q", "")
    if account.startswith("acct:"):
        account = account.replace("acct:", "", 1)
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
        searchable="false",
        guid=app.config.get("RELAY_GUID"),
        public_key=app.config.get("RELAY_PUBLIC_KEY"),
        username=app.config.get("RELAY_USERNAME"),
    )
    return Response(hcard, status=200)


@app.route("/receive/public/", methods=["POST"])
@app.route("/receive/public", methods=["POST"])
def receive_public():
    try:
        payload = request.form["xml"]
    except KeyError:
        return abort(404)
    # Queue to rq for processing
    public_queue.enqueue("workers.receive.process", payload)

    # Log statistics
    log_receive_statistics(request.host)

    # return 200 whatever
    data = {
        'result'  : 'ok',
    }
    js = json.dumps(data)
    return Response(js, status=200, mimetype='application/json')
