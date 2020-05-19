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

    return app

APP = create_app()

if __name__ == '__main__':
    APP.run(host='0.0.0.0', port=8080, debug=True)
