import os
import json
import math
import sys
import urllib.request
from datetime import datetime, timedelta
from flask import Flask, request, abort, jsonify
from flask_cors import CORS
from pywebpush import webpush, WebPushException

from models import (
    create_db,
    Post,
    User,
    Message,
    Thread,
    Report,
    Notification,
    NotificationSub,
    add as db_add,
    update as db_update,
    delete_object as db_delete,
    delete_all as db_delete_all,
    joined_query
    )
from auth import (
    AuthError,
    requires_auth,
    check_mgmt_api_token,
    get_management_api_token,
    AUTH0_DOMAIN,
    API_AUDIENCE
    )
from filter import Filter
from validator import Validator, ValidationError

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    create_db(app)
    CORS(app, origins='')
    word_filter = Filter()
    validator = Validator({
        'post': {
            'max': 480,
            'min': 1
        },
        'message': {
            'max': 480,
            'min': 1
        },
        'user': {
            'max': 60,
            'min': 1
        },
        'report': {
            'max': 120,
            'min': 1
        }
    })

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

    # Send push notification
    def send_push_notification(user_id, data):
        vapid_key = os.environ.get('PRIVATE_KEY')
        expiry_time = datetime.timestamp(datetime.utcnow() +
                                         timedelta(hours=12))
        vapid_claims = {
            'sub': 'mailto:theobjectivistb@gmail.com',
            'exp': expiry_time
        }
        subscriptions = NotificationSub.query.filter(NotificationSub.user ==
                                                     user_id).all()
        notification_data = {
            'title': 'New ' + data['type'],
            'body': data['text']
        }

        # Try to send the push notification
        try:
            for subscription in subscriptions:
                sub_data = json.loads(subscription.subscription_data)
                webpush(subscription_info=sub_data,
                        data=json.dumps(notification_data),
                        vapid_private_key=vapid_key, vapid_claims=vapid_claims)
        # If there's an error, print the details
        except WebPushException as e:
            print(e)

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

        # Check if the search query is empty; if it is, abort
        length_validated = validator.check_length(search_query, 'Search query')
        # Check if the search query isn't a string; if it isn't, abort
        type_validated = validator.check_type(search_query, 'Search query')

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
        current_user = User.query.filter(User.auth0_id ==
                                         token_payload['sub']).one_or_none()

        # If the user is currently blocked, raise an AuthError
        if(current_user.blocked is True):
            raise AuthError({
                'code': 403,
                'description': 'You cannot create posts while being blocked.'
            }, 403)

        new_post_data = json.loads(request.data)
        blacklist_check = word_filter.blacklisted(new_post_data['text'])

        # If there's no blacklisted word, add the new post to the database
        if(blacklist_check['blacklisted'] is False):
            # Check the length adn  type of the post's text
            length_validated = validator.check_length(new_post_data['text'], 'post')
            type_validated = validator.check_type(new_post_data['text'], 'post text')

            # Create a new post object
            new_post = Post(user_id=new_post_data['userId'],
                            text=new_post_data['text'],
                            date=new_post_data['date'],
                            given_hugs=new_post_data['givenHugs'],
                            sent_hugs='')

            # Try to add the post to the database
            try:
                db_add(new_post)
                added_post = new_post.format()
            # If there's an error, abort
            except Exception as e:
                abort(500)
        # If there's a blacklisted word / phrase, alert the user
        else:
            num_issues = len(blacklist_check['indexes'])
            raise ValidationError({
                'code': 400,
                'description': 'Your text contains ' + str(num_issues) + ' \
                                forbidden term(s). Please fix your post\'s \
                                text and try again.'
            }, 400)

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
        # Check if the post ID isn't an integer; if it isn't, abort
        id_validated = validator.check_type(post_id, 'Post ID')

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
                    blacklist_check = word_filter.blacklisted(updated_post['text'])
                    # If there's no blacklisted word, add the new post to the database
                    if(blacklist_check['blacklisted'] is False):
                        # Check the length adn  type of the post's text
                        length_validated = validator.check_length(updated_post['text'], 'post')
                        type_validated = validator.check_type(updated_post['text'], 'post text')

                        original_post.text = updated_post['text']
                    # If there's a blacklisted word / phrase, alert the user
                    else:
                        num_issues = len(blacklist_check['indexes'])
                        raise ValidationError({
                            'code': 400,
                            'description': 'Your text contains ' +
                                            str(num_issues) + ' forbidden \
                                            term(s). Please fix your post\'s \
                                            text and try again.'
                        }, 400)
        # Otherwise, the user is allowed to edit any post, and thus text
        # editing is allowed
        else:
            # If the text was changed
            if(original_post.text != updated_post['text']):
                blacklist_check = word_filter.blacklisted(updated_post['text'])
                # If there's no blacklisted word, add the new post to the database
                if(blacklist_check['blacklisted'] is False):
                    # Check the length adn  type of the post's text
                    length_validated = validator.check_length(updated_post['text'], 'post')
                    type_validated = validator.check_type(updated_post['text'], 'post text')

                    original_post.text = updated_post['text']
                # If there's a blacklisted word / phrase, alert the user
                else:
                    num_issues = len(blacklist_check['indexes'])
                    raise ValidationError({
                        'code': 400,
                        'description': 'Your text contains ' +
                                        str(num_issues) + ' forbidden \
                                        term(s). Please fix your post\'s \
                                        text and try again.'
                    }, 400)

        # If a hug was added
        # Since anyone can give hugs, this doesn't require a permissions check
        if('givenHugs' in updated_post):
            original_hugs = original_post.given_hugs

            if(original_post.given_hugs != updated_post['givenHugs']):
                hugs = original_post.sent_hugs.split(' ')
                sent_hugs = list(filter(None, hugs))

                # If the current user already sent a hug on this post, abort
                if(str(current_user.id) in sent_hugs):
                    abort(409)

                # Otherwise, continue adding the new hug
                original_post.given_hugs = updated_post['givenHugs']
                current_user.given_hugs += 1
                post_author.received_hugs += 1
                sent_hugs.append(current_user.id)
                original_post.sent_hugs = ''.join([str(e) + ' ' for e in sent_hugs])

                # Create a notification for the user getting the hug
                today = datetime.now()
                notification = Notification(for_id=post_author.id,
                                            from_id=current_user.id,
                                            type='hug',
                                            text='You got a hug',
                                            date=today)
                push_notification = {
                    'type': 'hug',
                    'text': current_user.display_name + ' sent you a hug'
                }
                notification_for = post_author.id

        # If there's a 'closeReport' value, this update is the result of
        # a report, which means the report with the given ID needs to be
        # closed.
        if('closeReport' in updated_post):
            open_report = Report.query.filter(Report.id ==
                                              updated_post['closeReport']).\
                                              one_or_none()
            open_report.dismissed = False
            open_report.closed = True
            original_post.open_report = False

        # Try to update the database
        try:
            # Update users' and post's data
            db_update(original_post)
            db_update(current_user)
            db_update(post_author)
            if('closeReport' in updated_post):
                db_update(open_report)
            # If there was an added hug, add the new notification
            if('givenHugs' in updated_post):
                if(original_hugs != updated_post['givenHugs']):
                    send_push_notification(user_id=notification_for,
                                           data=push_notification)
                    db_add(notification)
            db_updated_post = original_post.format()
        # If there's an error, abort
        except Exception as e:
            print(sys.exc_info())
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
        # Check if the post ID isn't an integer; if it isn't, abort
        id_validated = validator.check_type(post_id, 'Post ID')

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
                    # If it's past the user's release date, unblock them
                    current_date = datetime.now()
                    if(user.release_date < current_date):
                        user.blocked = False
                        user.release_date = None

                        # Try to update the database
                        try:
                            db_update(user)
                        # If there's an error, abort
                        except Exception as e:
                            abort(500)
                    # Otherwise, format the user's data
                    else:
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
            # Try to convert it to a number; if it's a number, it's a
            # regular ID, so try to find the user with that ID
            try:
                int(user_id)
                user_data = User.query.filter(User.id == user_id).one_or_none()

                # If there's no user with that ID either, abort
                if(user_data is None):
                    abort(404)
            # Otherwise, it's an Auth0 ID and it's the user's first login,
            # so just return a 'not found' message
            except Exception as e:
                abort(404)

        # If the user is currently blocked, compare their release date to
        # the current date and time.
        if(user_data.release_date):
            current_date = datetime.now()
            # If it's past the user's release date, unblock them
            if(user_data.release_date < current_date):
                user_data.blocked = False
                user_data.release_date = None

                # Try to update the database
                try:
                    db_update(user_data)
                # If there's an error, abort
                except Exception as e:
                    abort(500)

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
                        role='user',last_notifications_read=datetime.now(),
                        login_count=0,blocked=False,open_report=False,
                        auto_refresh=True,refresh_rate=20,push_enabled=False)

        # Try to add the post to the database
        try:
            db_add(new_user)
            added_user = new_user.format()
        # If there's an error, abort
        except Exception as e:
            abort(500)

        # Get the Management API token and check that it's valid
        MGMT_API_TOKEN = check_mgmt_api_token()
        # If the token expired, get and check a
        if(MGMT_API_TOKEN.lower() == 'token expired'):
            get_management_api_token()
            MGMT_API_TOKEN = check_mgmt_api_token()

        # Try to replace the user's role in Auth0's systems
        try:
            # Remove the 'new user' role from the user's payload
            data = "{ \"roles\": [ \"rol_QeyIIcHg326Vv1Ay\" ] }"
            url = "https://" + AUTH0_DOMAIN + "/api/v2/users/" + user_data['auth0Id'] + "/roles"
            auth_header = "Bearer " + MGMT_API_TOKEN
            headers = {
                'content-type': "application/json",
                'authorization': auth_header,
                'cache-control': "no-cache"
            }
            req = urllib.request.Request(url, data.encode('utf-8'), headers, method='DELETE')
            f = urllib.request.urlopen(req)
            for x in f:
                print(x)
            f.close()

            # Then add the 'user' role to the user's payload
            data = "{ \"roles\": [ \"rol_BhidDxUqlXDx8qIr\" ] }"
            url = "https://" + AUTH0_DOMAIN + "/api/v2/users/" + user_data['auth0Id'] + "/roles"
            auth_header = "Bearer " + MGMT_API_TOKEN
            headers = {
                'content-type': "application/json",
                'authorization': auth_header,
                'cache-control': "no-cache"
            }
            req = urllib.request.Request(url, data.encode('utf-8'), headers, method='POST')
            f = urllib.request.urlopen(req)
            for x in f:
                print(x)
            f.close()
        # If there's an error, print it
        except Exception as e:
            print(e)

        return jsonify({
            'success': True,
            'user': added_user
        })

    # Endpoint: PATCH /users/all/<user_id>
    # Description: Updates a user in the database.
    # Parameters: user_id - ID of the user to update.
    # Authorization: patch:user or patch:any-user.
    @app.route('/users/all/<user_id>', methods=['PATCH'])
    @requires_auth(['patch:user', 'patch:any-user'])
    def edit_user(token_payload, user_id):
        # if there's no user ID provided, abort with 'Bad Request'
        if(user_id is None):
            abort(404)
        # Check if the user ID isn't an integer; if it isn't, abort
        id_validated = validator.check_type(user_id, 'User ID')

        updated_user = json.loads(request.data)
        original_user = User.query.filter(User.id == user_id).one_or_none()
        current_user = User.query.filter(User.auth0_id ==
                                         token_payload['sub']).one_or_none()

        # If the user being updated was given a hug, also update the current
        # user's "given hugs" value, as they just gave a hug
        if('receivedH' in updated_user and 'givenH' in updated_user):
            original_hugs = original_user.received_hugs
            if(original_user.received_hugs != updated_user['receivedH']):
                current_user.given_hugs += 1
                today = datetime.now()
                notification = Notification(for_id=original_user.id,
                                            from_id=current_user.id,
                                            type='hug',
                                            text='You got a hug',
                                            date=today)
                push_notification = {
                    'type': 'hug',
                    'text': current_user.display_name + ' sent you a hug'
                }
                notification_for = original_user.id

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
                    # If it's not the current user, abort
                    if(token_payload['sub'] != original_user.auth0_id):
                        raise AuthError({
                            'code': 403,
                            'description': 'You do not have permission to \
                                            edit this user\'s display name.'
                            }, 403)
                    # If it is, let them update user data
                    else:
                        # Check the length adn  type of the user's display name
                        length_validated = validator.check_length(updated_user['displayName'], 'display name')
                        type_validated = validator.check_type(updated_user['displayName'], 'display name')

                        original_user.display_name = updated_user['displayName']
                # if the user can edit anyone or the user is trying to
                # update their own name
                else:
                    # Check the length adn  type of the user's display name
                    length_validated = validator.check_length(updated_user['displayName'], 'display name')
                    type_validated = validator.check_type(updated_user['displayName'], 'display name')

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

        # If there's a 'closeReport' value, this update is the result of
        # a report, which means the report with the given ID needs to be
        # closed.
        if('closeReport' in updated_user):
            open_report = Report.query.filter(Report.id ==
                                              updated_user['closeReport']).\
                                              one_or_none()
            open_report.dismissed = False
            open_report.closed = True
            original_user.open_report = False

        # If the user is changing their auto-refresh settings
        if('autoRefresh' in updated_user):
            original_user.auto_refresh = updated_user['autoRefresh']

        # If the user is changing their push notifications setting
        if('pushEnabled' in updated_user):
            original_user.push_enabled = updated_user['pushEnabled']

        # If the user is changing their auto-refresh settings
        if('refreshRate' in updated_user):
            original_user.refresh_rate = updated_user['refreshRate']

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
            # Update users' data
            db_update(original_user)
            db_update(current_user)
            if('closeReport' in updated_user):
                db_update(open_report)
            # If the user was given a hug, add a new notification
            if('receivedH' in updated_user and 'givenH' in updated_user):
                if(original_hugs != updated_user['receivedH']):
                    send_push_notification(user_id=notification_for,
                                           data=push_notification)
                    db_add(notification)
            updated_user = original_user.format()
        # If there's an error, abort
        except Exception as e:
            abort(500)

        return jsonify({
            'success': True,
            'updated': updated_user
        })

    # Endpoint: GET /users/all/<user_id>/posts
    # Description: Gets a specific user's posts.
    # Parameters: user_id - whose posts to fetch.
    # Authorization: read:user.
    @app.route('/users/all/<user_id>/posts')
    @requires_auth(['read:user'])
    def get_user_posts(token_payload, user_id):
        page = request.args.get('page', 1, type=int)

        # if there's no user ID provided, abort with 'Bad Request'
        if(user_id is None):
            abort(400)

        id_validated = validator.check_type(user_id, 'User ID')

        # Gets all posts written by the given user
        user_posts = Post.query.filter(Post.user_id == user_id).order_by(Post.date).all()
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

    # Endpoint: DELETE /users/all/<user_id>/posts
    # Description: Deletes a specific user's posts.
    # Parameters: user_id - whose posts to delete.
    # Authorization: delete:my-post or delete:any-post
    @app.route('/users/all/<user_id>/posts', methods=['DELETE'])
    @requires_auth(['delete:my-post', 'delete:any-post'])
    def delete_user_posts(token_payload, user_id):
        id_validated = validator.check_type(user_id, 'User ID')
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

        blacklist_check = word_filter.blacklisted(message_data['messageText'])

        # If there's a blacklisted word / phrase, alert the user
        if(blacklist_check['blacklisted'] is True):
            num_issues = len(blacklist_check['indexes'])
            raise ValidationError({
                'code': 400,
                'description': 'Your message contains ' + str(num_issues) + ' \
                                forbidden term(s). Please fix your post\'s \
                                text and try again.'
            }, 400)

        # Check the length adn  type of the message text
        length_validated = validator.check_length(message_data['messageText'], 'message')
        type_validated = validator.check_type(message_data['messageText'], 'message text')

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

        # Create a new message
        new_message = Message(from_id=message_data['fromId'],
                              for_id=message_data['forId'],
                              text=message_data['messageText'],
                              date=message_data['date'],
                              thread=thread_id)

        # Create a notification for the user getting the message
        notification = Notification(for_id=message_data['forId'],
                                    from_id=message_data['fromId'],
                                    type='message',
                                    text='You have a new message',
                                    date=message_data['date'])
        push_notification = {
            'type': 'message',
            'text': logged_user.display_name + ' sent you a message'
        }
        notification_for = message_data['forId']

        # Try to add the message to the database
        try:
            db_add(new_message)
            db_add(notification)
            send_push_notification(user_id=notification_for,
                                   data=push_notification)
            sent_message = new_message.format()
        # If there's an error, abort
        except Exception as e:
            abort(500)

        return jsonify({
            'success': True,
            'message': sent_message
        })

    # Endpoint: DELETE /messages/<mailbox_type>/<item_id>
    # Description: Deletes a message/thread from the database.
    # Parameters: mailbox_type - the type of message to delete.
    #             item_id - ID of the message/thread to delete.
    # Authorization: delete:messages.
    @app.route('/messages/<mailbox_type>/<item_id>', methods=['DELETE'])
    @requires_auth(['delete:messages'])
    def delete_thread(token_payload, mailbox_type, item_id):
        # Variable indicating whether to delete the message from the databse
        # or leave it in it (for the other user)
        delete_message = False

        # If there's no thread ID, abort
        if(item_id is None):
            abort(405)

        id_validated = validator.check_type(item_id, 'Message ID')

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
            # Otherwise, set the appropriate deleted property
            else:
                delete_item.for_deleted = True
        # If the mailbox type is outbox
        elif(mailbox_type == 'outbox'):
            # If the user is attempting to delete another user's messages
            if(request_user.id != delete_item.from_id):
                raise AuthError({
                    'code': 403,
                    'description': 'You do not have permission to delete \
                                    another user\'s messages.'
                }, 403)
            # Otherwise, set the appropriate deleted property
            else:
                delete_item.from_deleted = True
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
            # Otherwise, if the current user is the thread's user_1, set
            # the appropriate deleted property
            elif(request_user.id == delete_item.user_1_id):
                delete_item.user_1_deleted = True
            # Or, if the current user is the thread's user_2, set
            # the appropriate deleted property
            else:
                delete_item.user_2_deleted = True

        # Check the type of item and which user deleted the message/thread
        if(type(delete_item) is Message):
            # Check if both users deleted the message
            if(delete_item.for_deleted and delete_item.from_deleted):
                delete_message = True
            else:
                delete_message = False
        elif(type(delete_item) is Thread):
            # Check if both users deleted the thread
            if(delete_item.user_1_deleted and delete_item.user_2_deleted):
                delete_message = True
            else:
                delete_message = False

        # Try to delete the thread
        try:
            # If both users deleted the message/thread, delete it from
            # the database entirely
            if(delete_message):
                db_delete(delete_item)
            # Otherwise, just update the appropriate deleted property
            else:
                db_update(delete_item, {'set_deleted': True,
                                        'user_id': request_user.id})
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

        # Check the length adn  type of the report reason
        length_validated = validator.check_length(report_data['reportReason'], 'report')
        type_validated = validator.check_type(report_data['reportReason'], 'report reason')

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

        id_validated = validator.check_type(report_id, 'Report ID')

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

        # If the item wasn't deleted, set the post/user's open_report
        # value to false
        if(reported_item):
            reported_item.open_report = False

        # Try to update the report in the database
        try:
            db_update(report)

            # If the item wasn't deleted, set the post/user's open_report
            # value to false
            if(reported_item):
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

        # Check if the filter is empty; if it is, abort
        length_validated = validator.check_length(new_filter, 'Phrase to filter')

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
        id_validated = validator.check_type(filter_id, 'Filter ID')

        # If there's no word in that index
        if(word_filter.get_words()[int(filter_id)] is None):
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

    # Endpoint: GET /notifications
    # Description: Gets the latest notifications for the given user.
    # Parameters: None.
    # Authorization: read:messages.
    @app.route('/notifications')
    @requires_auth(['read:messages'])
    def get_latest_notifications(token_payload):
        silent_refresh = request.args.get('silentRefresh', True)
        user = User.query.filter(User.auth0_id == token_payload['sub']).\
            one_or_none()

        # If there's no user with that ID, abort
        if(user is None):
            abort(404)

        # Get user notifications
        notifications = joined_query('notifications',
                                     {'user_id': user.id,
                                      'last_read':
                                      user.last_notifications_read})['return']

        # Updates the user's 'last read' time only if this fetch was
        # triggered by the user (meaning, they're looking at the
        # notifications tab right now).
        if(silent_refresh == 'false'):
            # Update the user's last-read date
            try:
                user.last_notifications_read = datetime.now()
                db_update(user)
            # If there's an error, abort
            except Exception as e:
                abort(500)

        return jsonify({
            'success': True,
            'notifications': notifications
        })

    # Endpoint: POST /notifications
    # Description: Add a new PushSubscription to the database (for push
    #              notifications).
    # Parameters: None.
    # Authorization: read:messages.
    @app.route('/notifications', methods=['POST'])
    @requires_auth(['read:messages'])
    def add_notification_subscription(token_payload):
        # if the request is empty, return 204. This happens due to a bug
        # in the frontend that causes the request to be sent twice, once
        # with subscription data and once with an empty object
        if(not request.data):
            return ('', 204)

        subscription_json = request.data.decode('utf8').replace("'", '"')
        subscription_data = json.loads(subscription_json)
        user = User.query.filter(User.auth0_id == token_payload['sub']).\
            one_or_none()

        # If there's no user with that ID, abort
        if(user is None):
            abort(404)

        # Create a new subscription object with the given data
        subscription = NotificationSub(user=user.id,
                                       endpoint=subscription_data['endpoint'],
                                       subscription_data=json.dumps(
                                                         subscription_data))

        # Try to add it to the database
        try:
            subscribed = user.display_name
            db_add(subscription)
        # If there's an error, abort
        except Exception as e:
            abort(500)

        return {
            'success': True,
            'subscribed': subscribed
        }

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

    # Validation error handler
    @app.errorhandler(ValidationError)
    def validation_error(error):
        return jsonify({
            'success': False,
            'code': error.status_code,
            'message': error.error
        }), error.status_code

    return app


app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
