import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from app import create_app
from models import create_db, Post, User, Message


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



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
