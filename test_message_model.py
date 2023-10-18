"""Message model tests."""

# run these tests with:
# python -m unittest test_message_model.py

import os
from unittest import TestCase

from models import db, User, Message, Follows
from sqlalchemy.exc import IntegrityError

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app

db.create_all()


class MessageModelTestCase(TestCase):
    """Test Message model."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

    def test_message_model(self):
        """Does basic model work?
        Runs tests for: 
            model creation
            user relationship
            and likes relationship
        """

        u = User.query.one()

        m = Message(text='test message',
                    user_id=u.id)
        
        db.session.add(m)
        db.session.commit()
        
        self.assertEqual(u, m.user)
        self.assertEqual(len(m.likes), 0)

        u.likes.append(m)
        db.session.commit()

        self.assertEqual(len(m.likes), 1)

        with self.assertRaises(IntegrityError):
            m2 = Message(text='test message', user_id=9999999)
            db.session.add(m2)
            db.session.commit()