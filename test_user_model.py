"""User model tests."""

# run these tests with:
# python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows
from sqlalchemy.exc import IntegrityError

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app

db.create_all()


class UserModelTestCase(TestCase):
    """Test User model."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    def test_user_repr(self):
        """Is our repr working?"""

        u1 = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u1)
        db.session.commit()

        self.assertEqual(repr(u1), f'<User #{u1.id}: testuser, test@test.com>')

    def test_user_is_followed_by(self):
        """Is followed by working?"""

        u1 = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        u2 = User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD2"
        )

        db.session.add(u1, u2)
        db.session.commit()

        u1.following.append(u2)
        db.session.commit()
        followed_by = u2.is_followed_by(u1)

        self.assertEqual(followed_by, True)

        u1.following.remove(u2)
        db.session.commit()
        followed_by = u2.is_followed_by(u1)
        self.assertEqual(followed_by, False)

    def test_user_is_following(self):
        """"Is following working?"""

        u1 = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        u2 = User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD2"
        )

        db.session.add(u1, u2)
        db.session.commit()

        u1.following.append(u2)
        db.session.commit()
        following = u1.is_following(u2)

        self.assertEqual(following, True)

        u1.following.remove(u2)
        db.session.commit()
        following = u1.is_following(u2)

        self.assertEqual(following, False)

    def test_user_signup(self):
        """Is sign up working?"""

        testuser = User.signup(username='Brendino',
                               email='brendenjarias@gmail.com',
                               password='testpass',
                               image_url='www.google.com/cats')
        
        db.session.commit()
        user = User.query.one()

        self.assertEqual(user.username, 'Brendino')
        self.assertIsInstance(testuser, User)

        with self.assertRaises(IntegrityError):
            testuser2 = User.signup(username='Brendino',
                                   email='brendenjarias@hotmail.com',
                                   password='testpass',
                                   image_url='www.google.com/cats')
            db.session.commit()

    def test_user_authenticate(self):
        """Is authentication working?"""

        testuser = User.signup(username='Brendino',
                               email='brendenjarias@gmail.com',
                               password='testpass',
                               image_url='www.google.com/cats')
        db.session.commit()

        auth = User.authenticate(username='Brendino',password='testpass')
        self.assertIsInstance(auth, User)

        auth = User.authenticate(username='Brendino',password='wrongpassword')
        self.assertEqual(auth, False)

        auth = User.authenticate(username='wrong_username',password='testpass')
        self.assertEqual(auth, False)