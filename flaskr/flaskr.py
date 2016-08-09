#! /usr/bin/env python
#coding=utf-8

import MySQLdb
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE = 'flaskdb',
    DEBUG = True,
    SECRET_KEY = 'development key',
    USERNAME = 'root',
    PASSWORD = '123456',
    HOST = 'localhost',
    PORT = 3306,
))

app.config.from_envvar('FLASKR_SETTINGS', silent=True)

def connect_db():
    try:
        conn = MySQLdb.connect(host=app.config['HOST'], user=app.config['USERNAME'], passwd=app.config['PASSWORD'], db=app.config['DATABASE'], port=app.config['PORT'],use_unicode=True, charset="utf8")
        conn.set_character_set("utf8")
        return conn
    except MySQLdb.Error, e:
        print "Mysql Error %d: %s" % (e.args[0], e.args[1])

def init_db():
    try:
        db = connect_db()
        cur = db.cursor()
        # cur.execute('select * from entries')
        with app.open_resource('schema.sql') as f:
            query="".join(f.read().replace(';\n',';'))
            cur.execute(query)
        db.commit()
    finally:
        cur.close()

@app.cli.command('initdb')
def initdb_command():
    """Creates the database tables."""
    init_db()
    print('Initialized the database.')

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'mysql_db'):
        g.mysql_db = connect_db()
    return g.mysql_db

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'mysql_db'):
        g.mysql_db.close()

@app.route('/')
def show_entries():
    '''fetchall 返回的对象是元祖,和sqlite返回的row对象不同'''
    db = get_db()
    cur = db.cursor()
    cur.execute('select title, text from entries order by id desc')
    # entries = cur.fetchall()
    entries = [dict(title=row[0], text=row[1]) for row in cur.fetchall()]
    return render_template('show_entries.html', entries = entries)

@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    cur = db.cursor()
    sql = "insert into entries (title, text) values (%s, %s)"
    param = (request.form['title'],request.form['text'])
    cur.execute(sql,param)
    db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))

if __name__ == '__main__':
    init_db()
    app.run()