import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from app import create_app
from models import create_db, Post, User, Message

# Tokens
user_jwt = ''
moderator_jwt = ''
admin_jwt = ''

# Headers
malformed_header = {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer '
                    }
user_header = {
               'Content-Type': 'application/json',
               'Authorization': 'Bearer ' + user_jwt
              }
moderator_header = {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + moderator_jwt
                   }
admin_header = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + admin_jwt
               }

# Sample users data
sample_user_id = str(1)
sample_user_auth0_id = 'auth0|5ed34765f0b8e60c8e87ca62'
sample_moderator_id = str(5)
sample_moderator_auth0_id = 'auth0|5ede3e7a0793080013259050'
sample_admin_id = str(4)
sample_admin_auth0_id = 'auth0|5ed8e3d0def75d0befbc7e50'

# Item Samples
new_post = {
    "user_id": 0,
    "text": "test post",
    "date": "Sun Jun 07 2020 15:57:45 GMT+0300",
    "givenHugs": 0
}

updated_post = {
    "user_id": 0,
    "text": "test post",
    "date": "Sun Jun 07 2020 15:57:45 GMT+0300",
    "givenHugs": 0
}

new_user = '{\
"auth0Id": "",\
"displayName": "",\
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
    "date": "Sun Jun 07 2020 15:57:45 GMT+0300"
}


# App testing
class TestHugApp(unittest.TestCase):
    # Setting up each test
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client
        self.database_path = 'postgres://localhost:5432/test-capstone'

        create_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    # Executed after each test
    def tearDown(self):
        pass

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

    # Create Post Route Tests ('/posts', POST)
    # -------------------------------------------------------
    # Attempt to create a post with no authorisation header
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
        post['user_id'] = sample_user_id
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
        post['user_id'] = sample_moderator_id
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
        post['user_id'] = sample_admin_id
        response = self.client().post('/posts', headers=admin_header,
                                      data=json.dumps(post))
        response_data = json.loads(response.data)
        response_post = response_data['posts']

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_post['text'], post['text'])

    # Update Post Route Tests ('/posts/<post_id>', PATCH)
    # -------------------------------------------------------
    # Attempt to update a post with no authorisation header
    def test_update_post_no_auth(self):
        response = self.client().patch('/posts/4', data=json.dumps(updated_post))
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
        post['user_id'] = sample_user_id
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
        post['user_id'] = sample_moderator_id
        response = self.client().patch('/posts/13', headers=user_header,
                                       data=json.dumps(post))
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 403)

    # Attempt to update the moderator's post (with same moderator's JWT)
    def test_update_own_post_as_mod(self):
        post = updated_post
        post['user_id'] = sample_moderator_id
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
        post['user_id'] = sample_user_id
        response = self.client().patch('/posts/4', headers=moderator_header,
                                       data=json.dumps(post))
        response_data = json.loads(response.data)
        post_text = response_data['updated']

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(post_text['text'], post['text'])

    # Attempt to update the admin's post (with same admin's JWT)
    def test_update_own_post_as_admin(self):
        post = updated_post
        post['user_id'] = sample_admin_id
        response = self.client().patch('/posts/15', headers=admin_header,
                                       data=json.dumps(post))
        response_data = json.loads(response.data)
        post_text = response_data['updated']

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(post_text['text'], post['text'])

    # Attempt to update another user's post (with admin's JWT)
    def test_update_other_users_post_as_admin(self):
        post = updated_post
        post['user_id'] = sample_user_id
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
        post['user_id'] = sample_user_id
        response = self.client().patch('/posts/', headers=admin_header,
                                       data=json.dumps(post))
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 404)

    # Attempt to update a post that doesn't exist (with admin's JWT)
    def test_update_nonexistent_post_as_admin(self):
        post = updated_post
        post['user_id'] = sample_user_id
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
        response = self.client().delete('/posts/3', headers=moderator_header)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 403)

    # Attempt to delete the admin's post (with same admin's JWT)
    def test_delete_own_post_as_admin(self):
        response = self.client().delete('/posts/14', headers=admin_header)
        response_data = json.loads(response.data)

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['deleted'], '14')

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
        self.assertEqual(response_data['total_pages'], 2)

    # Attempt to get page 2 of full new posts
    def test_get_full_new_posts_page_2(self):
        response = self.client().get('/posts/new?page=2')
        response_data = json.loads(response.data)

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response_data['posts']), 5)
        self.assertEqual(response_data['total_pages'], 2)

    # Attempt to get page 1 of full suggested posts
    def test_get_full_suggested_posts(self):
        response = self.client().get('/posts/suggested')
        response_data = json.loads(response.data)

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response_data['posts']), 5)
        self.assertEqual(response_data['total_pages'], 2)

    # Attempt to get page 2 of full suggested posts
    def test_get_full_suggested_posts_page_2(self):
        response = self.client().get('/posts/suggested?page=2')
        response_data = json.loads(response.data)

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response_data['posts']), 5)
        self.assertEqual(response_data['total_pages'], 2)

    # Get User Data Tests ('/users/<user_id>', GET)
    # -------------------------------------------------------
    # Attempt to get a user's data without auth header
    def test_get_user_data_no_auth(self):
        response = self.client().get('/users/1')
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 401)

    # Attempt to get a user's data with malformed auth header
    def test_get_user_data_malformed_auth(self):
        response = self.client().get('/users/1', headers=malformed_header)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 401)

    # Attempt to get a user's data with a user's JWT
    def test_get_user_data_as_user(self):
        response = self.client().get('/users/' + sample_user_auth0_id, headers=user_header)
        response_data = json.loads(response.data)
        user_data = response_data['user']

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(user_data['id'], int(sample_user_id))

    # Attempt to get a user's data with a moderator's JWT
    def test_get_user_data_as_mod(self):
        response = self.client().get('/users/' + sample_moderator_auth0_id, headers=moderator_header)
        response_data = json.loads(response.data)
        user_data = response_data['user']

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(user_data['id'], int(sample_moderator_id))

    # Attempt to get a user's data with an admin's JWT
    def test_get_user_data_as_admin(self):
        response = self.client().get('/users/' + sample_admin_auth0_id, headers=admin_header)
        response_data = json.loads(response.data)
        user_data = response_data['user']

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(user_data['id'], int(sample_admin_id))

    # Attempt to get a user's data with no ID (with admin's JWT)
    def test_get_no_id_user_as_admin(self):
        response = self.client().get('/users/', headers=admin_header)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 404)

    # Attempt to get a nonexistent user's data (with admin's JWT)
    def test_get_nonexistent_user_as_admin(self):
        response = self.client().get('/users/100', headers=admin_header)
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
    def test_create_user_no_auth(self):
        response = self.client().post('/users', headers=malformed_header, data=new_user)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 401)

    # Attempt to create a user with user's JWT
    def test_create_user_no_auth(self):
        response = self.client().post('/users', headers=user_header, data=new_user)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 403)

    # Attempt to create a user with moderator's JWT
    def test_create_user_no_auth(self):
        response = self.client().post('/users', headers=moderator_header, data=new_user)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 403)

    # Attempt to create a user with admin's JWT
    def test_create_user_no_auth(self):
        response = self.client().post('/users', headers=admin_header, data=new_user)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 403)

    # Edit User Data Tests ('/users/<user_id>', PATCH)
    # -------------------------------------------------------
    # Attempt to update a user's data without auth header
    def test_update_user_no_auth(self):
        response = self.client().patch('/users/1', data=json.dumps(updated_user))
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 401)

    # Attempt to update a user's data with malformed auth header
    def test_update_user_malformed_auth(self):
        response = self.client().patch('/users/1', headers=malformed_header,
                                       data=json.dumps(updated_user))
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 401)

    # Attempt to update a user's data with a user's JWT
    def test_update_user_as_user(self):
        user = updated_user
        user['id'] = sample_user_id
        user['displayName'] = 'user'
        response = self.client().patch('/users/' + sample_user_id, headers=user_header,
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
        response = self.client().patch('/users/' + sample_moderator_id, headers=user_header,
                                       data=json.dumps(user))
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 403)

    # Attempt to update a user's data with a moderator's JWT
    def test_update_user_as_mod(self):
        user = updated_user
        user['id'] = sample_moderator_id
        user['displayName'] = 'mod'
        response = self.client().patch('/users/' + sample_moderator_id, headers=moderator_header,
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
        response = self.client().patch('/users/' + sample_admin_id, headers=moderator_header,
                                       data=json.dumps(user))
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 403)

    # Attempt to update a user's data with an admin's JWT
    def test_update_user_as_admin(self):
        user = updated_user
        user['id'] = sample_admin_id
        user['displayName'] = 'admin'
        response = self.client().patch('/users/' + sample_admin_id, headers=admin_header,
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
        response = self.client().patch('/users/' + sample_user_id, headers=admin_header,
                                       data=json.dumps(user))
        response_data = json.loads(response.data)
        updated = response_data['updated']

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(updated['receivedH'], user['receivedH'])

    # Attempt to update a user's data with no ID (with admin's JWT)
    def test_update_no_id_user_as_admin(self):
        response = self.client().patch('/users/', headers=admin_header,
                                       data=json.dumps(updated_user))
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 404)

    # Get User's Posts Tests ('/users/<user_id>/posts', GET)
    # -------------------------------------------------------
    # Attempt to get a user's posts without auth header
    def test_get_user_posts_no_auth(self):
        response = self.client().get('/users/1/posts')
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 401)

    # Attempt to get a user's posts with malformed auth header
    def test_get_user_posts_malformed_auth(self):
        response = self.client().get('/users/1/posts',
                                     headers=malformed_header)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 401)

    # Attempt to get a user's posts with a user's JWT
    def test_get_user_posts_as_user(self):
        response = self.client().get('/users/1/posts', headers=user_header)
        response_data = json.loads(response.data)

        self.assertTrue(response_data['success'])
        self.assertTrue(response_data['posts'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['page'], 1)
        self.assertEqual(response_data['total_pages'], 2)
        self.assertEqual(len(response_data['posts']), 5)

    # Attempt to get a user's posts with a moderator's JWT
    def test_get_user_posts_as_mod(self):
        response = self.client().get('/users/4/posts',
                                     headers=moderator_header)
        response_data = json.loads(response.data)

        self.assertTrue(response_data['success'])
        self.assertTrue(response_data['posts'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['page'], 1)
        self.assertEqual(response_data['total_pages'], 1)
        self.assertEqual(len(response_data['posts']), 1)

    # Attempt to get a user's posts with an admin's JWT
    def test_get_user_posts_as_admin(self):
        response = self.client().get('/users/5/posts', headers=admin_header)
        response_data = json.loads(response.data)

        self.assertTrue(response_data['success'])
        self.assertTrue(response_data['posts'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['page'], 1)
        self.assertEqual(response_data['total_pages'], 1)
        self.assertEqual(len(response_data['posts']), 1)

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

    # Attempt to get a user's messages with a user's JWT
    def test_get_user_messages_as_user(self):
        response = self.client().get('/messages?userID=' + sample_user_id, headers=user_header)
        response_data = json.loads(response.data)

        self.assertTrue(response_data['success'])
        self.assertTrue(response_data['messages'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['current_page'], 1)
        self.assertEqual(response_data['total_pages'], 1)
        self.assertEqual(len(response_data['messages']), 2)

    # Attempt to get another user's messages with a user's JWT
    def test_get_another_users_messages_as_user(self):
        response = self.client().get('/messages?userID=' + sample_moderator_id, headers=user_header)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 403)

    # Attempt to get a user's messages with a moderator's JWT
    def test_get_user_messages_as_mod(self):
        response = self.client().get('/messages?userID=' + sample_moderator_id,
                                     headers=moderator_header)
        response_data = json.loads(response.data)

        self.assertTrue(response_data['success'])
        self.assertTrue(response_data['messages'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['current_page'], 1)
        self.assertEqual(response_data['total_pages'], 1)
        self.assertEqual(len(response_data['messages']), 1)

    # Attempt to get another user's messages with a moderator's JWT
    def test_get_another_users_messages_as_mod(self):
        response = self.client().get('/messages?userID=' + sample_admin_id,
                                     headers=moderator_header)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 403)

    # Attempt to get a user's messages with an admin's JWT
    def test_get_user_messages_as_admin(self):
        response = self.client().get('/messages?userID=' + sample_admin_id,
                                     headers=admin_header)
        response_data = json.loads(response.data)

        self.assertTrue(response_data['success'])
        self.assertTrue(response_data['messages'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['current_page'], 1)
        self.assertEqual(response_data['total_pages'], 1)
        self.assertEqual(len(response_data['messages']), 1)

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

    # Create Message Route Tests ('/message', POST)
    # -------------------------------------------------------
    # Attempt to create a message with no authorisation header
    def test_send_message_no_auth(self):
        response = self.client().post('/messages', data=json.dumps(new_message))
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
        self.assertEqual(response_message['messageText'], message['messageText'])

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
        self.assertEqual(response_message['messageText'], message['messageText'])

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
        self.assertEqual(response_message['messageText'], message['messageText'])

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

    # Delete Message Route Tests ('/message/<message_id>', DELETE)
    # -------------------------------------------------------
    # Attempt to delete a message with no authorisation header
    def test_delete_message_no_auth(self):
        response = self.client().delete('/messages/1')
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 401)

    # Attempt to delete a message with a malformed auth header
    def test_delete_message_malformed_auth(self):
        response = self.client().delete('/messages/1',
                                        headers=malformed_header)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 401)

    # Attempt to delete a message with a user's JWT
    def test_delete_message_as_user(self):
        response = self.client().delete('/messages/1', headers=user_header)
        response_data = json.loads(response.data)

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['deleted'], '1')

    # Attempt to delete another user's message (with a user's JWT)
    def test_delete_message_from_another_user_as_user(self):
        response = self.client().delete('/messages/7', headers=user_header)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 403)

    # Attempt to delete a message with a moderator's JWT
    def test_delete_message_as_mod(self):
        response = self.client().delete('/messages/5',
                                        headers=moderator_header)
        response_data = json.loads(response.data)

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['deleted'], '5')

    # Attempt to delete another user's message (with a moderator's JWT)
    def test_delete_message_from_another_user_as_mod(self):
        response = self.client().delete('/messages/8',
                                        headers=moderator_header)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 403)

    # Attempt to delete a message with an admin's JWT
    def test_delete_message_as_admin(self):
        response = self.client().delete('/messages/6', headers=admin_header)
        response_data = json.loads(response.data)

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['deleted'], '6')

    # Attempt to delete another user's message (with an admin's JWT)
    def test_delete_message_from_another_user_as_admin(self):
        response = self.client().delete('/messages/3', headers=admin_header)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 403)

    # Attempt to delete a user's message with no ID (with admin's JWT)
    def test_delete_no_id_user_message_as_admin(self):
        response = self.client().delete('/messages/', headers=admin_header)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 404)

    # Attempt to delete a nonexistent user's message (with admin's JWT)
    def test_delete_nonexistent_user_message_as_admin(self):
        response = self.client().delete('/messages/100', headers=admin_header)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 404)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
