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
malformed_header = { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' }
user_header = { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + user_jwt }
moderator_header = { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + moderator_jwt }
admin_header = { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + admin_jwt }

# Item Samples
new_post = '{\
"user_id": 1,\
"text": "test post",\
"date": "Sun Jun 07 2020 15:57:45 GMT+0300",\
"givenHugs": 0 }'

updated_post = '{\
"user_id": 1,\
"text": "test post",\
"date": "Sun Jun 07 2020 15:57:45 GMT+0300",\
"givenHugs": 0 }'

updated_user = '{\
"id": 1,\
"auth0Id": "",\
"displayName": "",\
"receivedH": 0,\
"givenH": 0,\
"loginCount": 0 }'

updated_display = '{\
"id": 1,\
"auth0Id": "",\
"displayName": "meow",\
"receivedH": 0,\
"givenH": 0,\
"loginCount": 0 }'

new_message_user = '{\
"fromId": 1,\
"forId": 4,\
"messageText": "meow",\
"date": "Sun Jun 07 2020 15:57:45 GMT+0300" }'

new_message_mod = '{\
"fromId": 1,\
"forId": 4,\
"messageText": "meow",\
"date": "Sun Jun 07 2020 15:57:45 GMT+0300" }'

new_message_admin = '{\
"fromId": 1,\
"forId": 4,\
"messageText": "meow",\
"date": "Sun Jun 07 2020 15:57:45 GMT+0300" }'


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
        response = self.client().post('/posts', data=new_post)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 401)

    # Attempt to create a post with a malformed auth header
    def test_send_post_malformed_auth(self):
        response = self.client().post('/posts', headers=malformed_header, data=new_post)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 401)

    # Attempt to create a post with a user's JWT
    def test_send_post_as_user(self):
        response = self.client().post('/posts', headers=user_header, data=new_post)
        response_data = json.loads(response.data)

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['posts'], new_post)

    # Attempt to create a post with a moderator's JWT
    def test_send_post_as_mod(self):
        response = self.client().post('/posts', headers=moderator_header, data=new_post)
        response_data = json.loads(response.data)

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['posts'], new_post)

    # Attempt to create a post with an admin's JWT
    def test_send_post_as_admin(self):
        response = self.client().post('/posts', headers=admin_header, data=new_post)
        response_data = json.loads(response.data)

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['posts'], new_post)


    # Update Post Route Tests ('/posts/<post_id>', PATCH)
    # -------------------------------------------------------
    # Attempt to update a post with no authorisation header
    def test_update_post_no_auth(self):
        response = self.client().patch('/posts/1', data=updated_post)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 401)

    # Attempt to update a post with a malformed auth header
    def test_update_post_malformed_auth(self):
        response = self.client().patch('/posts/1', headers=malformed_header, data=updated_post)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 401)

    # Attempt to update the user's post (with same user's JWT)
    def test_update_own_post_as_user(self):
        response = self.client().patch('/posts/1', headers=user_header, data=updated_post)
        response_data = json.loads(response.data)
        post_text = response_data['updated']

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(post_text['text'], updated_post[23:32])

    # Attempt to update another user's post (with user's JWT)
    def test_update_other_users_post_as_user(self):
        response = self.client().patch('/posts/1', headers=user_header, data=updated_post)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 403)

    # Attempt to update the moderator's post (with same moderator's JWT)
    def test_update_own_post_as_mod(self):
        response = self.client().patch('/posts/1', headers=moderator_header, data=updated_post)
        response_data = json.loads(response.data)
        post_text = response_data['updated']

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(post_text['text'], updated_post[23:32])

    # Attempt to update another user's post (with moderator's JWT)
    def test_update_other_users_post_as_mod(self):
        response = self.client().patch('/posts/1', headers=moderator_header, data=updated_post)
        response_data = json.loads(response.data)
        post_text = response_data['updated']

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(post_text['text'], updated_post[23:32])

    # Attempt to update the admin's post (with same admin's JWT)
    def test_update_own_post_as_admin(self):
        response = self.client().patch('/posts/1', headers=admin_header, data=updated_post)
        response_data = json.loads(response.data)
        post_text = response_data['updated']

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(post_text['text'], updated_post[23:32])

    # Attempt to update another user's post (with admin's JWT)
    def test_update_other_users_post_as_admin(self):
        response = self.client().patch('/posts/1', headers=admin_header, data=updated_post)
        response_data = json.loads(response.data)
        post_text = response_data['updated']

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(post_text['text'], updated_post[23:32])

    # Attempt to update a post with no ID (with admin's JWT)
    def test_update_no_id_post_as_admin(self):
        response = self.client().patch('/posts/', headers=admin_header, data=updated_post)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 400)

    # Attempt to update a post that doesn't exist (with admin's JWT)
    def test_update_nonexistent_post_as_admin(self):
        response = self.client().patch('/posts/100', headers=admin_header, data=updated_post)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 404)


    # Delete Post Route Tests ('/posts/<post_id>', DELETE)
    # -------------------------------------------------------
    # Attempt to delete a post with no authorisation header
    def test_delete_post_no_auth(self):
        response = self.client().delete('/posts/1')
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 401)

    # Attempt to delete a post with a malformed auth header
    def test_delete_post_malformed_auth(self):
        response = self.client().delete('/posts/1', headers=malformed_header)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 401)

    # Attempt to delete the user's post (with same user's JWT)
    def test_delete_own_post_as_user(self):
        response = self.client().delete('/posts/1', headers=user_header)
        response_data = json.loads(response.data)

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['deleted'], 1)

    # Attempt to delete another user's post (with user's JWT)
    def test_delete_other_users_post_as_user(self):
        response = self.client().delete('/posts/1', headers=user_header)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 403)

    # Attempt to delete the moderator's post (with same moderator's JWT)
    def test_delete_own_post_as_mod(self):
        response = self.client().delete('/posts/1', headers=moderator_header)
        response_data = json.loads(response.data)

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['deleted'], 1)

    # Attempt to delete another user's post (with moderator's JWT)
    def test_delete_other_users_post_as_mod(self):
        response = self.client().delete('/posts/1', headers=moderator_header)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 403)

    # Attempt to delete the admin's post (with same admin's JWT)
    def test_delete_own_post_as_admin(self):
        response = self.client().delete('/posts/1', headers=admin_header)
        response_data = json.loads(response.data)

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['deleted'], 1)

    # Attempt to delete another user's post (with admin's JWT)
    def test_delete_other_users_post_as_admin(self):
        response = self.client().delete('/posts/1', headers=admin_header)
        response_data = json.loads(response.data)

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['deleted'], 1)

    # Attempt to delete a post with no ID (with admin's JWT)
    def test_delete_no_id_post_as_admin(self):
        response = self.client().delete('/posts/', headers=admin_header)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 400)

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
        self.assertEqual(len(response_data['posts']), 10)
        self.assertEqual(response_data['total_pages'], 2)

    # Attempt to get page 2 of full new posts
    def test_get_full_new_posts_page_2(self):
        response = self.client().get('/posts/new?page=2')
        response_data = json.loads(response.data)

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response_data['posts']), 10)
        self.assertEqual(response_data['total_pages'], 2)

    # Attempt to get page 1 of full suggested posts
    def test_get_full_suggested_posts(self):
        response = self.client().get('/posts/suggested')
        response_data = json.loads(response.data)

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response_data['posts']), 10)
        self.assertEqual(response_data['total_pages'], 2)

    # Attempt to get page 2 of full suggested posts
    def test_get_full_suggested_posts_page_2(self):
        response = self.client().get('/posts/suggested?page=2')
        response_data = json.loads(response.data)

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response_data['posts']), 10)
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
        response = self.client().get('/users/1', headers=user_header)
        response_data = json.loads(response.data)
        user_data = response_data['user']

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(user_data['id'], 1)

    # Attempt to get a user's data with a moderator's JWT
    def test_get_user_data_as_mod(self):
        response = self.client().get('/users/1', headers=moderator_header)
        response_data = json.loads(response.data)
        user_data = response_data['user']

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(user_data['id'], 1)

    # Attempt to get a user's data with an admin's JWT
    def test_get_user_data_as_admin(self):
        response = self.client().get('/users/1', headers=admin_header)
        response_data = json.loads(response.data)
        user_data = response_data['user']

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(user_data['id'], 1)

    # Attempt to get a user's data with no ID (with admin's JWT)
    def test_get_no_id_user_as_admin(self):
        response = self.client().get('/users/', headers=admin_header)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 400)

    # Attempt to get a nonexistent user's data (with admin's JWT)
    def test_get_nonexistent_user_as_admin(self):
        response = self.client().get('/users/100', headers=admin_header)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 404)


    # Edit User Data Tests ('/users/<user_id>', PATCH)
    # -------------------------------------------------------
    # Attempt to update a user's data without auth header
    def test_update_user_no_auth(self):
        response = self.client().patch('/users/1', data=updated_user)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 401)

    # Attempt to update a user's data with malformed auth header
    def test_update_user_malformed_auth(self):
        response = self.client().patch('/users/1', headers=malformed_header, data=updated_user)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 401)

    # Attempt to update a user's data with a user's JWT
    def test_update_user_as_user(self):
        response = self.client().patch('/users/1', headers=user_header, data=updated_user)
        response_data = json.loads(response.data)
        updated = response_data['updated']

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(updated['receivedH'], updated_user[54:55])
        self.assertEqual(updated['givenH'], updated_user[66:67])

    # Attempt to update another user's display name with a user's JWT
    def test_update_other_users_display_name_as_user(self):
        response = self.client().patch('/users/1', headers=user_header, data=updated_display)
        response_data = json.loads(response.data)
        updated = response_data['updated']

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 403)

    # Attempt to update a user's data with a moderator's JWT
    def test_update_user_as_mod(self):
        response = self.client().patch('/users/1', headers=moderator_header, data=updated_user)
        response_data = json.loads(response.data)
        updated = response_data['updated']

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(updated['receivedH'], updated_user[54:55])
        self.assertEqual(updated['givenH'], updated_user[66:67])

    # Attempt to update another user's display name with a moderator's JWT
    def test_update_other_users_display_name_as_mod(self):
        response = self.client().patch('/users/1', headers=moderator_header, data=updated_display)
        response_data = json.loads(response.data)
        updated = response_data['updated']

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 403)

    # Attempt to update a user's data with an admin's JWT
    def test_update_user_as_admin(self):
        response = self.client().patch('/users/1', headers=admin_header, data=updated_user)
        response_data = json.loads(response.data)
        updated = response_data['updated']

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(updated['receivedH'], updated_user[54:55])
        self.assertEqual(updated['givenH'], updated_user[66:67])

    # Attempt to update another user's display name with an admin's JWT
    def test_update_user_as_admin(self):
        response = self.client().patch('/users/1', headers=admin_header, data=updated_display)
        response_data = json.loads(response.data)
        updated = response_data['updated']

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(updated['receivedH'], updated_user[39:43])

    # Attempt to update a user's data with no ID (with admin's JWT)
    def test_update_no_id_user_as_admin(self):
        response = self.client().patch('/users/', headers=admin_header, data=updated_user)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 400)


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
        response = self.client().get('/users/1/posts', headers=malformed_header)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 401)

    # Attempt to get a user's posts with a user's JWT
    def test_get_user_posts_as_user(self):
        response = self.client().get('/users/1/posts', headers=user_header)
        response_data = json.loads(response.data)

        self.assertTrue(response_data['success'])
        self.assertTrue(esponse_data['posts'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['page'], 1)
        self.assertEqual(response_data['total_pages'], 2)
        self.assertEqual(len(response_data['posts']), 5)

    # Attempt to get a user's posts with a moderator's JWT
    def test_get_user_posts_as_mod(self):
        response = self.client().get('/users/1/posts', headers=moderator_header)
        response_data = json.loads(response.data)

        self.assertTrue(response_data['success'])
        self.assertTrue(esponse_data['posts'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['page'], 1)
        self.assertEqual(response_data['total_pages'], 2)
        self.assertEqual(len(response_data['posts']), 5)

    # Attempt to get a user's posts with an admin's JWT
    def test_get_user_posts_as_admin(self):
        response = self.client().get('/users/1/posts', headers=admin_header)
        response_data = json.loads(response.data)

        self.assertTrue(response_data['success'])
        self.assertTrue(esponse_data['posts'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['page'], 1)
        self.assertEqual(response_data['total_pages'], 2)
        self.assertEqual(len(response_data['posts']), 5)


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
        response = self.client().get('/messages?userID=1', headers=malformed_header)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 401)

    # Attempt to get a user's messages with a user's JWT
    def test_get_user_messages_as_user(self):
        response = self.client().get('/messages?userID=1', headers=user_header)
        response_data = json.loads(response.data)

        self.assertTrue(response_data['success'])
        self.assertTrue(esponse_data['messages'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['page'], 1)
        self.assertEqual(response_data['total_pages'], 1)
        self.assertEqual(len(response_data['messages']), 1)

    # Attempt to get another user's messages with a user's JWT
    def test_get_another_users_messages_as_user(self):
        response = self.client().get('/messages?userID=4', headers=user_header)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 403)

    # Attempt to get a user's messages with a moderator's JWT
    def test_get_user_messages_as_mod(self):
        response = self.client().get('/messages?userID=4', headers=moderator_header)
        response_data = json.loads(response.data)

        self.assertTrue(response_data['success'])
        self.assertTrue(esponse_data['messages'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['page'], 1)
        self.assertEqual(response_data['total_pages'], 1)
        self.assertEqual(len(response_data['messages']), 1)

    # Attempt to get another user's messages with a moderator's JWT
    def test_get_another_users_messages_as_mod(self):
        response = self.client().get('/messages?userID=1', headers=moderator_header)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 403)

    # Attempt to get a user's messages with an admin's JWT
    def test_get_user_messages_as_admin(self):
        response = self.client().get('/messages?userID=1', headers=admin_header)
        response_data = json.loads(response.data)

        self.assertTrue(response_data['success'])
        self.assertTrue(esponse_data['messages'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['page'], 1)
        self.assertEqual(response_data['total_pages'], 1)
        self.assertEqual(len(response_data['messages']), 1)

    # Attempt to get another user's messages with an admin's JWT
    def test_get_another_users_messages_as_admin(self):
        response = self.client().get('/messages?userID=1', headers=admin_header)
        response_data = json.loads(response.data)

        self.assertTrue(response_data['success'])
        self.assertTrue(esponse_data['messages'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['page'], 1)
        self.assertEqual(response_data['total_pages'], 1)
        self.assertEqual(len(response_data['messages']), 1)

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
        response = self.client().post('/messages', data=new_message)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 401)

    # Attempt to create a message with a malformed auth header
    def test_send_message_malformed_auth(self):
        response = self.client().post('/messages', headers=malformed_header, data=new_message)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 401)

    # Attempt to create a message with a user's JWT
    def test_send_message_as_user(self):
        response = self.client().post('/messages', headers=user_header, data=new_message_user)
        response_data = json.loads(response.data)
        message = response_data['message']

        self.assertTrue(response_data['success'])
        self.assertTrue(response_data['message'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(message['messageText'], new_message_user[40:44])

    # Attempt to create a message from another user (with a user's JWT)
    def test_send_message_from_another_user_as_user(self):
        response = self.client().post('/messages', headers=user_header, data=new_message_mod)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 403)

    # Attempt to create a message with a moderator's JWT
    def test_send_message_as_mod(self):
        response = self.client().post('/messages', headers=moderator_header, data=new_message_mod)
        response_data = json.loads(response.data)

        self.assertTrue(response_data['success'])
        self.assertTrue(response_data['message'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(message['messageText'], new_message_mod[40:44])

    # Attempt to create a message from another user (with a moderator's JWT)
    def test_send_message_from_another_user_as_mod(self):
        response = self.client().post('/messages', headers=moderator_header, data=new_message_admin)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 403)

    # Attempt to create a message with an admin's JWT
    def test_send_message_as_admin(self):
        response = self.client().post('/messages', headers=admin_header, data=new_message_admin)
        response_data = json.loads(response.data)

        self.assertTrue(response_data['success'])
        self.assertTrue(response_data['message'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(message['messageText'], new_message_admin[40:44])

    # Attempt to create a message from another user (with an admin's JWT)
    def test_send_message_from_another_user_as_admin(self):
        response = self.client().post('/messages', headers=admin_header, data=new_message_user)
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
        response = self.client().delete('/messages/1', headers=malformed_header)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 401)

    # Attempt to delete a message with a user's JWT
    def test_delete_message_as_user(self):
        response = self.client().delete('/messages/1', headers=user_header)
        response_data = json.loads(response.data)

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(message['deleted'], 1)

    # Attempt to delete another user's message (with a user's JWT)
    def test_delete_message_from_another_user_as_user(self):
        response = self.client().delete('/messages/1', headers=user_header)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 403)

    # Attempt to delete a message with a moderator's JWT
    def test_delete_message_as_mod(self):
        response = self.client().delete('/messages/1', headers=moderator_header)
        response_data = json.loads(response.data)

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(message['deleted'], 1)

    # Attempt to delete another user's message (with a moderator's JWT)
    def test_delete_message_from_another_user_as_mod(self):
        response = self.client().delete('/messages/1', headers=moderator_header)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 403)

    # Attempt to delete a message with an admin's JWT
    def test_delete_message_as_admin(self):
        response = self.client().delete('/messages/1', headers=admin_header)
        response_data = json.loads(response.data)

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(message['deleted'], 1)

    # Attempt to delete another user's message (with an admin's JWT)
    def test_delete_message_from_another_user_as_admin(self):
        response = self.client().delete('/messages/1', headers=admin_header)
        response_data = json.loads(response.data)

        self.assertTrue(response_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(message['deleted'], 1)

    # Attempt to delete a user's message with no ID (with admin's JWT)
    def test_delete_no_id_user_message_as_admin(self):
        response = self.client().delete('/messages', headers=admin_header)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 400)

    # Attempt to delete a nonexistent user's message (with admin's JWT)
    def test_delete_nonexistent_user_message_as_admin(self):
        response = self.client().delete('/messages/100', headers=admin_header)
        response_data = json.loads(response.data)

        self.assertFalse(response_data['success'])
        self.assertEqual(response.status_code, 404)



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
