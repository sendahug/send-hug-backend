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
import json
from typing import Any, List, Optional, TypeAlias, TypeVar

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import (
    Mapped,
    column_property,
    DeclarativeBase,
    mapped_column,
    relationship,
)
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
    select,
    Table,
)
from sqlalchemy.dialects.postgresql import ARRAY


class BaseModel(DeclarativeBase):
    pass


HugModelType = TypeVar("HugModelType", bound=BaseModel, covariant=True)
DumpedModel: TypeAlias = dict[str, Any]


# SQLAlchemy Tables
roles_permissions_map = Table(
    "roles_permissions_map",
    BaseModel.metadata,
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True),
    Column("permission_id", Integer, ForeignKey("permissions.id"), primary_key=True),
)


# Models
# -----------------------------------------------------------------
# Post Model
class Post(BaseModel):
    __tablename__ = "posts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", onupdate="CASCADE", ondelete="SET NULL"),
        nullable=False,
    )
    user: Mapped["User"] = relationship("User", back_populates="posts")
    text: Mapped[str] = mapped_column(String(480), nullable=False)
    date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    given_hugs: Mapped[Optional[int]] = mapped_column(Integer, default=0)
    open_report: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    sent_hugs: Mapped[Optional[List[int]]] = mapped_column(ARRAY(Integer))
    report: Mapped[Optional["Report"]] = relationship("Report", back_populates="post")

    @hybrid_property
    def user_name(self):
        return self.user.display_name

    # Format method
    # Responsible for returning a JSON object
    def format(self) -> DumpedModel:
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
class User(BaseModel):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    display_name: Mapped[str] = mapped_column(String(60), nullable=False)
    auth0_id: Mapped[str] = mapped_column(String(), nullable=False)
    received_hugs: Mapped[int] = mapped_column(Integer, default=0)
    given_hugs: Mapped[Optional[int]] = mapped_column(Integer, default=0)
    login_count: Mapped[Optional[int]] = mapped_column(Integer, default=1)
    role_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("roles.id", onupdate="CASCADE", ondelete="SET NULL"),
        default=4,
    )
    role: Mapped[Optional["Role"]] = relationship("Role", foreign_keys="User.role_id")
    blocked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    release_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    open_report: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    last_notifications_read: Mapped[Optional[datetime]] = mapped_column(DateTime)
    auto_refresh: Mapped[Optional[bool]] = mapped_column(Boolean, default=True)
    refresh_rate: Mapped[Optional[int]] = mapped_column(Integer, default=20)
    push_enabled: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    selected_character: Mapped[Optional[str]] = mapped_column(
        String(6), default="kitty"
    )
    icon_colours: Mapped[Optional[str]] = mapped_column(
        String(),
        default='{"character":"#BA9F93", "lbg":"#e2a275",'
        '"rbg":"#f8eee4", "item":"#f4b56a"}',
    )
    posts: Mapped[Optional[List["Post"]]] = relationship("Post", back_populates="user")
    sent_messages: Mapped[Optional[List["Message"]]] = relationship(
        "Message", back_populates="from_user", foreign_keys="Message.from_id"
    )
    received_messages: Mapped[Optional[List["Message"]]] = relationship(
        "Message", back_populates="for_user", foreign_keys="Message.for_id"
    )
    # mapped_column properties
    post_count = column_property(
        select(func.count(Post.id)).where(Post.user_id == id).scalar_subquery()
    )

    # Format method
    # Responsible for returning a JSON object
    def format(self) -> DumpedModel:
        return {
            "id": self.id,
            "auth0Id": self.auth0_id,
            "displayName": self.display_name,
            "receivedH": self.received_hugs,
            "givenH": self.given_hugs,
            "loginCount": self.login_count,
            "role": {
                "id": self.role.id,
                "name": self.role.name,
                "permissions": [
                    permission.permission for permission in self.role.permissions
                ],
            }
            if self.role
            else None,
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
class Message(BaseModel):
    __tablename__ = "messages"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    from_id: Mapped[int] = mapped_column(
        Integer,
        # TODO: This will fail if the user is deleted
        ForeignKey("users.id", onupdate="CASCADE", ondelete="SET NULL"),
        nullable=False,
    )
    from_user: Mapped["User"] = relationship(
        "User", back_populates="sent_messages", foreign_keys="Message.from_id"
    )
    for_id: Mapped[int] = mapped_column(
        Integer,
        # TODO: This will fail if the user is deleted
        ForeignKey("users.id", onupdate="CASCADE", ondelete="SET NULL"),
        nullable=False,
    )
    for_user: Mapped["User"] = relationship(
        "User", back_populates="received_messages", foreign_keys="Message.for_id"
    )
    text: Mapped[str] = mapped_column(String(480), nullable=False)
    date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    thread: Mapped[int] = mapped_column(
        Integer,
        # TODO: This will fail if the thread is deleted
        ForeignKey("threads.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    thread_details: Mapped["Thread"] = relationship("Thread", back_populates="messages")
    from_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    for_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    # mapped_column Properties
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
    def format(self) -> DumpedModel:
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


# Thread BaseModel
class Thread(BaseModel):
    __tablename__ = "threads"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_1_id: Mapped[int] = mapped_column(
        Integer,
        # TODO: This will fail if the user is deleted
        ForeignKey("users.id", onupdate="CASCADE", ondelete="SET NULL"),
        nullable=False,
    )
    user_1: Mapped["User"] = relationship("User", foreign_keys="Thread.user_1_id")
    user_2_id: Mapped[int] = mapped_column(
        Integer,
        # TODO: This will fail if the user is deleted
        ForeignKey("users.id", onupdate="CASCADE", ondelete="SET NULL"),
        nullable=False,
    )
    user_2: Mapped["User"] = relationship("User", foreign_keys="Thread.user_2_id")
    user_1_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    user_2_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    messages: Mapped[List[Message]] = relationship(
        "Message", back_populates="thread_details"
    )
    # mapped_column properties
    message_count = column_property(
        select(func.count(Message.id))
        .where(Message.thread == id)
        .group_by(Message.thread)
        .scalar_subquery()
    )
    latest_message_date = column_property(
        select(func.max(Message.date))
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
    def format(self) -> DumpedModel:
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


# Report BaseModel
class Report(BaseModel):
    __tablename__ = "reports"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type: Mapped[str] = mapped_column(String(10), nullable=False)
    user_id: Mapped[int] = mapped_column(
        Integer,
        # TODO: This will fail if the user is deleted
        ForeignKey("users.id", onupdate="CASCADE", ondelete="SET NULL"),
        nullable=False,
    )
    user: Mapped["User"] = relationship("User", foreign_keys="Report.user_id")
    post_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("posts.id", onupdate="CASCADE", ondelete="SET NULL")
    )
    post: Mapped[Optional["Post"]] = relationship("Post", back_populates="report")
    reporter: Mapped[int] = mapped_column(
        Integer,
        # TODO: This will fail if the user is deleted
        ForeignKey("users.id", onupdate="CASCADE", ondelete="SET NULL"),
        nullable=False,
    )
    report_reason: Mapped[str] = mapped_column(String(120), nullable=False)
    date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    dismissed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    closed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    # mapped_column properties
    user_name = column_property(
        select(User.display_name).where(User.id == user_id).scalar_subquery()
    )
    post_text = column_property(
        select(Post.text).where(Post.id == post_id).scalar_subquery()
    )

    # Format method
    # Responsible for returning a JSON object
    def format(self) -> DumpedModel:
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


# Notification BaseModel
class Notification(BaseModel):
    __tablename__ = "notifications"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    for_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    from_id: Mapped[int] = mapped_column(
        Integer,
        # TODO: This will fail if the user is deleted
        ForeignKey("users.id", onupdate="CASCADE", ondelete="SET NULL"),
        nullable=False,
    )
    type: Mapped[str] = mapped_column(String(), nullable=False)
    text: Mapped[str] = mapped_column(String(), nullable=False)
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    # mapped_column properties
    from_name = column_property(
        select(User.display_name).where(User.id == from_id).scalar_subquery()
    )
    for_name = column_property(
        select(User.display_name).where(User.id == for_id).scalar_subquery()
    )

    # Format method
    def format(self) -> DumpedModel:
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


# Notification Subscription BaseModel
class NotificationSub(BaseModel):
    __tablename__ = "subscriptions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    endpoint: Mapped[str] = mapped_column(String(), nullable=False)
    subscription_data: Mapped[Text] = mapped_column(Text, nullable=False)

    # Format method
    def format(self) -> DumpedModel:
        return {
            "id": self.id,
            "user_id": self.user,
            "endpoint": self.endpoint,
            "subscription_data": self.subscription_data,
        }


# Filter
class Filter(BaseModel):
    __tablename__ = "filters"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    filter: Mapped[str] = mapped_column(String(), nullable=False)

    # Format method
    def format(self) -> DumpedModel:
        return {"id": self.id, "filter": self.filter}


class Permission(BaseModel):
    __tablename__ = "permissions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    permission: Mapped[str] = mapped_column(String(), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String())

    # Format method
    def format(self) -> DumpedModel:
        return {
            "id": self.id,
            "permission": self.permission,
            "description": self.description,
        }


class Role(BaseModel):
    __tablename__ = "roles"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(), nullable=False)
    permissions: Mapped[List[Permission]] = relationship(
        "Permission", secondary=roles_permissions_map
    )

    # Format method
    def format(self) -> DumpedModel:
        return {
            "id": self.id,
            "name": self.name,
            "permissions": [perm.format() for perm in self.permissions],
        }
