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


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
