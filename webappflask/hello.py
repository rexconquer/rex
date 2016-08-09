from flask import Flask, url_for, redirect, abort, make_response
from flask import render_template
from flask import request

app = Flask(__name__)

@app.route('/hello')
def hello_world():
    return 'Hello World!'

@app.route('/')
def index():
    username = request.cookies.get('username')
    return redirect(url_for('login'))
    # return 'Root page ! '

@app.route('/login', methods=['POST', 'GET'])
def login():
    # abort(401)
    error = None
    if request.method == 'POST':
        if valid_login(request.form['username'],
                       request.form['password']):
            return log_the_user_in(request.form['username'])
        else:
            error = 'Invalid username/password'
    # the code below this is executed if the request method
    # was GET or the credentials were invalid
    return render_template('login.html', error=error)


@app.route('/user/<username>')
def profile(username):
    # show the user profile for that user
    return 'User %s' % username

@app.route('/post/<int:post_id>')
def show_post(post_id):
    # show the post with the given id, the id is an integer
    return 'Post %d' % post_id

@app.route('/uuid/<uuid>')
def show_uuid(uuid):
    # show the post with the given id, the id is an integer
    return uuid

@app.route('/projects/')
def projects():
    return 'The project page'

@app.route('/about')
def about():
    return 'The about page'

@app.route('/static')
def style():
    return url_for('static', filename='style.css')

with app.test_request_context():
    print url_for('index')
    print url_for('login')
    print url_for('login',next='/')
    print url_for('profile',username='rex')

with app.test_request_context('/hello', method='POST'):
    # now you can do something with the request until the
    # end of the with block, such as basic assertions:
    assert request.path == '/hello'
    assert request.method == 'POST'

@app.route('/hello/')
@app.route('/hello/<name>')
def hello(name=None):
    return render_template('hello.html', name=name)

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['the_file']
        f.save('.' + secure_filename(f.filename))

@app.errorhandler(404)
def page_not_found(error):
    # return render_template('page_not_found.html'), 404
    resp = make_response(render_template('page_not_found.html'), 404)
    resp.headers['X-Something'] = 'A value'
    return resp

if __name__ == '__main__':
    app.run()
    app.test_request_context()