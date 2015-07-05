import redis

from flask import render_template

from social_relay import app

r = redis.Redis(host=app.config.get("REDIS_HOST"), port=app.config.get("REDIS_PORT"), db=app.config.get("REDIS_DB"))

@app.route('/')
def show_posts():
    idlist = r.lrange('idlist',0,-1)
    return render_template('show_posts.html', idlist = idlist, r = r)
