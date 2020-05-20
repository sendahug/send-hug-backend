import os
from flask import Flask, request, abort, jsonify
from flask_cors import CORS

from models import create_db, Post, User, Message

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

        for post in suggestted_posts:
            formatted_suggested_posts.append(post.format())

        return jsonify({
            'success': True,
            'recent': formatted_recent_posts,
            'suggested': formatted_suggested_posts
        })


    # Endpoint: GET /users
    # Description: Gets the user's data.
    # Parameters: None.
    @app.route('/users')
    def get_user_data():
        user_id = request.args.get('userID')
        user_data = User.query.filter(User.auth0_id == user_id).one_or_none()

        # If there's no user with that ID, abort
        if(user_data is None):
            abort(404)

        formatted_user_data = user_data.format()

        return jsonify({
            'success': True,
            'user': formatted_user_data
        })

    # Endpoint: GET /messages
    # Description: Gets the user's messages.
    # Parameters: None.
    @app.route('/messages')
    def get_user_messages():
        # Gets the user's messages
        user_id = request.args.get('userID')
        user_messages = Message.query.filter(Message.for_id == user_id).\
            join(User.username.label('from'), User.id == Message.from_id).\
            join(User.username.label('for'), User.id == Message.for_id).all()
        formatted_user_messages = []

        # Formats the user's messages to JSON
        for message in user_messages:
            formatted_message = message.format()
            formatted_message['from'] = message.from
            formatted_message['for'] = message.for
            formatted_user_messages.append(formatted_message)

        return jsonify({
            'success': True,
            'messages': formatted_messages
        })

    return app

APP = create_app()

if __name__ == '__main__':
    APP.run(host='0.0.0.0', port=8080, debug=True)
