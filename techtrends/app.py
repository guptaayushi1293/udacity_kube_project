import sqlite3
import sys

from flask import Flask, json, render_template, request, url_for, redirect, flash
import logging

STDOUT_HANDLER = logging.StreamHandler(stream=sys.stdout)
STDERR_HANDLER = logging.StreamHandler(stream=sys.stderr)
HANDLERS = [STDERR_HANDLER, STDOUT_HANDLER]

FORMATTER = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
    handlers=HANDLERS
)
logger = logging.getLogger(__name__)

DB_COUNTER = 0


def get_db_connection():
    """This function connects to database with the name `database.db`"""
    global DB_COUNTER
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    DB_COUNTER += 1
    return connection


def get_post(post_id):
    """Function to get a post using its ID"""
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                              (post_id,)).fetchone()
    logger.info(f"Retrieved post by using id -> {post_id}")
    connection.close()
    return post


# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'


@app.route('/')
def index():
    """The main route of the web application"""
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    logger.debug(f"Retrieved all the posts from DB -> {len(posts)}")
    return render_template('index.html', posts=posts)


# Define how each individual article is rendered
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    logger.debug(f"Get post by using id -> {post_id}")
    post = get_post(post_id)
    if post is None:
        logger.debug(f"Post does not exists for id -> {post_id}")
        return render_template('404.html'), 404
    else:
        return render_template('post.html', post=post)


# Define the About Us page
@app.route('/about')
def about():
    logger.debug(f"Accessing about us page.")
    return render_template('about.html')


# Define the post creation functionality
@app.route('/create', methods=('GET', 'POST'))
def create():
    logger.debug(f"Creating new post.")
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                               (title, content))
            connection.commit()
            connection.close()
            logger.debug(f"Created post in the db having title -> {title}")
            return redirect(url_for('index'))

    return render_template('create.html')


@app.route('/healthz')
def health_check():
    response = app.response_class(
        response=json.dumps({"result": "OK - healthy"}),
        status=200,
        mimetype='application/json'
    )
    return response


@app.route('/metrics')
def metrics():
    body = {
        'db_connection_count': 0,
        'post_count': 0
    }
    connection = get_db_connection()
    cursor = connection.execute("Select count(*) from posts")
    row = cursor.fetchone()
    if row:
        body['post_count'] = row[0]
    body['db_connection_count'] = DB_COUNTER

    logger.debug(f"Total number of posts are -> {body['post_count']}")
    response = app.response_class(
        response=json.dumps(body),
        status=200,
        mimetype='application/json'
    )
    return response


# start the application on port 3111
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3111, debug=True)
