# MIT License
#
# Copyright (c) 2020-2023 Send A Hug
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

import os
import json
from typing import Dict
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate  # type: ignore
from flask import Flask

# Database configuration
database_path = os.environ.get("DATABASE_URL", "")

db = SQLAlchemy()


# Database setup
def initialise_db(app: Flask) -> SQLAlchemy:
    db.init_app(app)
    migrate = Migrate(app, db)  # NOQA - required by flask-migrate

    return db


# Models
# -----------------------------------------------------------------
# Post Model
class Post(db.Model):  # type: ignore[name-defined]
    __tablename__ = "posts"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    text = db.Column(db.String(480), nullable=False)
    date = db.Column(db.DateTime)
    given_hugs = db.Column(db.Integer, default=0)
    open_report = db.Column(db.Boolean, nullable=False, default=False)
    sent_hugs = db.Column(db.Text)
    report = db.relationship("Report", backref="post")

    # Format method
    # Responsible for returning a JSON object
    def format(self, user: str = ""):
        return {
            "id": self.id,
            "userId": self.user_id,
            "user": user,
            "text": self.text,
            "date": self.date,
            "givenHugs": self.given_hugs,
            "sentHugs": list(filter(None, self.sent_hugs.split(" "))),
        }


# User Model
class User(db.Model):  # type: ignore[name-defined]
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    display_name = db.Column(db.String(60), nullable=False)
    auth0_id = db.Column(db.String(), nullable=False)
    received_hugs = db.Column(db.Integer, default=0)
    given_hugs = db.Column(db.Integer, default=0)
    login_count = db.Column(db.Integer, default=1)
    role = db.Column(db.String(), default="user")
    blocked = db.Column(db.Boolean, nullable=False, default=False)
    release_date = db.Column(db.DateTime)
    open_report = db.Column(db.Boolean, nullable=False, default=False)
    last_notifications_read = db.Column(db.DateTime)
    auto_refresh = db.Column(db.Boolean, default=True)
    refresh_rate = db.Column(db.Integer, default=20)
    push_enabled = db.Column(db.Boolean, default=False)
    selected_character = db.Column(db.String(6), default="kitty")
    icon_colours = db.Column(
        db.String(),
        default='{"character":"#BA9F93", "lbg":"#e2a275",'
        '"rbg":"#f8eee4", "item":"#f4b56a"}',
    )
    posts = db.relationship("Post", backref="user")

    # Format method
    # Responsible for returning a JSON object
    def format(self):
        return {
            "id": self.id,
            "auth0Id": self.auth0_id,
            "displayName": self.display_name,
            "receivedH": self.received_hugs,
            "givenH": self.given_hugs,
            "loginCount": self.login_count,
            "role": self.role,
            "blocked": self.blocked,
            "releaseDate": self.release_date,
            "autoRefresh": self.auto_refresh,
            "refreshRate": self.refresh_rate,
            "pushEnabled": self.push_enabled,
            "last_notifications_read": self.last_notifications_read,
            "selectedIcon": self.selected_character,
            "iconColours": json.loads(self.icon_colours)
            if self.icon_colours
            else self.icon_colours,
        }


# Message Model
class Message(db.Model):  # type: ignore[name-defined]
    __tablename__ = "messages"
    id = db.Column(db.Integer, primary_key=True)
    from_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    for_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    text = db.Column(db.String(480), nullable=False)
    date = db.Column(db.DateTime)
    thread = db.Column(db.Integer, db.ForeignKey("threads.id"), nullable=False)
    from_deleted = db.Column(db.Boolean, nullable=False, default=False)
    for_deleted = db.Column(db.Boolean, nullable=False, default=False)

    # Format method
    # Responsible for returning a JSON object
    def format(
        self,
        from_name: str = "",
        from_icon: str = "",
        from_colous: Dict[str, str] = {},
        for_name: str = "",
        for_icon: str = "",
        for_colours: Dict[str, str] = {},
    ):
        return {
            "id": self.id,
            "fromId": self.from_id,
            "from": {
                "displayName": from_name,
                "selectedIcon": from_icon,
                "iconColours": from_colous,
            },
            "forId": self.for_id,
            "for": {
                "displayName": for_name,
                "selectedIcon": for_icon,
                "iconColours": for_colours,
            },
            "messageText": self.text,
            "date": self.date,
            "threadID": self.thread,
        }


# Thread Model
class Thread(db.Model):  # type: ignore[name-defined]
    __tablename__ = "threads"
    id = db.Column(db.Integer, primary_key=True)
    user_1_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user_2_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user_1_deleted = db.Column(db.Boolean, nullable=False, default=False)
    user_2_deleted = db.Column(db.Boolean, nullable=False, default=False)
    messages = db.relationship("Message", backref="threads")

    # Format method
    # Responsible for returning a JSON object
    def format(self):
        return {"id": self.id, "user1": self.user_1_id, "user2": self.user_2_id}


# Report Model
class Report(db.Model):  # type: ignore[name-defined]
    __tablename__ = "reports"
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(10), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"))
    reporter = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    report_reason = db.Column(db.String(120), nullable=False)
    date = db.Column(db.DateTime)
    dismissed = db.Column(db.Boolean, nullable=False, default=False)
    closed = db.Column(db.Boolean, nullable=False, default=False)

    # Format method
    # Responsible for returning a JSON object
    def format(self):
        # If the report was for a user
        if self.type.lower() == "user":
            return_report = {
                "id": self.id,
                "type": self.type,
                "userID": self.user_id,
                "reporter": self.reporter,
                "reportReason": self.report_reason,
                "date": self.date,
                "dismissed": self.dismissed,
                "closed": self.closed,
            }
        # If the report was for a post
        elif self.type.lower() == "post":
            return_report = {
                "id": self.id,
                "type": self.type,
                "userID": self.user_id,
                "postID": self.post_id,
                "reporter": self.reporter,
                "reportReason": self.report_reason,
                "date": self.date,
                "dismissed": self.dismissed,
                "closed": self.closed,
            }

        return return_report


# Notification Model
class Notification(db.Model):  # type: ignore[name-defined]
    __tablename__ = "notifications"
    id = db.Column(db.Integer, primary_key=True)
    for_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    from_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    type = db.Column(db.String(), nullable=False)
    text = db.Column(db.String(), nullable=False)
    date = db.Column(db.DateTime, nullable=False)

    # Format method
    def format(self, from_name: str = "", for_name: str = ""):
        return {
            "id": self.id,
            "fromId": self.from_id,
            "from": from_name,
            "forId": self.for_id,
            "for": for_name,
            "type": self.type,
            "text": self.text,
            "date": self.date,
        }


# Notification Subscription Model
class NotificationSub(db.Model):  # type: ignore[name-defined]
    __tablename__ = "subscriptions"
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    endpoint = db.Column(db.String(), nullable=False)
    subscription_data = db.Column(db.Text, nullable=False)

    # Format method
    def format(self):
        return {
            "id": self.id,
            "user_id": self.user,
            "endpoint": self.endpoint,
            "subscription_data": self.subscription_data,
        }


# Filter
class Filter(db.Model):  # type: ignore[name-defined]
    __tablename__ = "filters"
    id = db.Column(db.Integer, primary_key=True)
    filter = db.Column(db.String(), nullable=False)

    # Format method
    def format(self):
        return {"id": self.id, "filter": self.filter}
