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
from sqlalchemy.orm import Mapped, column_property, mapped_column, relationship

from models.common import BaseModel, DumpedModel
from models.schemas.posts import Post

# Table objects for column_property
# -----------------------------------------------------------------
reports_user_table = table(
    "reports", column("id"), column("user_id"), column("closed")
).alias("reports_user")


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
    last_notifications_read: Mapped[datetime | None] = mapped_column(DateTime)
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
        return {
            "id": self.id,
            "displayName": self.display_name,
            "receivedH": self.received_hugs,
            "givenH": self.given_hugs,
            "loginCount": self.login_count,
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
            "blocked": self.blocked,
            "releaseDate": self.release_date,
            "autoRefresh": self.auto_refresh,
            "refreshRate": self.refresh_rate,
            "pushEnabled": self.push_enabled,
            "last_notifications_read": self.last_notifications_read,
            "selectedIcon": self.selected_character,
            "iconColours": (
                json.loads(self.icon_colours)
                if self.icon_colours
                else self.icon_colours
            ),
            "posts": self.post_count,
            "firebaseId": self.firebase_id,
        }
