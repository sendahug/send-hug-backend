import os, json
from flask import Flask, request, abort, jsonify
from flask_cors import CORS

from models import {
    create_db,
    Post,
    User,
    Message,
    add as db_add,
    update as db_update,
    delete_object as db_delete
    }


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    create_db(app)
    CORS(app)

    # CORS Setup
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', 'localhost:5000')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST,\
                              PATCH, DELETE, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Authorization')

        return response

    # Routes
    # -----------------------------------------------------------------
    # Endpoint: GET /
    # Description: Gets recent and suggested posts.
    # Parameters: None.
    @app.route('/')
    def index():
        # Gets the ten most recent posts
        recent_posts = Post.query.order_by(Post.date).limit(10).all()
        formatted_recent_posts = []

        for post in recent_posts:
            formatted_recent_posts.append(post.format())

        # Gets the ten posts with the least hugs
        suggested_posts = Post.query.order_by(Post.given_hugs).limit(10).all()
        formatted_suggested_posts = []

        for post in suggested_posts:
            formatted_suggested_posts.append(post.format())

        return jsonify({
            'success': True,
            'recent': formatted_recent_posts,
            'suggested': formatted_suggested_posts
        })


    # Endpoint: POST /posts
    # Description: Add a new post to the database.
    # Parameters: None.
    @app.route('/posts', methods=['POST'])
    def add_post():
        # Get the post data and create a new post object
        new_post_data = json.loads(request.data)
        new_post = Post(user_id=new_post_data['userId'],
                        text=new_post_data['text'],
                        date=new_post_data['date'],
                        given_hugs=new_post_data['hugs'])

        # Try to add the post to the database
        try:
            db_add(new_post)
            added_post = new_post.format()
        # If there's an error, abort
        except Exception as e:
            abort(500)

        return jsonify({
            'success': True,
            'posts': added_post
        })


    # Endpoint: GET /users
    # Description: Gets the user's data.
    # Parameters: None.
    @app.route('/users')
    def get_user_data():
        user_id = request.args.get('userID', None)

        # If there's no ID provided
        if(user_id is None):
            abort(404)

        user_data = User.query.filter(User.auth0_id == user_id).one_or_none()

        # If there's no user with that ID, abort
        if(user_data is None):
            abort(404)

        formatted_user_data = user_data.format()

        return jsonify({
            'success': True,
            'user': formatted_user_data
        })


    # Endpoint: POST /users
    # Description: Adds a new user to the users table.
    # Parameters: None.
    @app.route('/users', methods=['POST'])
    def add_user():
        # Gets the user's data via the Auth0 post-registration hook
        user_data = json.loads(request.data)
        new_user = User(username=user_data['username'],
                        auth0_id=user_data['id'], received_hugs=0,
                        given_hugs=0, posts=0)

        # Try to add the post to the database
        try:
            db_add(new_user)
            added_user = new_user.format()
        # If there's an error, abort
        except Exception as e:
            abort(500)

        return jsonify({
            'success': True,
            'user': added_user
        })

    # Endpoint: GET /messages
    # Description: Gets the user's messages.
    # Parameters: None.
    @app.route('/messages')
    def get_user_messages():
        # Gets the user's ID from the URL arguments
        user_id = request.args.get('userID', None)

        # If there's no user ID, abort
        if(user_id is None):
            abort(404)

        # Gets the user's messages
        user_messages = Message.query.filter(Message.for_id == user_id).\
            join(User.username.label('from'), User.id == Message.from_id).\
            join(User.username.label('for'), User.id == Message.for_id).all()
        formatted_user_messages = []

        # Formats the user's messages to JSON
        for message in user_messages:
            formatted_message = message[1].format()
            formatted_message['from'] = message[2]
            formatted_message['for'] = message[3]
            formatted_user_messages.append(formatted_message)

        return jsonify({
            'success': True,
            'messages': formatted_messages
        })

    # Endpoint: POST /messages
    # Description: Adds a new message to the messages table.
    # Parameters: None.
    @app.route('/messages', methods=['POST'])
    def add_message():
        # Gets the new message's data
        message_data = json.loads(request.data)
        new_message = Message(from_id=message_data['fromId'],
                              for_id=message_data['forId'],
                              text=message_data['text'],
                              date=message_data['date'])

        # Try to add the post to the database
        try:
            db_add(new_message)
            sent_message = new_message.format()
        # If there's an error, abort
        except Exception as e:
            abort(500)

        return jsonify({
            'success': True,
            'message': sent_message
        })


    # Error Handlers
    # -----------------------------------------------------------------
    # Not found error handler
    @app.errorhandler(404)
    def not_found(eror):
        return jsonify({
            'success': False,
            'code': 404,
            'message': 'The resource you were looking for wasn\'t found.'
        }), 404

    return app

APP = create_app()

if __name__ == '__main__':
    APP.run(host='0.0.0.0', port=8080, debug=True)
