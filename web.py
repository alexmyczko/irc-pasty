#!/usr/bin/env python3

from flask import Flask, render_template, send_from_directory, request, abort
import os, yaml
from lib.poster import *
from lib.tools import *
from datetime import datetime as dt
from lib.irc import IRC
CONFIG_FILE = 'pasty_server.conf'
PASTY_ROOT = os.path.dirname(__file__)

conff = open(os.path.join(PASTY_ROOT, CONFIG_FILE))
config = yaml.load(conff)
conff.close()

irc_channels = [ '#' + c for c in config['irc']['channels'] ]
irc_client = IRC(server=config['irc']['server'], port=config['irc']['port'], username=config['irc']['username'])

app = Flask(__name__)

def save(title, content, display_mode, directory, year=None, month=None, day=None, hour=None, minute=None, second=None, id=None, irc_channel=None):
    if content == None or title == None:
        return None

    if irc_channel != None:
        if not irc_channel in irc_channels:
            return "ERROR: Channel not found, aborting, post not saved"

    if display_mode == None or display_mode == '':
        display_mode = 0

    if year != None and month != None and day != None and hour != None and minute != None and second != None:
        datetime = dt.strptime(str(year) + makeString(month) + makeString(day) + makeString(hour) + makeString(minute) + makeString(second), "%Y%m%d%H%M%S")
    else:
        datetime = None

    url = savePostTopLevel(title, content, display_mode, datetime, id, directory)

    print(irc_channel)

    if irc_channel != None:
        irc_client.send(irc_channel, os.path.join(config['pasty']['url'], 'get', url))

    return url

@app.route("/")
def create():
    return render_template('post.html', view_mode="edit", irc=buildIrcChannelHash(irc_channels))

@app.route("/autosave", methods=['POST'], strict_slashes=False)
@app.route("/autosave/<int:year>/<int:month>/<int:day>/<int:hour>/<int:minute>/<int:second>/<id>", methods=['POST'], strict_slashes=False)
def autosave(year=None, month=None, day=None, hour=None, minute=None, second=None, id=None):
    rv = save(request.form.get('title'), request.form.get('content'), request.form.get('display_mode'), os.path.join(PASTY_ROOT, 'autosave'), year, month, day, hour, minute, second, id, None)
    if rv == None:
        abort(400)
    else:
        return rv

@app.route("/save", methods=['POST'], strict_slashes=False)
@app.route("/save/<int:year>/<int:month>/<int:day>/<int:hour>/<int:minute>/<int:second>/<id>", methods=['POST'], strict_slashes=False)
def saveR(year=None, month=None, day=None, hour=None, minute=None, second=None, id=None):
    rv = save(request.form.get('title'), request.form.get('content'), request.form.get('display_mode'), os.path.join(PASTY_ROOT, 'posts'), year, month, day, hour, minute, second, id, request.form.get('irc_channel'))
    if rv == None:
        abort(400)
    else:
        return rv

@app.route("/get/<int:year>/<int:month>/<int:day>/<int:hour>/<int:minute>/<int:second>/<id>")
def get(year, month, day, hour, minute, second, id):
    datetime = dt.strptime(str(year) + makeString(month) + makeString(day) + makeString(hour) + makeString(minute) + makeString(second), "%Y%m%d%H%M%S")
    post = getPost(os.path.join(PASTY_ROOT, 'posts'), datetime, id)
    if post == None:
        abort(404)
    elif type(post) == type(bool()):
        abort(500)
    return render_template('post.html', view_mode="show", post_mode=post['display_mode'], post_id=post['link'], post_content=post['content'], post_title=post['title'], irc=buildIrcChannelHash(irc_channels))

@app.route("/getautosave/<int:year>/<int:month>/<int:day>/<int:hour>/<int:minute>/<int:second>/<id>")
def getAutoSave(year, month, day, hour, minute, second, id):
    datetime = dt.strptime(str(year) + makeString(month) + makeString(day) + makeString(hour) + makeString(minute) + makeString(second), "%Y%m%d%H%M%S")
    post = getPost(os.path.join(PASTY_ROOT, 'autosave'), datetime, id)
    if post == None:
        abort(404)
    elif type(post) == type(bool()):
        abort(500)
    return render_template('post.html', view_mode="edit", post_mode=post['display_mode'], post_id=post['link'], post_content=post['content'], post_title=post['title'], irc=buildIrcChannelHash(irc_channels))

@app.route("/all")
def getAll():
    posts = getAllPosts(os.path.join(PASTY_ROOT, 'posts'))
    if type(posts) != type([]):
        abort(500)

    return render_template('all.html', posts=posts)

@app.route("/file/<id>/<name>")
def saveFile(id, name):
    pass

#
# Error handling
#

@app.errorhandler(400)
def internal_server_error(e):
    return render_template('errors/400.html'), 400

@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html'), 500

if __name__ == "__main__":
  app.run(host='0.0.0.0', port=8000, debug=True)
