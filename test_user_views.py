"""User View tests."""

# run these tests with:
# FLASK_ENV=production python -m unittest test_user_views.py

import os
from unittest import TestCase

from models import db, connect_db, Message, User
from sqlalchemy.orm.exc import NoResultFound


os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app, CURR_USER_KEY

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False


class UserViewTestCase(TestCase):
    """Test views for user."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()

    def test_view_users(self):
        """Can view users?"""

        with self.client as c:
            resp = c.get("/users")

            self.assertEqual(resp.status_code, 200)

    def test_view_user_profile(self):
        """Can view a user profile?"""

        with self.client as c:
            resp = c.get(f"/users/{self.testuser.id}")

            self.assertEqual(resp.status_code, 200)

    def test_show_following(self):
        """Can view user following/followers/likes only when logged in?"""

        with self.client as c:
            resp = c.get(f'/users/{self.testuser.id}/following')
            self.assertEqual(resp.status_code, 302)

            resp = c.get(f'/users/{self.testuser.id}/followers')
            self.assertEqual(resp.status_code, 302)

            resp = c.get(f'/users/{self.testuser.id}/likes')
            self.assertEqual(resp.status_code, 302)

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get(f'/users/{self.testuser.id}/following')
            self.assertEqual(resp.status_code, 200)

            resp = c.get(f'/users/{self.testuser.id}/followers')
            self.assertEqual(resp.status_code, 200)

            resp = c.get(f'/users/{self.testuser.id}/likes')
            self.assertEqual(resp.status_code, 200)

    def test_add_or_delete_message_logged_out(self):
        """
        when not logged in:
            can we not add a message?
            can we not delete our own message?
        """
        m = Message(text='test message',user_id=self.testuser.id)
        db.session.add(m)
        db.session.commit()

        with self.client as c:
            resp = c.get('/messages/new')
            self.assertEqual(resp.status_code, 302)

            resp = c.post(f'/messages/{m.id}/delete')
            self.assertEqual(resp.status_code, 302)


    def test_add_or_delete_message_logged_in(self):
        """
        when logged in:
            can we add a message?
            can we delete our own message?
        """

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get('/messages/new')
            self.assertEqual(resp.status_code, 200)

            resp = c.post("/messages/new", data={"text": "Hello"})
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            resp = c.post(f"/messages/{msg.id}/delete")
            self.assertEqual(resp.status_code, 302)

def test_add_message_as_another_user(self):
    """When logged in, are you prohibited from adding a message as another user?"""

    with self.client as c:
        with c.session_transaction() as sess:
            sess[CURR_USER_KEY] = self.testuser.id

        resp = c.post("/messages/new", data={"text": "Hello", "user_id": 99999999})

        self.assertEqual(resp.status_code, 302)

def test_delete_message_as_another_user(self):
    """When logged in, are you prohibited from deleting a message as another user?"""

    m = Message(text='test message', user_id=self.testuser.id)
    db.session.add(m)
    db.session.commit()

    with self.client as c:
        with c.session_transaction() as sess:
            sess[CURR_USER_KEY] = self.testuser.id

        resp = c.post(f"/messages/{m.id}/delete")

        self.assertEqual(resp.status_code, 302)

        message_in_db = Message.query.get(m.id)
        self.assertIsNotNone(message_in_db)
