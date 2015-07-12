import json
from random import random
import redis

from flask import render_template, request, flash, url_for, redirect, Response, abort

from federation.controllers import handle_receive, handle_create_payload
from federation.entities.base import Post
from federation.hostmeta.generators import generate_host_meta, generate_legacy_webfinger

from social_relay import app


r = redis.Redis(host=app.config.get("REDIS_HOST"), port=app.config.get("REDIS_PORT"), db=app.config.get("REDIS_DB"))


@app.route('/')
def show_posts():
    idlist = r.lrange('idlist', 0, -1)
    posts = []
    for i in idlist:
        posts.append({"handle": r.get('posts:%s:handle' % i.decode("utf-8")).decode("utf-8"),
                      "raw_content": r.get('posts:%s:raw_content' % i.decode("utf-8")).decode("utf-8")})
    return render_template('show_posts.html', idlist=idlist, posts=posts)


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


@app.route("/receive/public", methods=["POST"])
def receive_public():
    payload = request.form["xml"]
    sender, protocol_name, entities = handle_receive(payload, skip_author_verification=True)

    for entity in entities:
        print(entity)
        # We only care about posts atm
        if isinstance(entity, Post):
            id = r.incr('global:nextPostId')
            r.lpush('idlist', id)
            r.set('posts:%s:raw_content' % id, '%s' % entity.raw_content)
            r.set('posts:%s:guid' % id, '%s' % entity.guid)
            r.set('posts:%s:handle' % id, '%s' % entity.handle)

    # return 200 whatever
    data = {
        'result'  : 'ok',
    }
    js = json.dumps(data)
    return Response(js, status=200, mimetype='application/json')


@app.route('/add')
def add_entry():
    raw_content = str(random())
    guid = str(random())
    handle = "%s@%s.%s" % (str(random()), str(random()), str(random()))
    id = r.incr('global:nextPostId')
    r.lpush('idlist', id)
    r.set('posts:%s:raw_content' % id, '%s' % raw_content)
    r.set('posts:%s:guid' % id, '%s' % guid)
    r.set('posts:%s:handle' % id, '%s' % handle)
    entity = Post(raw_content=raw_content, guid=guid, handle=handle)
    # data = handle_create_payload()
    flash('New entry was successfully posted')
    return redirect(url_for('show_posts'))
