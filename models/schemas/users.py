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

from typing import TYPE_CHECKING

from models.schemas.roles import Role

if TYPE_CHECKING:
    from .messages import Message
else:
    Message = "Message"

from datetime import datetime
import json

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    and_,
    case,
    column,
    false,
    func,
    select,
    table,
    true,
)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, column_property, foreign, mapped_column, relationship

from models.common import BaseModel, DumpedModel
from models.schemas.enums import UserIconCharacter, UserIconPart
from models.schemas.posts import Post

# Table objects for column_property
# -----------------------------------------------------------------
reports_user_table = table(
    "reports", column("id"), column("user_id"), column("closed")
).alias("reports_user")


class UserIconColour(BaseModel):
    __tablename__ = "users_icon_colours"
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
        autoincrement=False,
    )
    icon_part: Mapped[UserIconPart] = mapped_column(
        Enum(UserIconPart), primary_key=True
    )
    colour: Mapped[str] = mapped_column(String(7), nullable=False)


class UserPreference(BaseModel):
    __tablename__ = "user_preferences"
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
        autoincrement=False,
    )
    selected_character: Mapped[UserIconCharacter] = mapped_column(
        Enum(UserIconCharacter), default="kitty"
    )
    user_icon_colours: Mapped[list[UserIconColour]] = relationship(
        "UserIconColour",
        lazy="selectin",
        primaryjoin=foreign(UserIconColour.user_id) == user_id,
    )
    auto_refresh_enabled: Mapped[bool | None] = mapped_column(Boolean, default=True)
    refresh_rate: Mapped[int | None] = mapped_column(Integer, default=20)
    push_enabled: Mapped[bool | None] = mapped_column(Boolean, default=False)
    email_notifications_enabled: Mapped[bool | None] = mapped_column(
        Boolean, default=False
    )
    message_notifications: Mapped[bool | None] = mapped_column(Boolean, default=False)
    hugs_digest_notifications: Mapped[bool | None] = mapped_column(
        Boolean, default=False
    )
    you_okay_notifications: Mapped[bool | None] = mapped_column(Boolean, default=False)
    previous_interaction_notifications: Mapped[bool | None] = mapped_column(
        Boolean, default=False
    )
    last_updated_at: Mapped[datetime] = mapped_column(DateTime)


class User(BaseModel):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    display_name: Mapped[str] = mapped_column(String(60), nullable=False)
    received_hugs: Mapped[int] = mapped_column(Integer, default=0)
    given_hugs: Mapped[int] = mapped_column(Integer, default=0)
    login_count: Mapped[int | None] = mapped_column(Integer, default=1)
    role_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("roles.id", onupdate="CASCADE", ondelete="SET NULL"),
        default=4,
    )
    role: Mapped[Role | None] = relationship(
        "Role", foreign_keys="User.role_id", lazy="selectin"
    )
    release_date: Mapped[datetime | None] = mapped_column(DateTime)
    auto_refresh: Mapped[bool | None] = mapped_column(Boolean, default=True)
    refresh_rate: Mapped[int | None] = mapped_column(Integer, default=20)
    push_enabled: Mapped[bool | None] = mapped_column(Boolean, default=False)
    selected_character: Mapped[str | None] = mapped_column(String(6), default="kitty")
    icon_colours: Mapped[str | None] = mapped_column(
        String(),
        default='{"character":"#BA9F93", "lbg":"#e2a275",'
        '"rbg":"#f8eee4", "item":"#f4b56a"}',
    )
    posts: Mapped[list["Post"] | None] = relationship("Post", back_populates="user")
    sent_messages: Mapped[list["Message"] | None] = relationship(
        "Message", back_populates="from_user", foreign_keys="Message.from_id"
    )
    received_messages: Mapped[list["Message"] | None] = relationship(
        "Message", back_populates="for_user", foreign_keys="Message.for_id"
    )
    firebase_id: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    firebase_id_uq = UniqueConstraint("firebase_id", name="firebase_id_uq")
    email_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    email: Mapped[str] = mapped_column(String(75), nullable=False)
    gender: Mapped[str | None] = mapped_column(String(10))
    platform_usage_reason: Mapped[str | None] = mapped_column(String(25))
    user_preferences: Mapped[UserPreference | None] = relationship(
        "UserPreference", lazy="selectin"
    )
    reports = relationship(
        "Report", back_populates="user", foreign_keys="Report.user_id"
    )
    # Column properties
    post_count = column_property(
        select(func.count(Post.id)).where(Post.user_id == id).scalar_subquery()
    )
    open_reports_count = column_property(
        select(func.count(reports_user_table.table_valued()))
        .where(
            and_(
                reports_user_table.c.user_id == id,
                reports_user_table.c.closed == false(),
            )
        )
        .scalar_subquery()
    )
    blocked = column_property(role_id == 5)

    @hybrid_property
    def open_report(self):
        if self.open_reports_count == 0:
            return False

        return True

    @open_report.inplace.expression
    @classmethod
    def _open_report(cls):
        return case((cls.open_reports_count == 0, false()), else_=true())

    # Format method
    # Responsible for returning a JSON object
    def format(self, **kwargs) -> DumpedModel:
        current_user = kwargs.get("current_user")

        base_user_details = {
            "id": self.id,
            "displayName": self.display_name,
            "receivedH": self.received_hugs,
            "givenH": self.given_hugs,
            # Temp; For compatibility with admin views
            "blocked": self.blocked,
            # Temp; For compatibility with admin views
            "releaseDate": self.release_date,
            "selectedIcon": self.selected_character,
            "iconColours": (
                json.loads(self.icon_colours)
                if self.icon_colours
                else self.icon_colours
            ),
            "posts": self.post_count,
            "role": (
                {
                    "id": self.role.id,
                    "name": self.role.name,
                    "permissions": [
                        permission.permission for permission in self.role.permissions
                    ],
                }
                if self.role
                else None
            ),
        }

        if current_user != self.id:
            return base_user_details

        email_notifications_enabled: bool | None = None
        message_notifications: bool | None = None
        hugs_digest_notifications: bool | None = None
        you_okay_notifications: bool | None = None
        previous_interaction_notifications: bool | None = None

        if self.user_preferences:
            email_notifications_enabled = (
                self.user_preferences.email_notifications_enabled
            )
            message_notifications = self.user_preferences.message_notifications
            hugs_digest_notifications = self.user_preferences.hugs_digest_notifications
            you_okay_notifications = self.user_preferences.you_okay_notifications
            previous_interaction_notifications = (
                self.user_preferences.previous_interaction_notifications
            )

        return {
            **base_user_details,
            "loginCount": self.login_count,
            "autoRefresh": self.auto_refresh,
            "refreshRate": self.refresh_rate,
            "pushEnabled": self.push_enabled,
            "firebaseId": self.firebase_id,
            "emailVerified": self.email_verified,
            "email": self.email,
            "gender": self.gender,
            "platformUsageReason": self.platform_usage_reason,
            "preferences": {
                "emailNotificationsEnabled": email_notifications_enabled,
                "messageNotifications": message_notifications,
                "hugsDigestNotifications": hugs_digest_notifications,
                "youOkayNotifications": you_okay_notifications,
                "previousInteractionNotifications": previous_interaction_notifications,
            },
        }
