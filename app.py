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
    Thread,
    Report,
    add as db_add,
    update as db_update,
    delete_object as db_delete,
    delete_all as db_delete_all,
    joined_query
    )
from auth import AuthError, requires_auth
from filter import Filter


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    create_db(app)
    CORS(app, origins='')
    word_filter = Filter()

    # CORS Setup
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin',
                             os.environ.get('FRONTEND'))
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST,\
                              PATCH, DELETE, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Authorization,\
                              Content-Type')

        return response

    # Paginates posts / messages
    def paginate(items, page):
        items_per_page = 5
        start_index = (page - 1) * items_per_page
        paginated_items = items[start_index:(start_index+5)]
        total_pages = math.ceil(len(items) / 5)

        return [paginated_items, total_pages]

    # Routes
    # -----------------------------------------------------------------
    # Endpoint: GET /
    # Description: Gets recent and suggested posts.
    # Parameters: None.
    # Authorization: None.
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

    # Endpoint: POST /
    # Description: Run a search.
    # Parameters: None.
    # Authorization: None.
    @app.route('/', methods=['POST'])
    def search():
        search_query = json.loads(request.data)['search']
        current_page = request.args.get('page', 1, type=int)

        # Get the users with the search query in their display name
        users = User.query.filter(User.display_name.
                                  ilike('%' + search_query + '%')).all()
        posts = joined_query('post search', {'query': search_query})['return']
        formatted_users = []

        # Get the total number of items
        user_results = len(users)
        post_results = len(posts)

        # Formats the users' data
        for user in users:
            formatted_users.append(user.format())

        # Paginates posts
        paginated_data = paginate(posts, current_page)
        paginated_posts = paginated_data[0]
        total_pages = paginated_data[1]

        return jsonify({
            'success': True,
            'users': formatted_users,
            'posts': paginated_posts,
            'user_results': user_results,
            'post_results': post_results,
            'current_page': current_page,
            'total_pages': total_pages
        })

    # Endpoint: POST /posts
    # Description: Add a new post to the database.
    # Parameters: None.
    # Authorization: post:post.
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
    # Authorization: patch:my-post or patch:any-post.
    @app.route('/posts/<post_id>', methods=['PATCH'])
    @requires_auth(['patch:my-post', 'patch:any-post'])
    def edit_post(token_payload, post_id):
        # If there's no ID provided
        if(post_id is None):
            abort(404)

        updated_post = json.loads(request.data)
        original_post = Post.query.filter(Post.id == post_id).one_or_none()
        # Gets the user's ID
        current_user = User.query.filter(User.auth0_id ==
                                         token_payload['sub']).one_or_none()

        # If there's no post with that ID
        if(original_post is None):
            abort(404)

        post_author = User.query.filter(User.id ==
                                        original_post.user_id).one_or_none()

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
    # Authorization: delete:my-post or delete:any-post.
    @app.route('/posts/<post_id>', methods=['DELETE'])
    @requires_auth(['delete:my-post', 'delete:any-post'])
    def delete_post(token_payload, post_id):
        # If there's no ID provided
        if(post_id is None):
            abort(404)

        # Gets the post to delete
        post_data = Post.query.filter(Post.id == post_id).one_or_none()

        # If this post doesn't exist, abort
        if(post_data is None):
            abort(404)

        # If the user only has permission to delete their own posts
        if('delete:my-post' in token_payload['permissions']):
            # Gets the user's ID and compares it to the user_id of the post
            current_user = User.query.filter(User.auth0_id ==
                                             token_payload['sub']).\
                                             one_or_none()
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
    # Authorization: None.
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

    # Endpoint: GET /users/<type>
    # Description: Gets users by a given type.
    # Parameters: type - A type by which to filter the users.
    # Authorization: read:admin-board.
    @app.route('/users/<type>')
    @requires_auth(['read:admin-board'])
    def get_users_by_type(token_payload, type):
        page = request.args.get('page', 1, type=int)

        # If the type of users to fetch is blocked users
        if(type.lower() == 'blocked'):
            # Get all blocked users
            users = User.query.filter(User.blocked == True).\
                    order_by(User.release_date).all()

            # If there are no blocked users
            if(users is None):
                paginated_users = []
                total_pages = 1
            # Otherwise, filter and paginate blocked users
            else:
                formatted_users = []

                # Format users data
                for user in users:
                    formatted_users.append(user.format())

                # Paginate users
                paginated_data = paginate(formatted_users, page)
                paginated_users = paginated_data[0]
                total_pages = paginated_data[1]

        return jsonify({
            'success': True,
            'users': paginated_users,
            'total_pages': total_pages
        })

    # Endpoint: GET /users/all/<user_id>
    # Description: Gets the user's data.
    # Parameters: user_id - The user's Auth0 ID.
    # Authorization: read:user.
    @app.route('/users/all/<user_id>')
    @requires_auth(['read:user'])
    def get_user_data(token_payload, user_id):
        # If there's no ID provided
        if(user_id is None):
            abort(404)

        user_data = User.query.filter(User.auth0_id == user_id).one_or_none()

        # If there's no user with that Auth0 ID, try to find a user with that
        # ID; the user might be trying to view user profile
        if(user_data is None):
            user_data = User.query.filter(User.id == user_id).one_or_none()

            # If there's no user with that ID either, abort
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
    # Authorization: post:user.
    @app.route('/users', methods=['POST'])
    @requires_auth(['post:user'])
    def add_user(token_payload):
        # Gets the user's data
        user_data = json.loads(request.data)

        # If the user is attempting to add a user that isn't themselves to
        # the database, aborts
        if(user_data['auth0Id'] != token_payload['sub']):
            abort(422)

        # Checks whether a user with that Auth0 ID already exists
        # If it is, aborts
        database_user = User.query.filter(User.auth0_id ==
                                          user_data['id']).one_or_none()
        if(database_user):
            abort(409)

        new_user = User(auth0_id=user_data['id'],
                        display_name=user_data['displayName'],
                        role='user')

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
    # Authorization: patch:user or patch:any-user.
    @app.route('/users/<user_id>', methods=['PATCH'])
    @requires_auth(['patch:user', 'patch:any-user'])
    def edit_user(token_payload, user_id):
        # if there's no user ID provided, abort with 'Bad Request'
        if(user_id is None):
            abort(404)

        updated_user = json.loads(request.data)
        original_user = User.query.filter(User.id == user_id).one_or_none()
        current_user = User.query.filter(User.auth0_id ==
                                         token_payload['sub']).one_or_none()

        # If the user being updated was given a hug, also update the current
        # user's "given hugs" value, as they just gave a hug
        if('receivedH' in updated_user and 'givenH' in updated_user):
            if(original_user.received_hugs != updated_user['receivedH']):
                current_user.given_hugs += 1

            # Update user data
            original_user.received_hugs = updated_user['receivedH']
            original_user.given_hugs = updated_user['givenH']

        # If there's a login count (meaning, the user is editing their own
        # data), update it
        if('loginCount' in updated_user):
            original_user.login_count = updated_user['loginCount']

        # If the user is attempting to change a user's display name, check
        # their permissions
        if('displayName' in updated_user):
            if(updated_user['displayName'] != original_user.display_name):
                # if the user is only allowed to change their own name
                # (user / mod)
                if('patch:user' in token_payload['permissions']):
                    if(token_payload['sub'] != original_user.auth0_id):
                        raise AuthError({
                            'code': 403,
                            'description': 'You do not have permission to \
                                            edit this user\'s display name.'
                            }, 403)
                else:
                    # if the user can edit anyone or the user is trying to
                    # update their own name
                    original_user.display_name = updated_user['displayName']

        # If the request was in done in order to block or unlock a user
        if('blocked' in updated_user):
            # If the user doesn't have permission to block/unblock a user
            if('block:user' not in token_payload['permissions']):
                raise AuthError({
                    'code': 403,
                    'description': 'You do not have permission to block \
                                    this user.'
                }, 403)
            # Otherwise, the user is a manager, so they can block a user.
            # In that case, block / unblock the user as requested.
            else:
                original_user.blocked = updated_user['blocked']
                original_user.release_date = updated_user['releaseDate']

        # Checks if the user's role is updated based on the
        # permissions in the JWT
        # Checks whether the user has 'patch:any-post' permission, which
        # if given to moderators and admins
        if('patch:any-post' in token_payload['permissions']):
            # Checks whether the user has 'delete:any-post' permission, which
            # is given only to admins, and whether the user is already
            # marked as an admin in the database; if the user isn't an admin
            # in the database, changes their role to admin. If they are,
            # there's no need to update their role.
            if('delete:any-post' in token_payload['permissions'] and
               original_user.role != 'admin'):
                original_user.role = 'admin'
            # If the user doesn't have that permission but they have the
            # permission to edit any post, they're moderators. Checks whether
            # the user is marked as a mod in the database; if the user isn't,
            # changes their role to moderator. If they are, there's no need to
            # update their role.
            elif('delete:any-post' not in token_payload['permissions'] and
                 original_user.role != 'moderator'):
                original_user.role = 'moderator'

        # Try to update it in the database
        try:
            db_update(original_user)
            db_update(current_user)
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
    # Authorization: read:user.
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

    # Endpoint: DELETE /users/<user_id>/posts
    # Description: Deletes a specific user's posts.
    # Parameters: user_id - whose posts to delete.
    # Authorization: delete:my-post or delete:any-post
    @app.route('/users/<user_id>/posts', methods=['DELETE'])
    @requires_auth(['delete:my-post', 'delete:any-post'])
    def delete_user_posts(token_payload, user_id):
        current_user = User.query.filter(User.auth0_id ==
                                         token_payload['sub']).one_or_none()

        # If the user making the request isn't the same as the user
        # whose posts should be deleted
        if(current_user.id != user_id):
            # If the user can only delete their own posts, they're not
            # allowed to delete others' posts, so raise an AuthError
            if('delete:my-post' in token_payload['permissions']):
                raise AuthError({
                    'code': 403,
                    'description': 'You do not have permission to delete \
                                    another user\'s posts.'
                }, 403)

        # Otherwise, the user is either trying to delete their own posts or
        # they're allowed to delete others' posts, so let them continue
        posts = Post.query.filter(Post.user_id == user_id).all()
        num_deleted = len(posts)

        # If the user has no posts, abort
        if(num_deleted == 0):
            abort(404)

        # Try to delete
        try:
            db_delete_all('posts', user_id)
        # If there's an error, abort
        except Exception as e:
            abort(500)

        return jsonify({
            'success': True,
            'userID': user_id,
            'deleted': num_deleted
        })

    # Endpoint: GET /messages
    # Description: Gets the user's messages.
    # Parameters: None.
    # Authorization: read:messages.
    @app.route('/messages')
    @requires_auth(['read:messages'])
    def get_user_messages(token_payload):
        page = request.args.get('page', 1, type=int)
        type = request.args.get('type', 'inbox')
        thread_id = request.args.get('threadID', None)

        # Gets the user's ID from the URL arguments
        user_id = request.args.get('userID', None)

        # If there's no user ID, abort
        if(user_id is None):
            abort(400)

        # The user making the request
        requesting_user = User.query.filter(User.auth0_id ==
                                            token_payload['sub']).one_or_none()

        # If the user is attempting to read another user's messages
        if(requesting_user.id != int(user_id)):
            raise AuthError({
                'code': 403,
                'description': 'You do not have permission to view another\
                                user\'s messages.'
            }, 403)

        # Checks which mailbox the user is requesting
        if(type == 'inbox'):
            message = Message.query.filter(Message.for_id == user_id).all()
        elif(type == 'outbox'):
            message = Message.query.filter(Message.from_id == user_id).all()
        elif(type == 'threads'):
            message = Message.query.filter((Message.from_id == user_id) |
                                           (Message.for_id == user_id)).all()
        elif(type == 'thread'):
            message = Thread.query.filter(Thread.id == thread_id).one_or_none()
            # If the user is trying to view a thread that belongs to other
            # users, raise an AuthError
            if((message.user_1_id != requesting_user.id) and
               (message.user_2_id != requesting_user.id)):
                raise AuthError({
                    'code': 403,
                    'description': 'You do not have permission to view another\
                                user\'s messages.'
                }, 403)
        else:
            abort(404)

        # If there are no messages for the user, return an empty array
        if(not message):
            user_messages = []
            paginated_messages = []
            total_pages = 0
        # If there are messages, get the user's messages and format them
        else:
            # Gets the user's messages
            user_messages = joined_query('messages',
                                         {'user_id': user_id,
                                          'type': type,
                                          'thread_id': thread_id})['return']
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
    # Authorization: post:message.
    @app.route('/messages', methods=['POST'])
    @requires_auth(['post:message'])
    def add_message(token_payload):
        # Gets the new message's data
        message_data = json.loads(request.data)

        logged_user = User.query.filter(User.auth0_id ==
                                        token_payload['sub']).one_or_none()

        # Checks that the user isn't trying to send a message from someone else
        if(logged_user.id != message_data['fromId']):
            raise AuthError({
                'code': 403,
                'description': 'You do not have permission to send a message\
                                on behalf of another user.'
            }, 403)

        # Checks if there's an existing thread between the users
        thread = Thread.query.filter(((Thread.user_1_id ==
                                       message_data['fromId']) and
                                     (Thread.user_2_id ==
                                      message_data['forId']))).one_or_none()

        # If there's no thread between the users
        if(thread is None):
            new_thread = Thread(user_1_id=message_data['fromId'],
                                user_2_id=message_data['forId'])
            # Try to create the new thread
            try:
                db_add(new_thread)
                thread_id = new_thread.id
            # If there's an error, abort
            except Exception as e:
                abort(500)
        # If there's a thread between the users
        else:
            thread_id = thread.id

        new_message = Message(from_id=message_data['fromId'],
                              for_id=message_data['forId'],
                              text=message_data['messageText'],
                              date=message_data['date'],
                              thread=thread_id)

        # Try to add the message to the database
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

    # Endpoint: DELETE /messages/<mailbox_type>/<thread_id>
    # Description: Deletes a message/thread from the database.
    # Parameters: mailbox_type - the type of message to delete.
    #             item_id - ID of the message/thread to delete.
    # Authorization: delete:messages.
    @app.route('/messages/<mailbox_type>/<item_id>', methods=['DELETE'])
    @requires_auth(['delete:messages'])
    def delete_thread(token_payload, mailbox_type, item_id):
        # If there's no thread ID, abort
        if(item_id is None):
            abort(405)

        # If the mailbox type is inbox or outbox, search for a message
        # with that ID
        if(mailbox_type == 'inbox' or mailbox_type == 'outbox'):
            delete_item = Message.query.filter(Message.id == item_id).\
                one_or_none()
        # If the mailbox type is threads, search for a thread with that ID
        elif(mailbox_type == 'threads'):
            delete_item = Thread.query.filter(Thread.id == item_id).\
                one_or_none()

        # If this message/thread doesn't exist, abort
        if(delete_item is None):
            abort(404)

        request_user = User.query.filter(User.auth0_id ==
                                         token_payload['sub']).one_or_none()

        # If the mailbox type is inbox
        if(mailbox_type == 'inbox'):
            # If the user is attempting to delete another user's messages
            if(request_user.id != delete_item.for_id):
                raise AuthError({
                    'code': 403,
                    'description': 'You do not have permission to delete \
                                    another user\'s messages.'
                }, 403)
        # If the mailbox type is outbox
        elif(mailbox_type == 'outbox'):
            # If the user is attempting to delete another user's messages
            if(request_user.id != delete_item.from_id):
                raise AuthError({
                    'code': 403,
                    'description': 'You do not have permission to delete \
                                    another user\'s messages.'
                }, 403)
        # If the mailbox type is threads
        elif(mailbox_type == 'threads'):
            # If the user is attempting to delete another user's thread
            if((request_user.id != delete_item.user_1_id) and
               (request_user.id != delete_item.user_2_id)):
                raise AuthError({
                    'code': 403,
                    'description': 'You do not have permission to delete\
                                    another user\'s messages.'
                }, 403)

        # Try to delete the thread
        try:
            db_delete(delete_item)
        # If there's an error, abort
        except Exception as e:
            abort(500)

        return jsonify({
            'success': True,
            'deleted': item_id
        })

    # Endpoint: DELETE /messages/<mailbox_type>
    # Description: Clears the selected mailbox (deleting all messages in it).
    # Parameters: mailbox_type - Type of mailbox to clear.
    # Authorization: delete:messages.
    @app.route('/messages/<mailbox_type>', methods=['DELETE'])
    @requires_auth(['delete:messages'])
    def clear_mailbox(token_payload, mailbox_type):
        user_id = request.args.get('userID')

        # If there's no specified mailbox, abort
        if(mailbox_type is None):
            abort(404)

        # If there's no user ID, abort
        if(user_id is None):
            abort(400)

        current_user = User.query.filter(User.auth0_id ==
                                         token_payload['sub']).one_or_none()

        # If the user is attempting to delete another user's messages
        if(current_user.id != user_id):
            raise AuthError({
                'code': 403,
                'description': 'You do not have permission to delete another\
                                user\'s messages.'
            }, 403)

        # If the user is trying to clear their inbox
        if(mailbox_type == 'inbox'):
            num_messages = len(Message.query.filter(Message.for_id ==
                                                    user_id).all())
            # If there are no messages, abort
            if(num_messages == 0):
                abort(404)
        # If the user is trying to clear their outbox
        if(mailbox_type == 'outbox'):
            num_messages = len(Message.query.filter(Message.from_id ==
                                                    user_id).all())
            # If there are no messages, abort
            if(num_messages == 0):
                abort(404)
        # If the user is trying to clear their threads mailbox
        if(mailbox_type == 'threads'):
            num_messages = len(Thread.query.filter((Thread.user_1_id
                                                   == user_id) or
                                                   (Thread.user_2_id ==
                                                    user_id)).all())
            # If there are no messages, abort
            if(num_messages == 0):
                abort(404)

        # Try to clear the mailbox
        try:
            db_delete_all(mailbox_type, user_id)
        # If there's an error, abort
        except Exception as e:
            abort(500)

        return jsonify({
            'success': True,
            'userID': user_id,
            'deleted': num_messages
        })

    # Endpoint: GET /reports
    # Description: Gets the currently open reports.
    # Parameters: None.
    # Authorization: read:admin-board.
    @app.route('/reports')
    @requires_auth(['read:admin-board'])
    def get_open_reports(token_payload):
        user_reports_page = request.args.get('userPage', 1, type=int)
        post_reports_page = request.args.get('postPage', 1, type=int)

        # Get the user and post reports
        user_reports = joined_query('user reports')['return']
        post_reports = joined_query('post reports')['return']

        # Paginate user and posts reports
        paginated_user_data = paginate(user_reports, user_reports_page)
        paginated_user_reports = paginated_user_data[0]
        total_user_pages = paginated_user_data[1]
        paginated_post_data = paginate(post_reports, post_reports_page)
        paginated_post_reports = paginated_post_data[0]
        total_post_pages = paginated_post_data[1]

        return jsonify({
            'success': True,
            'userReports': paginated_user_reports,
            'totalUserPages': total_user_pages,
            'postReports': paginated_post_reports,
            'totalPostPages': total_post_pages
        })

    # Endpoint: POST /reports
    # Description: Add a new report to the database.
    # Parameters: None.
    # Authorization: post:report.
    @app.route('/reports', methods=['POST'])
    @requires_auth(['post:report'])
    def create_new_report(token_payload):
        report_data = json.loads(request.data)

        # If the reported item is a post
        if(report_data['type'].lower() == 'post'):
            reported_item = Post.query.filter(Post.id ==
                                              report_data['postID']).\
                                              one_or_none()

            # If this post doesn't exist, abort
            if(reported_item is None):
                abort(404)

            report = Report(type=report_data['type'], date=report_data['date'],
                            user_id=report_data['userID'],
                            post_id=report_data['postID'],
                            reporter=report_data['reporter'],
                            report_reason=report_data['reportReason'],
                            dismissed=False, closed=False)

            reported_item.open_report = True
        # Otherwise the reported item is a user
        else:
            reported_item = User.query.filter(User.id ==
                                              report_data['userID']).\
                                              one_or_none()

            # If this user doesn't exist, abort
            if(reported_item is None):
                abort(404)

            report = Report(type=report_data['type'], date=report_data['date'],
                            user_id=report_data['userID'],
                            reporter=report_data['reporter'],
                            report_reason=report_data['reportReason'],
                            dismissed=False, closed=False)

            reported_item.open_report = True

        # Try to add the report to the database
        try:
            db_add(report)
            db_update(reported_item)
            added_report = report.format()
        # If there's an error, abort
        except Exception as e:
            abort(500)

        return jsonify({
            'success': True,
            'report': added_report
        })

    # Endpoint: PATCH /reports/<report_id>
    # Description: Update the status of the report with the given ID.
    # Parameters: report_id - The ID of the report to update.
    # Authorization: read:admin-board.
    @app.route('/reports/<report_id>', methods=['PATCH'])
    @requires_auth(['read:admin-board'])
    def update_report_status(token_payload, report_id):
        updated_report = json.loads(request.data)
        report = Report.query.filter(Report.id == report_id).one_or_none()

        # If there's no report with that ID, abort
        if(report is None):
            abort(404)

        # If the item reported is a user
        if(report.type.lower() == 'user'):
            reported_item = User.query.filter(User.id ==
                                              updated_report['userID']).\
                                              one_or_none()
        # If the item reported is a post
        elif(report.type.lower() == 'post'):
            reported_item = Post.query.filter(Post.id ==
                                              updated_report['postID']).\
                                              one_or_none()

        # Set the dismissed and closed values to those of the updated report
        report.dismissed = updated_report['dismissed']
        report.closed = updated_report['closed']

        # Set the post/user's open_report value to false
        reported_item.open_report = False

        # Try to update the report in the database
        try:
            db_update(report)
            db_update(reported_item)
            return_report = report.format()
        # If there's an error, abort
        except Exception as e:
            abort(500)

        return jsonify({
            'success': True,
            'updated': return_report
        })

    # Endpoint: GET /filters
    # Description: Get a paginated list of filtered words.
    # Parameters: None.
    # Authorization: read:admin-board.
    @app.route('/filters')
    @requires_auth(['read:admin-board'])
    def get_filters(token_payload):
        page = request.args.get('page', 1, type=int)
        filtered_words = word_filter.get_words()

        # Paginate the filtered words
        words_per_page = 10
        start_index = (page - 1) * words_per_page
        paginated_words = filtered_words[start_index:(start_index+10)]
        total_pages = math.ceil(len(filtered_words) / 10)

        return jsonify({
            'success': True,
            'words': paginated_words,
            'total_pages': total_pages
        })

    # Endpoint: POST /filters
    # Description: Add a word or phrase to the list of filtered words.
    # Parameters: None.
    # Authorization: read:admin-board.
    @app.route('/filters', methods=['POST'])
    @requires_auth(['read:admin-board'])
    def add_filter(token_payload):
        new_filter = json.loads(request.data)['word']

        # If the word already exists in the filters list, abort
        if(new_filter in word_filter.get_full_list()):
            abort(409)

        # Try to add the word to the filters list
        try:
            word_filter.add_words(new_filter)
        # If there's an error, abort
        except Exception as e:
            abort(500)

        return jsonify({
            'success': True,
            'added': new_filter
        })

    # Endpoint: DELETE /filters/<filter_id>
    # Description: Delete a word from the filtered words list.
    # Parameters: filter_id - the index of the word to delete.
    # Authorization: read:admin-board.
    @app.route('/filters/<filter_id>', methods=['DELETE'])
    @requires_auth(['read:admin-board'])
    def delete_filter(token_payload, filter_id):
        # If there's no word in that index
        if(word_filter.get_words()[filter_id] is None):
            abort(404)

        # Otherwise, try to delete it
        try:
            removed = word_filter.remove_word(filter_id)
        # If there's an error, abort
        except Exception as e:
            abort(500)

        return jsonify({
            'success': True,
            'deleted': removed
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


app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
