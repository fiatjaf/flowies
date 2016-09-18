import os
import re
import json
import bcrypt
import requests
import datetime
from flask import Flask, request, render_template, flash, redirect, url_for
from flask_login import LoginManager, current_user, \
                        login_user, logout_user, login_required
from prettydate import date as prettydate

from apps import fields as appfields

app = Flask(__name__)

PORT = os.getenv('PORT', '5000')
COUCHDB_URL = os.getenv('COUCHDB_URL')
REMEMBER_COOKIE_NAME = 'rmeflowies'
app.config.from_object(__name__)
app.secret_key = os.getenv('SECRET', 'whiplash')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/setup', methods=['POST'])
def setup():
    # wfitem identifier may be a full shared URL
    wfitem = request.form.get('wfitem', '').strip()
    if wfitem.startswith('http'):
        wfitem = [p for p in wfitem.split('/') if p][-1]

    global current_user
    if not current_user.is_authenticated:
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        if re.search('[^\d\w_-]', username):
            flash('Username contains invalid characters.')
            return redirect(url_for('index', wfitem=wfitem, username=username))
        if not (username and password):
            flash('Missing information.')
            return redirect(url_for('index', wfitem=wfitem, username=username))

        # try to fetch user already registered
        try:
            user = User.from_name_password(username, password)
        except WrongPassword:
            # user is registered, but with a different password
            flash('This username is already taken.')
            return redirect(url_for('index', wfitem=wfitem))

        # register user if not
        if not user:
            user = User(username)
            user.save(password)

        login_user(user, remember=True)
        current_user = user

    # register wfitem / add user to it
    if wfitem:
        r = requests.get(COUCHDB_URL + '/' + wfitem)
        if r.status_code == 404:
            doc = {'_id': wfitem, 'users': {}}
        elif r.ok:
            doc = r.json()
        else:
            return r.text, 503

        doc['users'][current_user.name] = {'apps': {}}
        print(doc)
        r = requests.put(COUCHDB_URL + '/' + wfitem, data=json.dumps(doc))
        print(r.text)
        if not r.ok:
            return r.text, 503

    return redirect(url_for('dashboard'))


@app.route('/set-app/<wfshid>/<appname>', methods=['POST'])
@login_required
def set_app(wfshid, appname):
    data = {}
    if len([v for v in request.form.values() if v]) == 0:
        # empty form means delete this app
        pass
    else:
        expected = appfields[appname].keys()
        for field in expected:
            if field not in request.form:
                flash('Missing required field "%s".' % field)
                return redirect(url_for('dashboard'))
            data[field] = request.form[field]

    r = requests.post(COUCHDB_URL + '/_design/apps/_update/set-app/' + wfshid,
                      data=json.dumps({'appdata': data,
                                       'appname': appname,
                                       'username': current_user.name}))

    if not r.ok:
        flash(r.text)

    return redirect(url_for('dashboard') + '#' + wfshid)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        if not (username and password):
            flash('Missing information.')
            return redirect(url_for('login', username=username))

        try:
            user = User.from_name_password(username, password)
            if user:
                login_user(user, remember=True)
                return redirect(url_for('dashboard'))
            else:
                flash('User not registered.')
                return redirect(url_for('login', username=username))
        except WrongPassword:
            # user is registered, but with a different password
            flash('Wrong password.')
            return redirect(url_for('login', username=username))


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    today = datetime.date.today()
    res = requests.get(
        COUCHDB_URL + '/_design/reminders/_view/next-by-user',
        params={
            'startkey': json.dumps([
                current_user.name, today.year, today.month, today.day]),
            'endkey': json.dumps([current_user.name, {}]),
            'limit': 5
        }
    ).json()
    nextreminders = [(
        datetime.date(*row['key'][1:]),
        row['value']
    ) for row in res['rows']]

    return render_template('dashboard.html',
                           wfitems=current_user.get_wfitems(),
                           nextreminders=nextreminders,
                           appfields=appfields)


login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.login_message = 'Please login to access this page.'
login_manager.init_app(app)


@login_manager.user_loader
def load_user(id):
    if not id:
        return None
    return User(id)


class User():
    @classmethod
    def from_name_password(cls, name, password):
        r = requests.get(COUCHDB_URL + '/users~' + name)
        if not r.ok:
            print(r.text)
            return None

        doc = r.json()
        password = password.encode('utf-8')
        hashedpw = doc['password'].encode('utf-8')
        if bcrypt.hashpw(password, hashedpw) == hashedpw:
            return cls(name)
        else:
            raise WrongPassword()

    def __init__(self, name):
        self.name = name

    def save(self, password):
        password = password.encode('utf-8')
        hashedpw = bcrypt.hashpw(password, bcrypt.gensalt()).decode('utf-8')
        r = requests.put(COUCHDB_URL + '/users~' + self.name, data=json.dumps({
            '_id': 'users~' + self.name,
            'password': hashedpw
        }))
        print(r.text)

    def get_wfitems(self):
        wfitems = {}
        r = requests.get(COUCHDB_URL + '/_design/apps/_view/apps',
                         params={'startkey': json.dumps([self.name]),
                                 'endkey': json.dumps([self.name, {}])})
        if not r.ok:
            print(r.text)
            return wfitems
        for row in r.json()['rows']:
            wfid = row['key'][1]
            wfname = row['key'][2]
            try:
                last_updated = prettydate(datetime.datetime.fromtimestamp(
                    row['key'][3] / 1000,
                )) if row['key'][3] else None
            except TypeError:  # date is in iso-string format, not timestamp.
                last_updated = row['key'][3]
            apps = row['value']
            wfitems[wfid] = {
                'name': wfname,
                'apps': apps,
                'last_updated': last_updated
            }
        return wfitems

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.name


class WrongPassword(Exception):
    pass


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(PORT), debug=True)
