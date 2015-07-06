from random import random
import redis

from flask import render_template, request, flash, url_for, redirect

from federation.controllers import handle_receive, handle_create_payload
from federation.entities.base import Post

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
