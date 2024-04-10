# MIT License
#
# Copyright (c) 2020-2024 Send A Hug
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

from datetime import datetime
import os
import json
from typing import List, Optional

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate  # type: ignore
from flask import Flask
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, column_property
from sqlalchemy import DateTime, Text, select
from sqlalchemy.dialects.postgresql import ARRAY

# Database configuration
database_path = os.environ.get("DATABASE_URL", "")

db = SQLAlchemy()


# Database setup
def initialise_db(app: Flask) -> SQLAlchemy:
    db.init_app(app)
    migrate = Migrate(app, db)  # NOQA - required by flask-migrate

    return db


# SQLAlchemy Tables
roles_permissions_map = db.Table(
    "roles_permissions_map",
    db.Column("role_id", db.Integer, db.ForeignKey("roles.id"), primary_key=True),
    db.Column(
        "permission_id", db.Integer, db.ForeignKey("permissions.id"), primary_key=True
    ),
)


# Models
# -----------------------------------------------------------------
# Post Model
class Post(db.Model):  # type: ignore[name-defined]
    __tablename__ = "posts"
    id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    user_id: Mapped[int] = db.Column(
        db.Integer,
        db.ForeignKey("users.id", onupdate="CASCADE", ondelete="SET NULL"),
        nullable=False,
    )
    user: Mapped["User"] = db.relationship(
        "User", back_populates="posts"
    )  # type: ignore
    text: Mapped[str] = db.Column(db.String(480), nullable=False)
    date: Mapped[Optional[DateTime]] = db.Column(db.DateTime)
    given_hugs: Mapped[Optional[int]] = db.Column(db.Integer, default=0)
    open_report: Mapped[bool] = db.Column(db.Boolean, nullable=False, default=False)
    # TODO: This should be a list of integers
    sent_hugs: Mapped[Optional[List[int]]] = db.Column(ARRAY(db.Integer))
    report: Mapped[Optional["Report"]] = db.relationship(
        "Report", back_populates="post"
    )  # type: ignore

    @hybrid_property
    def user_name(self):
        return self.user.display_name

    # Format method
    # Responsible for returning a JSON object
    def format(self):
        return {
            "id": self.id,
            "userId": self.user_id,
            "user": self.user_name,
            "text": self.text,
            "date": self.date,
            "givenHugs": self.given_hugs,
            "sentHugs": list(filter(None, self.sent_hugs)) if self.sent_hugs else [],
        }


# User Model
class User(db.Model):  # type: ignore[name-defined]
    __tablename__ = "users"
    id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    display_name: Mapped[str] = db.Column(db.String(60), nullable=False)
    auth0_id: Mapped[str] = db.Column(db.String(), nullable=False)
    received_hugs: Mapped[int] = db.Column(db.Integer, default=0)
    given_hugs: Mapped[Optional[int]] = db.Column(db.Integer, default=0)
    login_count: Mapped[Optional[int]] = db.Column(db.Integer, default=1)
    role_id: Mapped[int] = db.Column(
        db.Integer,
        db.ForeignKey("roles.id", onupdate="CASCADE", ondelete="SET NULL"),
        default=4,
    )
    role: Mapped[Optional["Role"]] = db.relationship(
        "Role", foreign_keys="User.role_id"
    )  # type: ignore
    blocked: Mapped[bool] = db.Column(db.Boolean, nullable=False, default=False)
    release_date: Mapped[Optional[DateTime]] = db.Column(db.DateTime)
    open_report: Mapped[bool] = db.Column(db.Boolean, nullable=False, default=False)
    last_notifications_read: Mapped[Optional[datetime]] = db.Column(db.DateTime)
    auto_refresh: Mapped[Optional[bool]] = db.Column(db.Boolean, default=True)
    refresh_rate: Mapped[Optional[int]] = db.Column(db.Integer, default=20)
    push_enabled: Mapped[Optional[bool]] = db.Column(db.Boolean, default=False)
    selected_character: Mapped[Optional[str]] = db.Column(db.String(6), default="kitty")
    icon_colours: Mapped[Optional[str]] = db.Column(
        db.String(),
        default='{"character":"#BA9F93", "lbg":"#e2a275",'
        '"rbg":"#f8eee4", "item":"#f4b56a"}',
    )
    posts: Mapped[Optional[List["Post"]]] = db.relationship(
        "Post", back_populates="user"
    )  # type: ignore
    sent_messages: Mapped[Optional[List["Message"]]] = db.relationship(
        "Message", back_populates="from_user", foreign_keys="Message.from_id"
    )  # type: ignore
    received_messages: Mapped[Optional[List["Message"]]] = db.relationship(
        "Message", back_populates="for_user", foreign_keys="Message.for_id"
    )  # type: ignore
    # Column properties
    post_count = column_property(
        select(db.func.count(Post.id)).where(Post.user_id == id).scalar_subquery()
    )

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
            "role": self.role.format() if self.role else None,
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
            "posts": self.post_count,
        }


# Message Model
class Message(db.Model):  # type: ignore[name-defined]
    __tablename__ = "messages"
    id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    from_id: Mapped[int] = db.Column(
        db.Integer,
        # TODO: This will fail if the user is deleted
        db.ForeignKey("users.id", onupdate="CASCADE", ondelete="SET NULL"),
        nullable=False,
    )
    from_user: Mapped["User"] = db.relationship(
        "User", back_populates="sent_messages", foreign_keys="Message.from_id"
    )  # type: ignore
    for_id: Mapped[int] = db.Column(
        db.Integer,
        # TODO: This will fail if the user is deleted
        db.ForeignKey("users.id", onupdate="CASCADE", ondelete="SET NULL"),
        nullable=False,
    )
    for_user: Mapped["User"] = db.relationship(
        "User", back_populates="received_messages", foreign_keys="Message.for_id"
    )  # type: ignore
    text: Mapped[str] = db.Column(db.String(480), nullable=False)
    date: Mapped[Optional[DateTime]] = db.Column(db.DateTime)
    thread: Mapped[int] = db.Column(
        db.Integer,
        # TODO: This will fail if the thread is deleted
        db.ForeignKey("threads.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    thread_details: Mapped["Thread"] = db.relationship(
        "Thread", back_populates="messages"
    )  # type: ignore
    from_deleted: Mapped[bool] = db.Column(db.Boolean, nullable=False, default=False)
    for_deleted: Mapped[bool] = db.Column(db.Boolean, nullable=False, default=False)
    # Column Properties
    from_name = column_property(
        select(User.display_name).where(User.id == from_id).scalar_subquery()
    )
    from_icon = column_property(
        select(User.selected_character).where(User.id == from_id).scalar_subquery()
    )
    from_colours = column_property(
        select(User.icon_colours).where(User.id == from_id).scalar_subquery()
    )
    for_name = column_property(
        select(User.display_name).where(User.id == for_id).scalar_subquery()
    )
    for_icon = column_property(
        select(User.selected_character).where(User.id == for_id).scalar_subquery()
    )
    for_colours = column_property(
        select(User.icon_colours).where(User.id == for_id).scalar_subquery()
    )

    # Format method
    # Responsible for returning a JSON object
    def format(self):
        return {
            "id": self.id,
            "fromId": self.from_id,
            "from": {
                "displayName": self.from_name,
                "selectedIcon": self.from_icon,
                "iconColours": json.loads(self.from_colours)
                if self.from_colours
                else self.from_colours,
            },
            "forId": self.for_id,
            "for": {
                "displayName": self.for_name,
                "selectedIcon": self.for_icon,
                "iconColours": json.loads(self.for_colours)
                if self.for_colours
                else self.for_colours,
            },
            "messageText": self.text,
            "date": self.date,
            "threadID": self.thread,
        }


# Thread Model
class Thread(db.Model):  # type: ignore[name-defined]
    __tablename__ = "threads"
    id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    user_1_id: Mapped[int] = db.Column(
        db.Integer,
        # TODO: This will fail if the user is deleted
        db.ForeignKey("users.id", onupdate="CASCADE", ondelete="SET NULL"),
        nullable=False,
    )
    user_1: Mapped["User"] = db.relationship(
        "User", foreign_keys="Thread.user_1_id"
    )  # type: ignore
    user_2_id: Mapped[int] = db.Column(
        db.Integer,
        # TODO: This will fail if the user is deleted
        db.ForeignKey("users.id", onupdate="CASCADE", ondelete="SET NULL"),
        nullable=False,
    )
    user_2: Mapped["User"] = db.relationship(
        "User", foreign_keys="Thread.user_2_id"
    )  # type: ignore
    user_1_deleted: Mapped[bool] = db.Column(db.Boolean, nullable=False, default=False)
    user_2_deleted: Mapped[bool] = db.Column(db.Boolean, nullable=False, default=False)
    messages: Mapped[List[Message]] = db.relationship(
        "Message", back_populates="thread_details"
    )  # type: ignore
    # Column properties
    message_count = column_property(
        select(db.func.count(Message.id))
        .where(Message.thread == id)
        .group_by(Message.thread)
        .scalar_subquery()
    )
    latest_message_date = column_property(
        select(db.func.max(Message.date))
        .where(Message.thread == id)
        .group_by(Message.thread)
        .scalar_subquery()
    )
    user_1_name = column_property(
        select(User.display_name).where(User.id == user_1_id).scalar_subquery()
    )
    user_1_icon = column_property(
        select(User.selected_character).where(User.id == user_1_id).scalar_subquery()
    )
    user_1_colours = column_property(
        select(User.icon_colours).where(User.id == user_1_id).scalar_subquery()
    )
    user_2_name = column_property(
        select(User.display_name).where(User.id == user_2_id).scalar_subquery()
    )
    user_2_icon = column_property(
        select(User.selected_character).where(User.id == user_2_id).scalar_subquery()
    )
    user_2_colours = column_property(
        select(User.icon_colours).where(User.id == user_2_id).scalar_subquery()
    )

    # Format method
    # Responsible for returning a JSON object
    def format(self):
        return {
            "id": self.id,
            "user1": {
                "displayName": self.user_1_name,
                "selectedIcon": self.user_1_icon,
                "iconColours": json.loads(self.user_1_colours)
                if self.user_1_colours
                else self.user_1_colours,
            },
            "user1Id": self.user_1_id,
            "user2": {
                "displayName": self.user_2_name,
                "selectedIcon": self.user_2_icon,
                "iconColours": json.loads(self.user_2_colours)
                if self.user_2_colours
                else self.user_2_colours,
            },
            "user2Id": self.user_2_id,
            "numMessages": self.message_count,
            "latestMessage": self.latest_message_date,
        }


# Report Model
class Report(db.Model):  # type: ignore[name-defined]
    __tablename__ = "reports"
    id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    type: Mapped[str] = db.Column(db.String(10), nullable=False)
    user_id: Mapped[int] = db.Column(
        db.Integer,
        # TODO: This will fail if the user is deleted
        db.ForeignKey("users.id", onupdate="CASCADE", ondelete="SET NULL"),
        nullable=False,
    )
    user: Mapped["User"] = db.relationship(
        "User", foreign_keys="Report.user_id"
    )  # type: ignore
    post_id: Mapped[Optional[int]] = db.Column(
        db.Integer, db.ForeignKey("posts.id", onupdate="CASCADE", ondelete="SET NULL")
    )
    post: Mapped[Optional["Post"]] = db.relationship(
        "Post", back_populates="report"
    )  # type: ignore
    reporter: Mapped[int] = db.Column(
        db.Integer,
        # TODO: This will fail if the user is deleted
        db.ForeignKey("users.id", onupdate="CASCADE", ondelete="SET NULL"),
        nullable=False,
    )
    report_reason: Mapped[str] = db.Column(db.String(120), nullable=False)
    date: Mapped[Optional[DateTime]] = db.Column(db.DateTime)
    dismissed: Mapped[bool] = db.Column(db.Boolean, nullable=False, default=False)
    closed: Mapped[bool] = db.Column(db.Boolean, nullable=False, default=False)
    # Column properties
    user_name = column_property(
        select(User.display_name).where(User.id == user_id).scalar_subquery()
    )
    post_text = column_property(
        select(Post.text).where(Post.id == post_id).scalar_subquery()
    )

    # Format method
    # Responsible for returning a JSON object
    def format(self):
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

        # If the report was for a user
        if self.type.lower() == "user":
            return_report["displayName"] = self.user_name
        # If the report was for a post
        else:
            return_report["postID"] = self.post_id
            return_report["text"] = self.post_text

        return return_report


# Notification Model
class Notification(db.Model):  # type: ignore[name-defined]
    __tablename__ = "notifications"
    id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    for_id: Mapped[int] = db.Column(
        db.Integer,
        db.ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    from_id: Mapped[int] = db.Column(
        db.Integer,
        # TODO: This will fail if the user is deleted
        db.ForeignKey("users.id", onupdate="CASCADE", ondelete="SET NULL"),
        nullable=False,
    )
    type: Mapped[str] = db.Column(db.String(), nullable=False)
    text: Mapped[str] = db.Column(db.String(), nullable=False)
    date: Mapped[DateTime] = db.Column(db.DateTime, nullable=False)
    # Column properties
    from_name = column_property(
        select(User.display_name).where(User.id == from_id).scalar_subquery()
    )
    for_name = column_property(
        select(User.display_name).where(User.id == for_id).scalar_subquery()
    )

    # Format method
    def format(self):
        return {
            "id": self.id,
            "fromId": self.from_id,
            "from": self.from_name,
            "forId": self.for_id,
            "for": self.for_name,
            "type": self.type,
            "text": self.text,
            "date": self.date,
        }


# Notification Subscription Model
class NotificationSub(db.Model):  # type: ignore[name-defined]
    __tablename__ = "subscriptions"
    id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    user: Mapped[int] = db.Column(
        db.Integer,
        db.ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    endpoint: Mapped[str] = db.Column(db.String(), nullable=False)
    subscription_data: Mapped[Text] = db.Column(db.Text, nullable=False)

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
    id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    filter: Mapped[str] = db.Column(db.String(), nullable=False)

    # Format method
    def format(self):
        return {"id": self.id, "filter": self.filter}


class Permission(db.Model):
    __tablename__ = "permissions"
    id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    permission: Mapped[str] = db.Column(db.String(), nullable=False)
    description: Mapped[Optional[str]] = db.Column(db.String())

    # Format method
    def format(self):
        return {
            "id": self.id,
            "permission": self.permission,
            "description": self.description,
        }


class Role(db.Model):
    __tablename__ = "roles"
    id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    name: Mapped[str] = db.Column(db.String(), nullable=False)
    permissions: Mapped[List[Permission]] = db.relationship(
        "Permission", secondary=roles_permissions_map
    )  # type: ignore

    # Format method
    def format(self):
        return {
            "id": self.id,
            "name": self.name,
            "permissions": [perm.format() for perm in self.permissions],
        }
