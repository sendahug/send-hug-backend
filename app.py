import os
import json
import math
from flask import Flask, request, abort, jsonify
from flask_cors import CORS

from models import (
    create_db,
    Post,
    User,
    Message,
    add as db_add,
    update as db_update,
    delete_object as db_delete,
    joined_query
    )
from auth import AuthError, requires_auth


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    create_db(app)
    CORS(app, origins='')

    # CORS Setup
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin',
                             'http://localhost:3000')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST,\
                              PATCH, DELETE, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Authorization,\
                              Content-Type')

        return response

    # Paginates posts / messages
    def paginate(items, page):
        items_per_page = 5;
        start_index = (page - 1) * items_per_page
        paginated_items = items[start_index:(start_index+4)]
        total_pages = math.ceil(len(items) / 5)

        return [paginated_items, total_pages]

    # Routes
    # -----------------------------------------------------------------
    # Endpoint: GET /
    # Description: Gets recent and suggested posts.
    # Parameters: None.
    @app.route('/')
    def index():
        # Gets the ten most recent posts
        recent_posts = joined_query('main new')['return']

        # Gets the ten posts with the least hugs
        suggested_posts = joined_query('main suggested')['return']

        return jsonify({
            'success': True,
            'recent': recent_posts,
            'suggested': suggested_posts
        })

    # Endpoint: POST /posts
    # Description: Add a new post to the database.
    # Parameters: None.
    @app.route('/posts', methods=['POST'])
    @requires_auth(['post:post'])
    def add_post(token_payload):
        # Get the post data and create a new post object
        new_post_data = json.loads(request.data)
        new_post = Post(user_id=new_post_data['user_id'],
                        text=new_post_data['text'],
                        date=new_post_data['date'],
                        given_hugs=new_post_data['givenHugs'])

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

    # Endpoint: PATCH /posts/<post_id>
    # Description: Updates a post (either its text or its hugs) in the
    #              database.
    # Parameters: post_id - ID of the post to update.
    @app.route('/posts/<post_id>', methods=['PATCH'])
    @requires_auth(['patch:my-post', 'patch:any-post'])
    def edit_post(token_payload, post_id):
        # If there's no ID provided
        if(post_id is None):
            abort(400)

        updated_post = json.loads(request.data)
        original_post = Post.query.filter(Post.id == post_id).one_or_none()
        # Gets the user's ID
        current_user = User.query.filter(User.auth0_id ==
                                         token_payload['sub']).one_or_none()
        post_author = User.query.filter(User.id == original_post.user_id).one_or_none()

        # If there's no post with that ID
        if(original_post is None):
            abort(404)

        # If the user's permission is 'patch my' the user can only edit
        # their own posts.
        if('patch:my-post' in token_payload['permissions']):
            # Compares the user's ID to the user_id of the post
            if(original_post.user_id != current_user.id):
                # If the user attempted to edit the text of a post that doesn't
                # belong to them, throws an auth error
                if(original_post.text != updated_post['text']):
                    raise AuthError({
                        'code': 403,
                        'description': 'You do not have permission to edit \
                                        this post.'
                        }, 403)
            # Otherwise, the user attempted to edit their own post, which
            # is allowed
            else:
                # If the text was changed
                if(original_post.text != updated_post['text']):
                    original_post.text = updated_post['text']
        # Otherwise, the user is allowed to edit any post, and thus text
        # editing is allowed
        else:
            # If the text was changed
            if(original_post.text != updated_post['text']):
                original_post.text = updated_post['text']

        # If a hug was added
        # Since anyone can give hugs, this doesn't require a permissions check
        if(original_post.given_hugs != updated_post['givenHugs']):
            original_post.given_hugs = updated_post['givenHugs']
            current_user.given_hugs += 1
            post_author.received_hugs += 1

        # Try to update the database
        try:
            db_update(original_post)
            db_update(current_user)
            db_update(post_author)
            db_updated_post = original_post.format()
        # If there's an error, abort
        except Exception as e:
            abort(500)

        return jsonify({
            'success': True,
            'updated': db_updated_post
        })

    # Endpoint: DELETE /posts/<post_id>
    # Description: Deletes a post from the database.
    # Parameters: post_id - ID of the post to delete.
    @app.route('/posts/<post_id>', methods=['DELETE'])
    @requires_auth(['delete:my-post', 'delete:any-post'])
    def delete_post(token_payload, post_id):
        # If there's no ID provided
        if(post_id is None):
            abort(400)

        # Gets the post to delete
        post_data = Post.query.filter(Post.id == post_id).one_or_none()

        # If this post doesn't exist, abort
        if(post_data is None):
            abort(404)

        # If the user only has permission to delete their own posts
        if('delete:my-post' in token_payload['permissions']):
            # Gets the user's ID and compares it to the user_id of the post
            current_user = User.query.filter(User.auth0_id ==
                                             token_payload['sub']).one_or_none()
            # If it's not the same user, they can't delete the post, so an
            # auth error is raised
            if(post_data.user_id != current_user.id):
                raise AuthError({
                    'code': 403,
                    'description': 'You do not have permission to delete \
                                    this post.'
                }, 403)

        # Otherwise, it's either their post or they're allowed to delete any
        # post.
        # Try to delete the post
        try:
            db_delete(post_data)
        # If there's an error, abort
        except Exception as e:
            abort(500)

        return jsonify({
            'success': True,
            'deleted': post_id
        })

    # Endpoint: GET /posts/<type>
    # Description: Gets all new posts.
    # Parameters: type - Type of posts (new or suggested) to fetch.
    @app.route('/posts/<type>')
    def get_new_posts(type):
        page = request.args.get('page', 1, type=int)

        # Gets the recent posts and paginates them
        full_posts = joined_query('full ' + type)['return']
        paginated_data = paginate(full_posts, page)
        paginated_posts = paginated_data[0]
        total_pages = paginated_data[1]

        return jsonify({
            'success': True,
            'posts': paginated_posts,
            'total_pages': total_pages
        })

    # Endpoint: GET /users
    # Description: Gets the user's data.
    # Parameters: None.
    @app.route('/users/<user_id>')
    @requires_auth(['read:user'])
    def get_user_data(token_payload, user_id):
        # If there's no ID provided
        if(user_id is None):
            abort(400)

        user_data = User.query.filter(User.auth0_id == user_id).one_or_none()

        # If there's no user with that ID, abort
        if(user_data is None):
            abort(404)

        formatted_user_data = user_data.format()
        formatted_user_data['posts'] = len(Post.query.filter(Post.user_id ==
                                           user_data.id).all())

        return jsonify({
            'success': True,
            'user': formatted_user_data
        })

    # Endpoint: POST /users
    # Description: Adds a new user to the users table.
    # Parameters: None.
    @app.route('/users', methods=['POST'])
    @requires_auth(['post:user'])
    def add_user(token_payload):
        # Gets the user's data
        user_data = json.loads(request.data)

        # Checks whether a user with that Auth0 ID already exists
        # If it is, aborts
        database_user = User.query.filter(User.auth0_id ==
                                          user_data['id']).one_or_none()
        if(database_user):
            abort(409)

        new_user = User(auth0_id=user_data['id'],
                        display_name=user_data['displayName'])

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

    # Endpoint: PATCH /users/<user_id>
    # Description: Updates a user in the database.
    # Parameters: user_id - ID of the user to update.
    @app.route('/users/<user_id>', methods=['PATCH'])
    @requires_auth(['patch:user', 'patch:any-user'])
    def edit_user(token_payload, user_id):
        # if there's no user ID provided, abort with 'Bad Request'
        if(user_id is None):
            abort(400)

        updated_user = json.loads(request.data)
        original_user = User.query.filter(User.id == user_id).one_or_none()

        # Update user data
        original_user.received_hugs = updated_user['receivedH']
        original_user.given_hugs = updated_user['givenH']
        original_user.login_count = updated_user['loginCount']

        # if the user is only allowed to change their own name (user / mod)
        if('patch:user' in token_payload):
            if(token_payload['sub'] != original_user.auth0_id):
                raise AuthError({
                    'code': 403,
                    'description': 'You do not have permission to edit \
                                    this user\'s display name.'
                }, 403)

        # if the user can edit anyone or the user is trying to update their
        # own name
        original_user.display_name = updated_user['displayName']

        # Try to update it in the database
        try:
            db_update(original_user)
            updated_user = original_user.format()
        # If there's an error, abort
        except Exception as e:
            abort(500)

        return jsonify({
            'success': True,
            'updated': updated_user
        })

    # Endpoint: GET /users/<user_id>/posts
    # Description: Gets a specific user's posts.
    # Parameters: user_id - whose posts to fetch.
    @app.route('/users/<user_id>/posts')
    @requires_auth(['read:user'])
    def get_user_posts(token_payload, user_id):
        page = request.args.get('page', 1, type=int)

        # if there's no user ID provided, abort with 'Bad Request'
        if(user_id is None):
            abort(400)

        # Gets all posts written by the given user
        user_posts = Post.query.filter(Post.user_id == user_id).all()
        user_posts_array = []

        # If there are no posts, returns an empty array
        if(user_posts is None):
            user_posts_array = []
        # If the user has written posts, formats each post and adds it
        # to the posts array
        else:
            for post in user_posts:
                user_posts_array.append(post.format())

            paginated_data = paginate(user_posts_array, page)
            paginated_posts = paginated_data[0]
            total_pages = paginated_data[1]

        return jsonify({
            'success': True,
            'posts': paginated_posts,
            'page': page,
            'total_pages': total_pages
        })

    # Endpoint: GET /messages
    # Description: Gets the user's messages.
    # Parameters: None.
    @app.route('/messages')
    @requires_auth(['read:messages'])
    def get_user_messages(token_payload):
        page = request.args.get('page', 1, type=int)

        # Gets the user's ID from the URL arguments
        user_id = request.args.get('userID', None)

        # If there's no user ID, abort
        if(user_id is None):
            abort(400)

        message = Message.query.filter(Message.for_id == user_id).all()

        # If there are no messages for the user, return an empty array
        if(not message):
            user_messages = []
        # If there are messages, get the user's messages and format them
        else:
            # Gets the user's messages
            user_messages = joined_query('messages',
                                         {'user_id': user_id})['return']
            paginated_data = paginate(user_messages, page)
            paginated_messages = paginated_data[0]
            total_pages = paginated_data[1]

        return jsonify({
            'success': True,
            'messages': paginated_messages,
            'current_page': page,
            'total_pages': total_pages
        })

    # Endpoint: POST /messages
    # Description: Adds a new message to the messages table.
    # Parameters: None.
    @app.route('/messages', methods=['POST'])
    @requires_auth(['post:message'])
    def add_message(token_payload):
        # Gets the new message's data
        message_data = json.loads(request.data)
        new_message = Message(from_id=message_data['fromId'],
                              for_id=message_data['forId'],
                              text=message_data['messageText'],
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

    # Endpoint: DELETE /messages/<message_id>
    # Description: Deletes a message from the database.
    # Parameters: message_id - ID of the message to delete.
    @app.route('/messages/<message_id>', methods=['DELETE'])
    @requires_auth(['delete:messages'])
    def delete_message(token_payload, message_id):
        # If there's no message ID, abort
        if(message_id is None):
            abort(400)

        # Get the message with that ID
        message_data = Message.query.filter(Message.id == message_id).\
                                            one_or_none()

        # If there's no message with that ID, abort
        if(message_data is None):
            abort(404)

        # Try to delete the message
        try:
            db_delete(message_data)
        # If there's an error, abort
        except Exception as e:
            abort(500)

        return jsonify({
            'success': True,
            'deleted': message_id
        })

    # Error Handlers
    # -----------------------------------------------------------------
    # Bad request error handler
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'code': 400,
            'message': 'Bad request. Fix your request and try again.'
        }), 400

    # Not found error handler
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'code': 404,
            'message': 'The resource you were looking for wasn\'t found.'
        }), 404

    # Method not allowed handler
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            'success': False,
            'code': 405,
            'message': 'This HTTP method is not allowed at this endpoint.'
        }), 405

    # Conflict error handler
    @app.errorhandler(409)
    def conflict(error):
        return jsonify({
            'success': False,
            'code': 409,
            'message': 'Conflict. The resource you were trying to create \
                        already exists.'
        }), 409

    # Unprocessable error handler
    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success': False,
            'code': 422,
            'message': 'Unprocessable request.'
        }), 422

    # Internal server error handler
    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            'success': False,
            'code': 500,
            'message': 'An internal server error occurred.'
        }), 500

    # Authentication error handler
    @app.errorhandler(AuthError)
    def auth_error(error):
        return jsonify({
            'success': False,
            'code': error.status_code,
            'message': error.error
        }), error.status_code

    return app


APP = create_app()

if __name__ == '__main__':
    APP.run(host='0.0.0.0', port=8080, debug=True)
