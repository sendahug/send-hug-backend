# MIT License
#
# Copyright (c) 2020 Send A Hug
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# The provided Software is separate from the idea behind its website. The Send A Hug
# website and its underlying design and ideas are owned by Send A Hug group and
# may not be sold, sub-licensed or distributed in any way. The Software itself may
# be adapted for any purpose and used freely under the given conditions.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import unittest
import json
import os
import urllib.request
import base64
import time
import sys
from flask_sqlalchemy import SQLAlchemy
from sh import pg_restore

from app import create_app
from models import create_db, Post, User, Message

AUTH0_DOMAIN = os.environ.get('AUTH0_DOMAIN')
API_AUDIENCE = os.environ.get('API_AUDIENCE')
TEST_CLIENT_ID = os.environ.get('TEST_CLIENT_ID')
TEST_CLIENT_SECRET = os.environ.get('TEST_CLIENT_SECRET')

# Tokens
access_tokens = {
    'user_jwt': '',
    'moderator_jwt': '',
    'admin_jwt': '',
    'blocked_jwt': ''
}

# Headers
malformed_header = {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer'
                    }
user_header = {
               'Content-Type': 'application/json',
               'Authorization': 'Bearer ' + access_tokens['user_jwt']
              }
moderator_header = {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + access_tokens['moderator_jwt']
                   }
admin_header = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + access_tokens['admin_jwt']
               }

blocked_header = {
                  'Content-Type': 'application/json',
                  'Authorization': 'Bearer ' + access_tokens['blocked_jwt']
                 }


# Get Auth0 access tokens for each of the users to be able to ru
# the tests.
def get_user_tokens():
    headers = {
        'content-type': "application/x-www-form-urlencoded"
    }

    roles = ['user', 'moderator', 'admin', 'blocked']
    for role in roles:
        url = "https://" + AUTH0_DOMAIN + "/oauth/token"
        print(url)

        # Get the user's username and password
        role_username = os.environ.get(role.upper() + '_USERNAME')
        role_password = os.environ.get(role.upper() + '_PASSWORD')

        data = "grant_type=password&username=" + role_username + \
               "&password=" + role_password + "&audience=" + API_AUDIENCE + \
               "&client_id=" + TEST_CLIENT_ID + "&client_secret=" +\
                TEST_CLIENT_SECRET

        # make the request and get the token
        req = urllib.request.Request(url, data.encode('utf-8'), headers, method='POST')
        f = urllib.request.urlopen(req)
        response_data = f.read()
        token_data = response_data.decode('utf8').replace("'", '"')
        token = json.loads(token_data)['access_token']
        access_tokens[role + '_jwt'] = token
        f.close()

    # Set the authorisation headers with the newly fetched JWTs
    user_header['Authorization'] = 'Bearer ' + access_tokens['user_jwt']
    moderator_header['Authorization'] = 'Bearer ' + access_tokens['moderator_jwt']
    admin_header['Authorization'] = 'Bearer ' + access_tokens['admin_jwt']
    blocked_header['Authorization'] = 'Bearer ' + access_tokens['blocked_jwt']


# Sample users data
sample_user_id = str(1)
sample_user_auth0_id = 'auth0|5ed34765f0b8e60c8e87ca62'
sample_moderator_id = str(5)
sample_moderator_auth0_id = 'auth0|5ede3e7a0793080013259050'
sample_admin_id = str(4)
sample_admin_auth0_id = 'auth0|5ed8e3d0def75d0befbc7e50'
blocked_user_id = str(20)

# Item Samples
new_post = {
    "userId": 0,
    "text": "test post",
    "date": "Sun Jun 07 2020 15:57:45",
    "givenHugs": 0
}

updated_post = {
    "userId": 0,
    "text": "test post",
    "date": "Sun Jun 07 2020 15:57:45",
    "givenHugs": 0
}

report_post = {
    "user_id": 0,
    "text": "test post",
    "date": "Sun Jun 07 2020 15:57:45",
    "givenHugs": 0,
    "closeReport": 1
}

new_user = '{\
"id": "auth0|5edf778e56d062001335196e",\
"displayName": "user",\
"receivedH": 0,\
"givenH": 0,\
"loginCount": 0 }'

updated_user = {
    "id": 0,
    "displayName": "",
    "receivedH": 0,
    "givenH": 0,
    "loginCount": 0
}

updated_unblock_user = {
    "id": 0,
    "displayName": "hello",
    "receivedH": 0,
    "givenH": 0,
    "loginCount": 0,
    "blocked": False,
    "releaseDate": None
}

updated_display = {
    "id": 0,
    "displayName": "meow",
    "receivedH": 0,
    "givenH": 0,
    "loginCount": 0
}

new_message = {
    "fromId": 0,
    "forId": 0,
    "messageText": "meow",
    "date": "Sun Jun 07 2020 15:57:45"
}

new_report = {
    "type": "Post",
    "userID": 0,
    "postID": 0,
    "reporter": 0,
    "reportReason": "It is inappropriate",
    "date": "Sun Jun 07 2020 15:57:45"
}

new_subscription = {
    "endpoint": "https://fcm.googleapis.com/fcm/send/epyhl2GD",
    "expirationTime": None,
    "keys": {
            "p256dh": "fdsfd",
            "auth": "dfs"
            }
}


# App testing
class TestHugApp(unittest.TestCase):
    # Setting up the suite
    @classmethod
    def setUpClass(cls):
        try:
            get_user_tokens()
        except Exception as e:
            print(sys.exc_info())

    # Setting up each test
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client
        self.database_path = 'postgresql://localhost:5432/test-capstone'

        create_db(self.app, self.database_path)
        pg_restore('-d', 'test-capstone', 'capstone_db', '-Fc', '-c', '--no-owner')

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    # Executed after each test
    def tearDown(self):
        # binds the app to the current context
        with self.app.app_context():
            self.db.drop_all()
            self.db.session.close()

    # Index Route Tests ('/', GET)
    # -------------------------------------------------------
    def test_get_home_page(self):
        response = self.client().get('/')
        response_data = json.loads(response.data)

        self.assertTrue(response_data['success'])
        self.assertTrue(response_data['recent'])
        self.assertTrue(response_data['suggested'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response_data['recent']), 10)
        self.assertEqual(len(response_data['suggested']), 10)

    # Search Route Tests ('/', POST)
    # -------------------------------------------------------
    # Run a search
    def test_search(self):
        response = self.client().post('/', data=json.dumps({'search': 'user'}))
        response_data = json.loads(response.data)

        self.assertTrue(response_data['success'])
        self.assertTrue(response_data['users'])
        self.assertTrue(response_data['posts'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['post_results'], 1)
        self.assertEqual(response_data['user_results'], 4)

    # Run a search which returns multiple pages of results
    def test_search_multiple_pages(self):
        response = self.client().post('/', data=json.dumps({'search': 'test'}))
        response_data = json.loads(response.data)

        self.assertTrue(response_data['success'])
        self.assertTrue(response_data['posts'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['post_results'], 13)
        self.assertEqual(len(response_data['posts']), 5)
        self.assertEqual(response_data['total_pages'], 3)
        self.assertEqual(response_data['current_page'], 1)
        self.assertEqual(response_data['user_results'], 0)

    # Run a search which returns multiple pages of results - get page 2
    def test_search_multiple_pages_page_2(self):
        response = self.client().post('/?page=2', data=json.dumps({'search': 'test'}))
        response_data = json.loads(response.data)

        self.assertTrue(response_data['success'])
        self.assertTrue(response_data['posts'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['post_results'], 13)
        self.assertEqual(len(response_data['posts']), 5)
        self.assertEqual(response_data['total_pages'], 3)
        self.assertEqual(response_data['current_page'], 2)
        self.assertEqual(response_data['user_results'], 0)

    # Create Post Route Tests ('/posts', POST)
    # -------------------------------------------------------
    # Attempt to create a post without auth header
    def test_send_post_no_auth(self):
        response = self.client().post('/posts', data=json.dumps(new_post))
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 401)

    # Attempt to create a post with a malformed auth header
    def test_send_post_malformed_auth(self):
        response = self.client().post('/posts', headers=malformed_header,
                                      data=json.dumps(new_post))
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 401)

    # Attempt to create a post with a user's JWT
    def test_send_post_as_user(self):
        post = new_post
        post['userId'] = sample_user_id
        response = self.client().post('/posts', headers=user_header,
                                      data=json.dumps(post))
        response_data = json.loads(response.data)
        response_post = response_data['posts']

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_post['text'], post['text'])

    # Attempt to create a post with a moderator's JWT
    def test_send_post_as_mod(self):
        post = new_post
        post['userId'] = sample_moderator_id
        response = self.client().post('/posts', headers=moderator_header,
                                      data=json.dumps(post))
        response_data = json.loads(response.data)
        response_post = response_data['posts']

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_post['text'], post['text'])

    # Attempt to create a post with an admin's JWT
    def test_send_post_as_admin(self):
        post = new_post
        post['userId'] = sample_admin_id
        response = self.client().post('/posts', headers=admin_header,
                                      data=json.dumps(post))
        response_data = json.loads(response.data)
        response_post = response_data['posts']

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_post['text'], post['text'])

    # Attempt to create a post with a blocked user's JWT
    def test_send_post_as_blocked(self):
        post = new_post
        post['userId'] = blocked_user_id
        response = self.client().post('/posts', headers=blocked_header,
                                      data=json.dumps(post))
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 403)

    # Update Post Route Tests ('/posts/<post_id>', PATCH)
    # -------------------------------------------------------
    # Attempt to update a post with no authorisation header
    def test_update_post_no_auth(self):
        response = self.client().patch('/posts/4',
                                       data=json.dumps(updated_post))
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 401)

    # Attempt to update a post with a malformed auth header
    def test_update_post_malformed_auth(self):
        response = self.client().patch('/posts/4', headers=malformed_header,
                                       data=json.dumps(updated_post))
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 401)

    # Attempt to update the user's post (with same user's JWT)
    def test_update_own_post_as_user(self):
        post = updated_post
        post['userId'] = sample_user_id
        post['givenHugs'] = 2
        response = self.client().patch('/posts/4', headers=user_header,
                                       data=json.dumps(post))
        response_data = json.loads(response.data)
        post_text = response_data['updated']

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(post_text['text'], post['text'])

    # Attempt to update another user's post (with user's JWT)
    def test_update_other_users_post_as_user(self):
        post = updated_post
        post['userId'] = sample_moderator_id
        post['givenHugs'] = 1
        response = self.client().patch('/posts/13', headers=user_header,
                                       data=json.dumps(post))
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 403)

    # Attempt to update the moderator's post (with same moderator's JWT)
    def test_update_own_post_as_mod(self):
        post = updated_post
        post['userId'] = sample_moderator_id
        post['givenHugs'] = 1
        response = self.client().patch('/posts/13', headers=moderator_header,
                                       data=json.dumps(post))
        response_data = json.loads(response.data)
        post_text = response_data['updated']

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(post_text['text'], post['text'])

    # Attempt to update another user's post (with moderator's JWT)
    def test_update_other_users_post_as_mod(self):
        post = updated_post
        post['userId'] = sample_user_id
        post['givenHugs'] = 2
        response = self.client().patch('/posts/4', headers=moderator_header,
                                       data=json.dumps(post))
        response_data = json.loads(response.data)
        post_text = response_data['updated']

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(post_text['text'], post['text'])

    # Attempt to close the report on another user's post (with mod's JWT)
    def test_update_other_users_post_report_as_mod(self):
        post = report_post
        post['userId'] = sample_user_id
        post['givenHugs'] = 2
        response = self.client().patch('/posts/4', headers=moderator_header,
                                       data=json.dumps(post))
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 403)

    # Attempt to update the admin's post (with same admin's JWT)
    def test_update_own_post_as_admin(self):
        post = updated_post
        post['userId'] = sample_admin_id
        post['givenHugs'] = 2
        response = self.client().patch('/posts/23', headers=admin_header,
                                       data=json.dumps(post))
        response_data = json.loads(response.data)
        post_text = response_data['updated']

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(post_text['text'], post['text'])

    # Attempt to update another user's post (with admin's JWT)
    def test_update_other_users_post_as_admin(self):
        post = updated_post
        post['userId'] = sample_user_id
        post['givenHugs'] = 2
        response = self.client().patch('/posts/4', headers=admin_header,
                                       data=json.dumps(post))
        response_data = json.loads(response.data)
        post_text = response_data['updated']

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(post_text['text'], post['text'])

    # Attempt to close the report on another user's post (with admin's JWT)
    def test_update_other_users_post_report_as_admin(self):
        post = report_post
        post['userId'] = sample_user_id
        post['givenHugs'] = 2
        response = self.client().patch('/posts/4', headers=admin_header,
                                       data=json.dumps(post))
        response_data = json.loads(response.data)
        post_text = response_data['updated']

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(post_text['text'], post['text'])

    # Attempt to update a post with no ID (with admin's JWT)
    def test_update_no_id_post_as_admin(self):
        post = updated_post
        post['userId'] = sample_user_id
        response = self.client().patch('/posts/', headers=admin_header,
                                       data=json.dumps(post))
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 404)

    # Attempt to update a post that doesn't exist (with admin's JWT)
    def test_update_nonexistent_post_as_admin(self):
        post = updated_post
        post['userId'] = sample_user_id
        response = self.client().patch('/posts/100', headers=admin_header,
                                       data=json.dumps(post))
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 404)

    # Delete Post Route Tests ('/posts/<post_id>', DELETE)
    # -------------------------------------------------------
    # Attempt to delete a post with no authorisation header
    def test_delete_post_no_auth(self):
        response = self.client().delete('/posts/3')
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 401)

    # Attempt to delete a post with a malformed auth header
    def test_delete_post_malformed_auth(self):
        response = self.client().delete('/posts/3', headers=malformed_header)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 401)

    # Attempt to delete the user's post (with same user's JWT)
    def test_delete_own_post_as_user(self):
        response = self.client().delete('/posts/2', headers=user_header)
        response_data = json.loads(response.data)

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['deleted'], '2')

    # Attempt to delete another user's post (with user's JWT)
    def test_delete_other_users_post_as_user(self):
        response = self.client().delete('/posts/12', headers=user_header)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 403)

    # Attempt to delete the moderator's post (with same moderator's JWT)
    def test_delete_own_post_as_mod(self):
        response = self.client().delete('/posts/12', headers=moderator_header)
        response_data = json.loads(response.data)

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['deleted'], '12')

    # Attempt to delete another user's post (with moderator's JWT)
    def test_delete_other_users_post_as_mod(self):
        response = self.client().delete('/posts/25', headers=moderator_header)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 403)

    # Attempt to delete the admin's post (with same admin's JWT)
    def test_delete_own_post_as_admin(self):
        response = self.client().delete('/posts/23', headers=admin_header)
        response_data = json.loads(response.data)

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['deleted'], '23')

    # Attempt to delete another user's post (with admin's JWT)
    def test_delete_other_users_post_as_admin(self):
        response = self.client().delete('/posts/1', headers=admin_header)
        response_data = json.loads(response.data)

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['deleted'], '1')

    # Attempt to delete a post with no ID (with admin's JWT)
    def test_delete_no_id_post_as_admin(self):
        response = self.client().delete('/posts/', headers=admin_header)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 404)

    # Attempt to delete a post that doesn't exist (with admin's JWT)
    def test_delete_nonexistent_post_as_admin(self):
        response = self.client().delete('/posts/100', headers=admin_header)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 404)

    # Get Posts by Type Tests ('posts/<type>', GET)
    # -------------------------------------------------------
    # Attempt to get page 1 of full new posts
    def test_get_full_new_posts(self):
        response = self.client().get('/posts/new')
        response_data = json.loads(response.data)

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response_data['posts']), 5)
        self.assertEqual(response_data['total_pages'], 5)

    # Attempt to get page 2 of full new posts
    def test_get_full_new_posts_page_2(self):
        response = self.client().get('/posts/new?page=2')
        response_data = json.loads(response.data)

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response_data['posts']), 5)
        self.assertEqual(response_data['total_pages'], 5)

    # Attempt to get page 1 of full suggested posts
    def test_get_full_suggested_posts(self):
        response = self.client().get('/posts/suggested')
        response_data = json.loads(response.data)

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response_data['posts']), 5)
        self.assertEqual(response_data['total_pages'], 5)

    # Attempt to get page 2 of full suggested posts
    def test_get_full_suggested_posts_page_2(self):
        response = self.client().get('/posts/suggested?page=2')
        response_data = json.loads(response.data)

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response_data['posts']), 5)
        self.assertEqual(response_data['total_pages'], 5)

    # Get Users by Type Tests ('/users/<type>', GET)
    # -------------------------------------------------------
    # Attempt to get list of users without auth header
    def test_get_user_list_no_auth(self):
        response = self.client().get('/users/blocked')
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 401)

    # Attempt to get list of users with malformed auth header
    def test_get_user_list_malformed_auth(self):
        response = self.client().get('/users/blocked',
                                     headers=malformed_header)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 401)

    # Attempt to get list of users with user's auth header
    def test_get_user_list_as_user(self):
        response = self.client().get('/users/blocked', headers=user_header)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 403)

    # Attempt to get list of users with moderator's auth header
    def test_get_user_list_as_mod(self):
        response = self.client().get('/users/blocked',
                                     headers=moderator_header)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 403)

    # Attempt to get list of users with admin's auth header
    def test_get_user_list_as_admin(self):
        response = self.client().get('/users/blocked',
                                     headers=admin_header)
        response_data = json.loads(response.data)

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['total_pages'], 1)

    # Get User Data Tests ('/users/all/<user_id>', GET)
    # -------------------------------------------------------
    # Attempt to get a user's data without auth header
    def test_get_user_data_no_auth(self):
        response = self.client().get('/users/all/1')
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 401)

    # Attempt to get a user's data with malformed auth header
    def test_get_user_data_malformed_auth(self):
        response = self.client().get('/users/all/1', headers=malformed_header)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 401)

    # Attempt to get a user's data with a user's JWT
    def test_get_user_data_as_user(self):
        response = self.client().get('/users/all/' + sample_user_auth0_id,
                                     headers=user_header)
        response_data = json.loads(response.data)
        user_data = response_data['user']

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(user_data['id'], int(sample_user_id))

    # Attempt to get a user's data with a moderator's JWT
    def test_get_user_data_as_mod(self):
        response = self.client().get('/users/all/' + sample_moderator_auth0_id,
                                     headers=moderator_header)
        response_data = json.loads(response.data)
        user_data = response_data['user']

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(user_data['id'], int(sample_moderator_id))

    # Attempt to get a user's data with an admin's JWT
    def test_get_user_data_as_admin(self):
        response = self.client().get('/users/all/' + sample_admin_auth0_id,
                                     headers=admin_header)
        response_data = json.loads(response.data)
        user_data = response_data['user']

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(user_data['id'], int(sample_admin_id))

    # Attempt to get a user's data with no ID (with admin's JWT)
    def test_get_no_id_user_as_admin(self):
        response = self.client().get('/users/all/', headers=admin_header)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 404)

    # Attempt to get a nonexistent user's data (with admin's JWT)
    def test_get_nonexistent_user_as_admin(self):
        response = self.client().get('/users/all/100', headers=admin_header)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 404)

    # Create User Tests ('/users', POST)
    # -------------------------------------------------------
    # Attempt to create a user without auth header
    def test_create_user_no_auth(self):
        response = self.client().post('/users', data=new_user)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 401)

    # Attempt to create a user with malformed auth header
    def test_create_user_malformed_auth(self):
        response = self.client().post('/users', headers=malformed_header,
                                      data=new_user)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 401)

    # Attempt to create a user with user's JWT
    def test_create_user_as_user(self):
        response = self.client().post('/users', headers=user_header,
                                      data=new_user)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 403)

    # Attempt to create a user with moderator's JWT
    def test_create_user_as_moderator(self):
        response = self.client().post('/users', headers=moderator_header,
                                      data=new_user)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 403)

    # Attempt to create a user with admin's JWT
    def test_create_user_as_damin(self):
        response = self.client().post('/users', headers=admin_header,
                                      data=new_user)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 403)

    # Attempt to create a user with new user's JWT
    # This test is performed as fallback; since the new user -> user change
    # is done automatically, it's no longer needed, but in case of an error
    # adjusting a user's roles, it's important to make sure they still
    # can't create other users
    def test_create_different_user_as_new_user(self):
        response = self.client().post('/users', headers=blocked_header,
                                      data=new_user)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 422)

    # Edit User Data Tests ('/users/all/<user_id>', PATCH)
    # -------------------------------------------------------
    # Attempt to update a user's data without auth header
    def test_update_user_no_auth(self):
        response = self.client().patch('/users/all/1',
                                       data=json.dumps(updated_user))
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 401)

    # Attempt to update a user's data with malformed auth header
    def test_update_user_malformed_auth(self):
        response = self.client().patch('/users/all/1', headers=malformed_header,
                                       data=json.dumps(updated_user))
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 401)

    # Attempt to update a user's data with a user's JWT
    def test_update_user_as_user(self):
        user = updated_user
        user['id'] = sample_user_id
        user['displayName'] = 'user'
        response = self.client().patch('/users/all/' + sample_user_id,
                                       headers=user_header,
                                       data=json.dumps(user))
        response_data = json.loads(response.data)
        updated = response_data['updated']

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(updated['receivedH'], user['receivedH'])
        self.assertEqual(updated['givenH'], user['givenH'])

    # Attempt to update another user's display name with a user's JWT
    def test_update_other_users_display_name_as_user(self):
        user = updated_display
        user['id'] = sample_moderator_id
        response = self.client().patch('/users/all/' + sample_moderator_id,
                                       headers=user_header,
                                       data=json.dumps(user))
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 403)

    # Attempt to update a user's blocked state with a user's JWT
    def test_update_block_user_as_user(self):
        user = updated_unblock_user
        user['id'] = sample_user_id
        response = self.client().patch('/users/all/' + sample_user_id,
                                       headers=user_header,
                                       data=json.dumps(user))
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 403)

    # Attempt to update a user's data with a moderator's JWT
    def test_update_user_as_mod(self):
        user = updated_user
        user['id'] = sample_moderator_id
        user['displayName'] = 'mod'
        response = self.client().patch('/users/all/' + sample_moderator_id,
                                       headers=moderator_header,
                                       data=json.dumps(user))
        response_data = json.loads(response.data)
        updated = response_data['updated']

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(updated['receivedH'], user['receivedH'])
        self.assertEqual(updated['givenH'], user['givenH'])

    # Attempt to update another user's display name with a moderator's JWT
    def test_update_other_users_display_name_as_mod(self):
        user = updated_display
        user['id'] = sample_admin_id
        response = self.client().patch('/users/all/' + sample_admin_id,
                                       headers=moderator_header,
                                       data=json.dumps(user))
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 403)

    # Attempt to update a user's blocked state with a moderator's JWT
    def test_update_block_user_as_mod(self):
        user = updated_unblock_user
        user['id'] = sample_moderator_id
        response = self.client().patch('/users/all/' + sample_moderator_id,
                                       headers=moderator_header,
                                       data=json.dumps(user))
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 403)

    # Attempt to update a user's data with an admin's JWT
    def test_update_user_as_admin(self):
        user = updated_user
        user['id'] = sample_admin_id
        user['displayName'] = 'admin'
        response = self.client().patch('/users/all/' + sample_admin_id,
                                       headers=admin_header,
                                       data=json.dumps(user))
        response_data = json.loads(response.data)
        updated = response_data['updated']

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(updated['receivedH'], user['receivedH'])
        self.assertEqual(updated['givenH'], user['givenH'])

    # Attempt to update another user's display name with an admin's JWT
    def test_update_user_as_admin(self):
        user = updated_display
        user['id'] = sample_user_id
        response = self.client().patch('/users/all/' + sample_user_id,
                                       headers=admin_header,
                                       data=json.dumps(user))
        response_data = json.loads(response.data)
        updated = response_data['updated']

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(updated['receivedH'], user['receivedH'])

    # Attempt to update a user's blocked state with an admin's JWT
    def test_update_block_user_as_admin(self):
        user = updated_unblock_user
        user['id'] = sample_user_id
        response = self.client().patch('/users/all/' + sample_user_id,
                                       headers=admin_header,
                                       data=json.dumps(user))
        response_data = json.loads(response.data)
        updated = response_data['updated']

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(updated['id'], int(user['id']))

    # Attempt to update another user's settings (admin's JWT)
    def test_update_user_settings_as_admin(self):
        user = updated_unblock_user
        user['id'] = sample_user_id
        user['autoRefresh'] = True
        user['pushEnabled'] = True
        response = self.client().patch('/users/all/' + sample_user_id,
                                       headers=admin_header,
                                       data=json.dumps(user))
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 403)

    # Attempt to update a user's data with no ID (with admin's JWT)
    def test_update_no_id_user_as_admin(self):
        response = self.client().patch('/users/all/', headers=admin_header,
                                       data=json.dumps(updated_user))
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 404)

    # Get User's Posts Tests ('/users/all/<user_id>/posts', GET)
    # -------------------------------------------------------
    # Attempt to get a user's posts without auth header
    def test_get_user_posts_no_auth(self):
        response = self.client().get('/users/all/1/posts')
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 401)

    # Attempt to get a user's posts with malformed auth header
    def test_get_user_posts_malformed_auth(self):
        response = self.client().get('/users/all/1/posts',
                                     headers=malformed_header)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 401)

    # Attempt to get a user's posts with a user's JWT
    def test_get_user_posts_as_user(self):
        response = self.client().get('/users/all/1/posts', headers=user_header)
        response_data = json.loads(response.data)

        self.assertTrue(response_data['success'])
        self.assertTrue(response_data['posts'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['page'], 1)
        self.assertEqual(response_data['total_pages'], 2)
        self.assertEqual(len(response_data['posts']), 5)

    # Attempt to get a user's posts with a moderator's JWT
    def test_get_user_posts_as_mod(self):
        response = self.client().get('/users/all/4/posts',
                                     headers=moderator_header)
        response_data = json.loads(response.data)

        self.assertTrue(response_data['success'])
        self.assertTrue(response_data['posts'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['page'], 1)
        self.assertEqual(response_data['total_pages'], 3)
        self.assertEqual(len(response_data['posts']), 5)

    # Attempt to get a user's posts with an admin's JWT
    def test_get_user_posts_as_admin(self):
        response = self.client().get('/users/all/5/posts', headers=admin_header)
        response_data = json.loads(response.data)

        self.assertTrue(response_data['success'])
        self.assertTrue(response_data['posts'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['page'], 1)
        self.assertEqual(response_data['total_pages'], 1)
        self.assertEqual(len(response_data['posts']), 2)

    # Delete User's Posts Route Tests ('/users/all/<user_id>/posts', DELETE)
    # -------------------------------------------------------
    # Attempt to delete user's posts with no authorisation header
    def test_delete_posts_no_auth(self):
        response = self.client().delete('/users/all/1/posts')
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 401)

    # Attempt to delete user's with a malformed auth header
    def test_delete_posts_malformed_auth(self):
        response = self.client().delete('/users/all/1/posts',
                                        headers=malformed_header)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 401)

    # Attempt to delete the user's posts (with same user's JWT)
    def test_delete_own_posts_as_user(self):
        response = self.client().delete('/users/all/1/posts',
                                        headers=user_header)
        response_data = json.loads(response.data)

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['deleted'], 8)

    # Attempt to delete another user's posts (with user's JWT)
    def test_delete_other_users_posts_as_user(self):
        response = self.client().delete('/users/all/4/posts',
                                        headers=user_header)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 403)

    # Attempt to delete the moderator's posts (with same moderator's JWT)
    def test_delete_own_posts_as_mod(self):
        response = self.client().delete('/users/all/5/posts',
                                        headers=moderator_header)
        response_data = json.loads(response.data)

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['deleted'], 2)

    # Attempt to delete another user's posts (with moderator's JWT)
    def test_delete_other_users_posts_as_mod(self):
        response = self.client().delete('/users/all/1/posts',
                                        headers=moderator_header)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 403)

    # Attempt to delete the admin's posts (with same admin's JWT)
    def test_delete_own_posts_as_admin(self):
        response = self.client().delete('/users/all/4/posts',
                                        headers=admin_header)
        response_data = json.loads(response.data)

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['deleted'], 14)

    # Attempt to delete another user's posts (with admin's JWT)
    def test_delete_other_users_posts_as_admin(self):
        response = self.client().delete('/users/all/5/posts',
                                        headers=admin_header)
        response_data = json.loads(response.data)

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['deleted'], 2)

    # Attempt to delete the posts of a user that doesn't exist (admin's JWT)
    def test_delete_nonexistent_users_posts_as_admin(self):
        response = self.client().delete('/users/all/100/posts',
                                        headers=admin_header)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 404)

    # Attempt to delete the posts of a user that has no posts (admin's JWT)
    def test_delete_nonexistent_posts_as_admin(self):
        response = self.client().delete('/users/all/9/posts',
                                        headers=admin_header)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 404)

    # Get User's Messages Tests ('/messages', GET)
    # -------------------------------------------------------
    # Attempt to get a user's messages without auth header
    def test_get_user_messages_no_auth(self):
        response = self.client().get('/messages?userID=1')
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 401)

    # Attempt to get a user's messages with malformed auth header
    def test_get_user_messages_malformed_auth(self):
        response = self.client().get('/messages?userID=1',
                                     headers=malformed_header)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 401)

    # Attempt to get a user's inbox with a user's JWT
    def test_get_user_inbox_as_user(self):
        response = self.client().get('/messages?userID=' + sample_user_id,
                                     headers=user_header)
        response_data = json.loads(response.data)

        self.assertTrue(response_data['success'])
        self.assertTrue(response_data['messages'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['current_page'], 1)
        self.assertEqual(response_data['total_pages'], 2)
        self.assertEqual(len(response_data['messages']), 5)

    # Attempt to get a user's outbox with a user's JWT
    def test_get_user_outbox_as_user(self):
        response = self.client().get('/messages?type=outbox&userID=' +
                                     sample_user_id,
                                     headers=user_header)
        response_data = json.loads(response.data)

        self.assertTrue(response_data['success'])
        self.assertTrue(response_data['messages'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['current_page'], 1)
        self.assertEqual(response_data['total_pages'], 1)
        self.assertEqual(len(response_data['messages']), 2)

    # Attempt to get a user's threads mailbox with a user's JWT
    def test_get_user_threads_as_user(self):
        response = self.client().get('/messages?type=threads&userID=' +
                                     sample_user_id,
                                     headers=user_header)
        response_data = json.loads(response.data)

        self.assertTrue(response_data['success'])
        self.assertTrue(response_data['messages'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['current_page'], 1)
        self.assertEqual(response_data['total_pages'], 1)
        self.assertEqual(len(response_data['messages']), 4)

    # Attempt to get another user's messages with a user's JWT
    def test_get_another_users_messages_as_user(self):
        response = self.client().get('/messages?userID=' + sample_moderator_id,
                                     headers=user_header)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 403)

    # Attempt to get a user's inbox with a moderator's JWT
    def test_get_user_inbox_as_mod(self):
        response = self.client().get('/messages?userID=' + sample_moderator_id,
                                     headers=moderator_header)
        response_data = json.loads(response.data)

        self.assertTrue(response_data['success'])
        self.assertTrue(response_data['messages'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['current_page'], 1)
        self.assertEqual(response_data['total_pages'], 1)
        self.assertEqual(len(response_data['messages']), 5)

    # Attempt to get a user's outbox with a moderator's JWT
    def test_get_user_outbox_as_mod(self):
        response = self.client().get('/messages?type=outbox&userID=' +
                                     sample_moderator_id,
                                     headers=moderator_header)
        response_data = json.loads(response.data)

        self.assertTrue(response_data['success'])
        self.assertTrue(response_data['messages'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['current_page'], 1)
        self.assertEqual(response_data['total_pages'], 1)
        self.assertEqual(len(response_data['messages']), 2)

    # Attempt to get a user's threads mailbox with a moderator's JWT
    def test_get_user_threads_as_mod(self):
        response = self.client().get('/messages?type=threads&userID=' +
                                     sample_moderator_id,
                                     headers=moderator_header)
        response_data = json.loads(response.data)

        self.assertTrue(response_data['success'])
        self.assertTrue(response_data['messages'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['current_page'], 1)
        self.assertEqual(response_data['total_pages'], 1)
        self.assertEqual(len(response_data['messages']), 3)

    #  Attempt to get another user's messages with a moderator's JWT
    def test_get_another_users_messages_as_mod(self):
        response = self.client().get('/messages?userID=' + sample_admin_id,
                                     headers=moderator_header)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 403)

    # Attempt to get a user's inbox with an admin's JWT
    def test_get_user_inbox_as_admin(self):
        response = self.client().get('/messages?userID=' + sample_admin_id,
                                     headers=admin_header)
        response_data = json.loads(response.data)

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['current_page'], 1)
        self.assertEqual(response_data['total_pages'], 1)
        self.assertEqual(len(response_data['messages']), 1)

    # Attempt to get a user's outbox with an admin's JWT
    def test_get_user_outbox_as_admin(self):
        response = self.client().get('/messages?type=outbox&userID=' +
                                     sample_admin_id,
                                     headers=admin_header)
        response_data = json.loads(response.data)

        self.assertTrue(response_data['success'])
        self.assertTrue(response_data['messages'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['current_page'], 1)
        self.assertEqual(response_data['total_pages'], 1)
        self.assertEqual(len(response_data['messages']), 5)

    # Attempt to get a user's threads mailbox with an admin's JWT
    def test_get_user_threads_as_admin(self):
        response = self.client().get('/messages?type=threads&userID=' +
                                     sample_admin_id,
                                     headers=admin_header)
        response_data = json.loads(response.data)

        self.assertTrue(response_data['success'])
        self.assertTrue(response_data['messages'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['current_page'], 1)
        self.assertEqual(response_data['total_pages'], 1)
        self.assertEqual(len(response_data['messages']), 3)

    # Attempt to get another user's messages with an admin's JWT
    def test_get_another_users_messages_as_admin(self):
        response = self.client().get('/messages?userID=' + sample_user_id,
                                     headers=admin_header)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 403)

    # Attempt to get a user's messages with no ID (with admin's JWT)
    def test_get_no_id_user_messages_as_admin(self):
        response = self.client().get('/messages', headers=admin_header)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 400)

    # Attempt to get other users' messaging thread (with admin's JWT)
    def get_other_users_thread_as_admin(self):
        response = self.client().get('/messages?userID=4&type=thread&\
                                     threadID=2', headers=admin_header)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 403)

    # Create Message Route Tests ('/message', POST)
    # -------------------------------------------------------
    # Attempt to create a message with no authorisation header
    def test_send_message_no_auth(self):
        response = self.client().post('/messages',
                                      data=json.dumps(new_message))
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 401)

    # Attempt to create a message with a malformed auth header
    def test_send_message_malformed_auth(self):
        response = self.client().post('/messages', headers=malformed_header,
                                      data=json.dumps(new_message))
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 401)

    # Attempt to create a message with a user's JWT
    def test_send_message_as_user(self):
        message = new_message
        message['fromId'] = int(sample_user_id)
        message['forId'] = sample_moderator_id
        response = self.client().post('/messages', headers=user_header,
                                      data=json.dumps(message))
        response_data = json.loads(response.data)
        response_message = response_data['message']

        self.assertTrue(response_data['success'])
        self.assertTrue(response_data['message'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_message['messageText'],
                         message['messageText'])

    # Attempt to create a message from another user (with a user's JWT)
    def test_send_message_from_another_user_as_user(self):
        message = new_message
        message['fromId'] = int(sample_admin_id)
        message['forId'] = sample_moderator_id
        response = self.client().post('/messages', headers=user_header,
                                      data=json.dumps(message))
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 403)

    # Attempt to create a message with a moderator's JWT
    def test_send_message_as_mod(self):
        message = new_message
        message['fromId'] = int(sample_moderator_id)
        message['forId'] = sample_admin_id
        response = self.client().post('/messages', headers=moderator_header,
                                      data=json.dumps(message))
        response_data = json.loads(response.data)
        response_message = response_data['message']

        self.assertTrue(response_data['success'])
        self.assertTrue(response_data['message'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_message['messageText'],
                         message['messageText'])

    # Attempt to create a message from another user (with a moderator's JWT)
    def test_send_message_from_another_user_as_mod(self):
        message = new_message
        message['fromId'] = int(sample_admin_id)
        message['forId'] = sample_user_id
        response = self.client().post('/messages', headers=moderator_header,
                                      data=json.dumps(message))
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 403)

    # Attempt to create a message with an admin's JWT
    def test_send_message_as_admin(self):
        message = new_message
        message['fromId'] = int(sample_admin_id)
        message['forId'] = sample_moderator_id
        response = self.client().post('/messages', headers=admin_header,
                                      data=json.dumps(message))
        response_data = json.loads(response.data)
        response_message = response_data['message']

        self.assertTrue(response_data['success'])
        self.assertTrue(response_data['message'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_message['messageText'],
                         message['messageText'])

    # Attempt to create a message from another user (with an admin's JWT)
    def test_send_message_from_another_user_as_admin(self):
        message = new_message
        message['fromId'] = int(sample_user_id)
        message['forId'] = sample_moderator_id
        response = self.client().post('/messages', headers=admin_header,
                                      data=json.dumps(message))
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 403)

    # Attempt to send a message from a user (when there's no thread)
    def test_send_message_create_thread_as_user(self):
        message = new_message
        message['fromId'] = int(blocked_user_id)
        message['forId'] = sample_admin_id
        response = self.client().post('/messages', headers=blocked_header,
                                      data=json.dumps(message))
        response_data = json.loads(response.data)
        response_message = response_data['message']
        new_thread = self.client().get('/messages?userID=20&type=thread&threadID=7', headers=blocked_header)
        new_thread_data = json.loads(new_thread.data)

        self.assertTrue(response_data['success'])
        self.assertTrue(response_data['message'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_message['messageText'],
                         message['messageText'])
        self.assertEqual(response_message['threadID'], 7)
        self.assertEqual(len(new_thread_data['messages']), 2)

    # Delete Message Route Tests ('/message/<message_id>', DELETE)
    # -------------------------------------------------------
    # Attempt to delete a message with no authorisation header
    def test_delete_message_no_auth(self):
        response = self.client().delete('/messages/inbox/1')
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 401)

    # Attempt to delete a message with a malformed auth header
    def test_delete_message_malformed_auth(self):
        response = self.client().delete('/messages/inbox/1',
                                        headers=malformed_header)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 401)

    # Attempt to delete a message with a user's JWT
    def test_delete_message_as_user(self):
        response = self.client().delete('/messages/inbox/3',
                                        headers=user_header)
        response_data = json.loads(response.data)

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['deleted'], '3')

    # Attempt to delete another user's message (with a user's JWT)
    def test_delete_message_from_another_user_as_user(self):
        response = self.client().delete('/messages/inbox/7',
                                        headers=user_header)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 403)

    # Attempt to delete a thread with a user's JWT
    def test_delete_thread_as_user(self):
        response = self.client().delete('/messages/threads/2',
                                        headers=user_header)
        response_data = json.loads(response.data)
        get_thread = self.client().get('/messages?userID=1&type=thread&\
                                        threadID=2', headers=user_header)
        thread_data = json.loads(get_thread.data)

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['deleted'], '2')
        self.assertEqual(len(thread_data['messages']), 0)

    # Attempt to delete a message with a moderator's JWT
    def test_delete_message_as_mod(self):
        response = self.client().delete('/messages/inbox/5',
                                        headers=moderator_header)
        response_data = json.loads(response.data)

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['deleted'], '5')

    # Attempt to delete another user's message (with a moderator's JWT)
    def test_delete_message_from_another_user_as_mod(self):
        response = self.client().delete('/messages/outbox/9',
                                        headers=moderator_header)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 403)

    # Attempt to delete a message with an admin's JWT
    def test_delete_message_as_admin(self):
        response = self.client().delete('/messages/outbox/10',
                                        headers=admin_header)
        response_data = json.loads(response.data)

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['deleted'], '10')

    # Attempt to delete another user's message (with an admin's JWT)
    def test_delete_message_from_another_user_as_admin(self):
        response = self.client().delete('/messages/outbox/3',
                                        headers=admin_header)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 403)

    # Attempt to delete a user's message with no mailbox (with admin's JWT)
    def test_delete_no_id_user_message_as_admin(self):
        response = self.client().delete('/messages/', headers=admin_header)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 404)

    # Attempt to delete a nonexistent user's message (with admin's JWT)
    def test_delete_nonexistent_user_message_as_admin(self):
        response = self.client().delete('/messages/inbox/100', headers=admin_header)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 404)

    # Empty Mailbox Tests ('/messages/<mailbox>', DELETE)
    # -------------------------------------------------------
    # Attempt to empty mailbox without auth header
    def test_empty_mailbox_no_auth(self):
        response = self.client().delete('/messages/inbox?userID=4')
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 401)

    # Attempt to empty mailbox with malformed auth header
    def test_empty_mailbox_malformed_auth(self):
        response = self.client().delete('/messages/inbox?userID=4',
                                        headers=malformed_header)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 401)

    # Attempt to empty user's inbox (user JWT)
    def test_empty_mailbox_as_user(self):
        response = self.client().delete('/messages/inbox?userID=' +
                                        sample_user_id,
                                        headers=user_header)
        response_data = json.loads(response.data)

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['deleted'], 7)
        self.assertEqual(response_data['userID'], '1')

    # Attempt to empty another user's inbox (user JWT)
    def test_empty_other_users_mailbox_as_user(self):
        response = self.client().delete('/messages/inbox?userID=4',
                                        headers=user_header)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 403)

    # Attempt to empty user's outbox (moderator's JWT)
    def test_empty_mailbox_as_mod(self):
        response = self.client().delete('/messages/outbox?userID=' +
                                        sample_moderator_id,
                                        headers=moderator_header)
        response_data = json.loads(response.data)

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['deleted'], 2)
        self.assertEqual(response_data['userID'], '5')

    # Attempt to empty another user's outbox (moderator's JWT)
    def test_empty_other_users_mailbox_as_mod(self):
        response = self.client().delete('/messages/outbox?userID=1',
                                        headers=moderator_header)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 403)

    # Attempt to empty user's threads mailbox (admin's JWT)
    def test_empty_mailbox_as_admin(self):
        response = self.client().delete('/messages/threads?userID=' +
                                        sample_admin_id,
                                        headers=admin_header)
        response_data = json.loads(response.data)

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['deleted'], 2)
        self.assertEqual(response_data['userID'], '4')

    # Attempt to empty another user's threads mailbox (admin's JWT)
    def test_empty_other_users_mailbox_as_admin(self):
        response = self.client().delete('/messages/threads?userID=5',
                                        headers=admin_header)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 403)

    # Get Open Reports Tests ('/reports', GET)
    # -------------------------------------------------------
    # Attempt to get open reports without auth header
    def test_get_open_reports_no_auth(self):
        response = self.client().get('/reports')
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 401)

    # Attempt to get open reports with malformed auth header
    def test_get_open_reports_malformed_auth(self):
        response = self.client().get('/reports', headers=malformed_header)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 401)

    # Attempt to get open reports with a user's JWT
    def test_get_open_reports_as_user(self):
        response = self.client().get('/reports', headers=user_header)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 403)

    #  Attempt to get open reports with a moderator's JWT
    def test_get_open_reports_as_mod(self):
        response = self.client().get('/reports', headers=moderator_header)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 403)

    # Attempt to get open reports with an admin's JWT
    def test_get_open_reports_as_admin(self):
        response = self.client().get('/reports', headers=admin_header)
        response_data = json.loads(response.data)

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['totalUserPages'], 0)
        self.assertEqual(response_data['totalPostPages'], 0)
        self.assertEqual(len(response_data['userReports']), 0)
        self.assertEqual(len(response_data['postReports']), 0)

    # Create Report Route Tests ('/reports', POST)
    # -------------------------------------------------------
    # Attempt to create a report with no authorisation header
    def test_send_report_no_auth(self):
        response = self.client().post('/reports', data=json.dumps(new_report))
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 401)

    # Attempt to create a report with a malformed auth header
    def test_send_report_malformed_auth(self):
        response = self.client().post('/reports', headers=malformed_header,
                                      data=json.dumps(new_report))
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 401)

    # Attempt to create a report with a user's JWT
    def test_send_report_as_user(self):
        report = new_report
        report['userID'] = 4
        report['postID'] = 25
        report['reporter'] = sample_user_id
        response = self.client().post('/reports', headers=user_header,
                                      data=json.dumps(report))
        response_data = json.loads(response.data)
        response_report = response_data['report']

        self.assertTrue(response_data['success'])
        self.assertFalse(response_report['closed'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_report['postID'], report['postID'])

    # Attempt to create a report with a moderator's JWT
    def test_send_report_as_mod(self):
        report = new_report
        report['userID'] = 4
        report['postID'] = 25
        report['reporter'] = sample_moderator_id
        response = self.client().post('/reports', headers=moderator_header,
                                      data=json.dumps(report))
        response_data = json.loads(response.data)
        response_report = response_data['report']

        self.assertTrue(response_data['success'])
        self.assertFalse(response_report['closed'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_report['postID'], report['postID'])

    # Attempt to create a report with an admin's JWT
    def test_send_report_as_admin(self):
        report = new_report
        report['userID'] = 4
        report['postID'] = 25
        report['reporter'] = sample_admin_id
        response = self.client().post('/reports', headers=admin_header,
                                      data=json.dumps(report))
        response_data = json.loads(response.data)
        response_report = response_data['report']

        self.assertTrue(response_data['success'])
        self.assertFalse(response_report['closed'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_report['postID'], report['postID'])

    # Attempt to create a post report without post ID with an admin's JWT
    def test_send_malformed_report_as_admin(self):
        report = new_report
        report['userID'] = 4
        report['postID'] = None
        report['reporter'] = sample_admin_id
        response = self.client().post('/reports', headers=admin_header,
                                      data=json.dumps(report))
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 422)

    # Update Report Route Tests ('/reports/<report_id>', PATCH)
    # -------------------------------------------------------
    # Attempt to update a report with no authorisation header
    def test_update_report_no_auth(self):
        response = self.client().patch('/reports/36',
                                       data=json.dumps(new_report))
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 401)

    # Attempt to update a report with a malformed auth header
    def test_update_report_malformed_auth(self):
        response = self.client().patch('/reports/36', headers=malformed_header,
                                       data=json.dumps(new_report))
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 401)

    # Attempt to update a report (with user's JWT)
    def test_update_report_as_user(self):
        report = new_report
        report['userID'] = 4
        report['postID'] = 25
        report['reporter'] = sample_user_id
        response = self.client().patch('/reports/36', headers=user_header,
                                       data=json.dumps(report))
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 403)

    # Attempt to update a report (with moderator's JWT)
    def test_update_report_as_mod(self):
        report = new_report
        report['userID'] = 4
        report['postID'] = 25
        report['reporter'] = sample_moderator_id
        response = self.client().patch('/reports/36', headers=moderator_header,
                                       data=json.dumps(report))
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 403)

    # Attempt to update a report (with admin's JWT)
    def test_update_report_as_admin(self):
        report = new_report
        report['id'] = 36
        report['userID'] = 4
        report['postID'] = 25
        report['reporter'] = sample_admin_id
        report['dismissed'] = False
        report['closed'] = False
        response = self.client().patch('/reports/36', headers=admin_header,
                                       data=json.dumps(report))
        response_data = json.loads(response.data)
        report_text = response_data['updated']

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(report_text['id'], report['id'])

    # Attempt to update a report with no ID (with admin's JWT)
    def test_update_no_id_report_as_admin(self):
        report = new_report
        report['id'] = 36
        report['userID'] = 4
        report['postID'] = 25
        report['reporter'] = sample_admin_id
        report['dismissed'] = False
        report['closed'] = False
        response = self.client().patch('/reports/', headers=admin_header,
                                       data=json.dumps(report))
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 404)

    # Attempt to update a report that doesn't exist (with admin's JWT)
    def test_update_nonexistent_report_as_admin(self):
        report = new_report
        report['id'] = 36
        report['userID'] = 4
        report['postID'] = 25
        report['reporter'] = sample_admin_id
        report['dismissed'] = False
        report['closed'] = False
        response = self.client().patch('/reports/100', headers=admin_header,
                                       data=json.dumps(report))
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 404)

    # Get Filters Tests ('/filters', GET)
    # -------------------------------------------------------
    # Attempt to get filters without auth header
    def test_get_filters_no_auth(self):
        response = self.client().get('/filters')
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 401)

    # Attempt to get filters with malformed auth header
    def test_get_filters_malformed_auth(self):
        response = self.client().get('/filters', headers=malformed_header)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 401)

    # Attempt to get filters with a user's JWT
    def test_get_filters_as_user(self):
        response = self.client().get('/filters', headers=user_header)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 403)

    #  Attempt to get filters with a moderator's JWT
    def test_get_filters_as_mod(self):
        response = self.client().get('/filters', headers=moderator_header)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 403)

    # Attempt to get filters with an admin's JWT
    def test_get_filters_as_admin(self):
        response = self.client().get('/filters', headers=admin_header)
        response_data = json.loads(response.data)

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['total_pages'], 0)
        self.assertEqual(len(response_data['words']), 0)

    # Create Filters Tests ('/filters', POST)
    # -------------------------------------------------------
    # Attempt to create a filter without auth header
    def test_create_filters_no_auth(self):
        response = self.client().post('/filters',
                                      data=json.dumps({"word":"sample"}))
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 401)

    # Attempt to create a filter with malformed auth header
    def test_create_filters_malformed_auth(self):
        response = self.client().post('/filters', headers=malformed_header,
                                      data=json.dumps({"word":"sample"}))
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 401)

    # Attempt to create a filter with a user's JWT
    def test_create_filters_as_user(self):
        response = self.client().post('/filters', headers=user_header,
                                      data=json.dumps({"word":"sample"}))
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 403)

    #  Attempt to create a filter with a moderator's JWT
    def test_create_filters_as_mod(self):
        response = self.client().post('/filters', headers=moderator_header,
                                      data=json.dumps({"word":"sample"}))
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 403)

    # Attempt to create a filter with an admin's JWT
    def test_create_filters_as_admin(self):
        response = self.client().post('/filters', headers=admin_header,
                                      data=json.dumps({"word":"sample"}))
        response_data = json.loads(response.data)
        added_word = response_data['added']

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(added_word['filter'], 'sample')

    # Delete Filters Tests ('/filters/<id>', DELETE)
    # -------------------------------------------------------
    # Attempt to delete a filter without auth header
    def test_delete_filters_no_auth(self):
        response = self.client().delete('/filters/1')
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 401)

    # Attempt to delete a filter with malformed auth header
    def test_delete_filters_malformed_auth(self):
        response = self.client().delete('/filters/1', headers=malformed_header)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 401)

    # Attempt to delete a filter with a user's JWT
    def test_delete_filters_as_user(self):
        response = self.client().delete('/filters/1', headers=user_header)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 403)

    #  Attempt to delete a filter with a moderator's JWT
    def test_delete_filters_as_mod(self):
        response = self.client().delete('/filters/1', headers=moderator_header)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 403)

    # Attempt to delete a filter with an admin's JWT
    def test_delete_filters_as_admin(self):
        # Set up the test by adding a word
        self.client().post('/filters', headers=admin_header,
                                      data=json.dumps({"word":"sample"}))
        # Delete the filter
        response = self.client().delete('/filters/2', headers=admin_header)
        response_data = json.loads(response.data)
        deleted = response_data['deleted']

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(deleted['filter'], 'sample')

    # Attempt to delete a filter that doesn't exist with an admin's JWT
    def test_delete_nonexistent_filters_as_admin(self):
        response = self.client().delete('/filters/100', headers=admin_header)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 404)

    # Get New Notifications Route Tests ('/notifications', GET)
    # -------------------------------------------------------
    # Attempt to get user notifications without auth header
    def test_get_notifications_no_auth(self):
        response = self.client().get('/notifications')
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 401)

    # Attempt to get user notifications with malformed auth header
    def test_get_notifications_malformed_auth(self):
        response = self.client().get('/notifications',
                                     headers=malformed_header)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 401)

    # Attempt to get user notifications with a user's JWT (silent refresh)
    def test_get_silent_notifications_as_user(self):
        pre_user_query = self.client().get('/users/all/' +
                                           sample_user_auth0_id,
                                           headers=user_header)
        pre_user_data = json.loads(pre_user_query.data)['user']
        response = self.client().get('/notifications?silentRefresh=true',
                                     headers=user_header)
        response_data = json.loads(response.data)
        post_user_query = self.client().get('/users/all/' +
                                            sample_user_auth0_id,
                                            headers=user_header)
        post_user_data = json.loads(post_user_query.data)['user']

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response_data['notifications']), 11)
        self.assertEqual(pre_user_data['last_notifications_read'],
                         post_user_data['last_notifications_read'])

    # Attempt to get user notifications with a user's JWT (non-silent refresh)
    def test_get_non_silent_notifications_as_user(self):
        pre_user_query = self.client().get('/users/all/' +
                                           sample_user_auth0_id,
                                           headers=user_header)
        pre_user_data = json.loads(pre_user_query.data)['user']
        response = self.client().get('/notifications?silentRefresh=false',
                                     headers=user_header)
        response_data = json.loads(response.data)
        post_user_query = self.client().get('/users/all/' +
                                            sample_user_auth0_id,
                                            headers=user_header)
        post_user_data = json.loads(post_user_query.data)['user']

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response_data['notifications']), 11)
        self.assertNotEqual(pre_user_data['last_notifications_read'],
                            post_user_data['last_notifications_read'])

    # Attempt to get user notifications with a mod's JWT (silent refresh)
    def test_get_silent_notifications_as_mod(self):
        pre_user_query = self.client().get('/users/all/' +
                                           sample_moderator_auth0_id,
                                           headers=moderator_header)
        pre_user_data = json.loads(pre_user_query.data)['user']
        response = self.client().get('/notifications?silentRefresh=true',
                                     headers=moderator_header)
        response_data = json.loads(response.data)
        post_user_query = self.client().get('/users/all/' +
                                            sample_moderator_auth0_id,
                                            headers=moderator_header)
        post_user_data = json.loads(post_user_query.data)['user']

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response_data['notifications']), 4)
        self.assertEqual(pre_user_data['last_notifications_read'],
                         post_user_data['last_notifications_read'])

    # Attempt to get user notifications with a mod's JWT (non-silent refresh)
    def test_get_non_silent_notifications_as_mod(self):
        pre_user_query = self.client().get('/users/all/' +
                                           sample_moderator_auth0_id,
                                           headers=moderator_header)
        pre_user_data = json.loads(pre_user_query.data)['user']
        response = self.client().get('/notifications?silentRefresh=false',
                                     headers=moderator_header)
        response_data = json.loads(response.data)
        post_user_query = self.client().get('/users/all/' +
                                            sample_moderator_auth0_id,
                                            headers=moderator_header)
        post_user_data = json.loads(post_user_query.data)['user']

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response_data['notifications']), 4)
        self.assertNotEqual(pre_user_data['last_notifications_read'],
                            post_user_data['last_notifications_read'])

        # Attempt to get user notifications with an admin's JWT (silently)
        def test_get_silent_notifications_as_admin(self):
            pre_user_query = self.client().get('/users/all/' +
                                               sample_admin_auth0_id,
                                               headers=admin_header)
            pre_user_data = json.loads(pre_user_query.data)['user']
            response = self.client().get('/notifications?silentRefresh=true',
                                         headers=admin_header)
            response_data = json.loads(response.data)
            post_user_query = self.client().get('/users/all/' +
                                                sample_admin_auth0_id,
                                                headers=admin_header)
            post_user_data = json.loads(post_user_query.data)['user']

            self.assertTrue(response_data['success'])
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response_data['notifications']), 0)
            self.assertEqual(pre_user_data['last_notifications_read'],
                             post_user_data['last_notifications_read'])

        # Attempt to get user notifications with an admin's JWT (non-silently)
        def test_get_non_silent_notifications_as_admin(self):
            pre_user_query = self.client().get('/users/all/' +
                                               sample_admin_auth0_id,
                                               headers=admin_header)
            pre_user_data = json.loads(pre_user_query.data)['user']
            response = self.client().get('/notifications?silentRefresh=false',
                                         headers=admin_header)
            response_data = json.loads(response.data)
            post_user_query = self.client().get('/users/all/' +
                                                sample_admin_auth0_id,
                                                headers=admin_header)
            post_user_data = json.loads(post_user_query.data)['user']

            self.assertTrue(response_data['success'])
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response_data['notifications']), 0)
            self.assertNotEqual(pre_user_data['last_notifications_read'],
                                post_user_data['last_notifications_read'])

        # Add New Push Subscription Route Tests ('/notifications', POST)
        # -------------------------------------------------------
        # Attempt to create push subscription without auth header
        def test_post_subscription_no_auth(self):
            response = self.client().post('/notifications',
                                          data=json.dumps(new_subscription))
            response_data = json.loads(response.data)

            self.assertFalse(response_data['success'])
            self.assertEqual(response.status_code, 401)

        # Attempt to create push subscription with malformed auth header
        def test_post_subscription_malformed_auth(self):
            response = self.client().post('/notifications',
                                          data=json.dumps(new_subscription),
                                          headers=malformed_header)
            response_data = json.loads(response.data)

            self.assertFalse(response_data['success'])
            self.assertEqual(response.status_code, 401)

        # Attempt to create push subscription with a user's JWT
        def test_post_subscription_as_user(self):
            response = self.client().post('/notifications',
                                          data=json.dumps(new_subscription),
                                          headers=user_header)
            response_data = json.loads(response.data)

            self.assertTrue(response_data['success'])
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response_data['subscribed'], 'shirb')

        # Attempt to create push subscription with a moderator's JWT
        def test_post_subscription_as_mod(self):
            response = self.client().post('/notifications',
                                          data=json.dumps(new_subscription),
                                          headers=moderator_header)
            response_data = json.loads(response.data)

            self.assertTrue(response_data['success'])
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response_data['subscribed'], 'user52')

        # Attempt to create push subscription with an admin's JWT
        def test_post_subscription_as_admin(self):
            response = self.client().post('/notifications',
                                          data=json.dumps(new_subscription),
                                          headers=admin_header)
            response_data = json.loads(response.data)

            self.assertTrue(response_data['success'])
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response_data['subscribed'], 'user14')

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
