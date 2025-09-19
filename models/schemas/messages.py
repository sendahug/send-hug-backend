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

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    and_,
    case,
    false,
    func,
    or_,
    select,
    true,
)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, column_property, foreign, mapped_column, relationship

from models.common import BaseModel, DumpedModel
from models.schemas.enums import UserIconCharacter
from models.schemas.users import User, UserIconColour


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
        "User",
        back_populates="sent_messages",
        foreign_keys="Message.from_id",
    )
    from_user_colours: Mapped[list[UserIconColour]] = relationship(
        "UserIconColour",
        lazy="selectin",
        primaryjoin=foreign(UserIconColour.user_id) == from_id,
        viewonly=True,
    )
    for_id: Mapped[int] = mapped_column(
        Integer,
        # TODO: This will fail if the user is deleted
        ForeignKey("users.id", onupdate="CASCADE", ondelete="SET NULL"),
        nullable=False,
    )
    for_user: Mapped["User"] = relationship(
        "User",
        back_populates="received_messages",
        foreign_keys="Message.for_id",
    )
    for_user_colours: Mapped[list[UserIconColour]] = relationship(
        "UserIconColour",
        lazy="selectin",
        primaryjoin=foreign(UserIconColour.user_id) == for_id,
        viewonly=True,
    )
    text: Mapped[str] = mapped_column(String(480), nullable=False)
    date: Mapped[datetime | None] = mapped_column(DateTime)
    thread: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("threads.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    thread_details: Mapped["Thread"] = relationship("Thread", back_populates="messages")
    from_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    for_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    from_archived: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    for_archived: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # mapped_column Properties
    from_name: Mapped[str] = column_property(
        select(User.display_name).where(User.id == from_id).scalar_subquery()
    )
    from_icon: Mapped[UserIconCharacter] = column_property(
        select(User.selected_character).where(User.id == from_id).scalar_subquery()
    )
    for_name: Mapped[str] = column_property(
        select(User.display_name).where(User.id == for_id).scalar_subquery()
    )
    for_icon: Mapped[UserIconCharacter] = column_property(
        select(User.selected_character).where(User.id == for_id).scalar_subquery()
    )

    # Format method
    # Responsible for returning a JSON object
    def format(self, **kwargs) -> DumpedModel:
        from_icon_colours = {
            item.icon_part.value: item.colour for item in self.from_user_colours
        }
        for_icon_colours = {
            item.icon_part.value: item.colour for item in self.for_user_colours
        }

        return {
            "id": self.id,
            "fromId": self.from_id,
            "from": {
                "displayName": self.from_name,
                "selectedIcon": self.from_icon.value,
                "iconColours": from_icon_colours,
            },
            "forId": self.for_id,
            "for": {
                "displayName": self.for_name,
                "selectedIcon": self.for_icon.value,
                "iconColours": for_icon_colours,
            },
            "messageText": self.text,
            "date": self.date,
            "threadID": self.thread,
        }


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
    user1_colours: Mapped[list[UserIconColour]] = relationship(
        "UserIconColour",
        lazy="selectin",
        primaryjoin=foreign(UserIconColour.user_id) == user_1_id,
        viewonly=True,
    )
    user_2_id: Mapped[int] = mapped_column(
        Integer,
        # TODO: This will fail if the user is deleted
        ForeignKey("users.id", onupdate="CASCADE", ondelete="SET NULL"),
        nullable=False,
    )
    user_2: Mapped["User"] = relationship("User", foreign_keys="Thread.user_2_id")
    user2_colours: Mapped[list[UserIconColour]] = relationship(
        "UserIconColour",
        lazy="selectin",
        primaryjoin=foreign(UserIconColour.user_id) == user_2_id,
        viewonly=True,
    )
    messages: Mapped[list["Message"]] = relationship(
        "Message", back_populates="thread_details"
    )
    # Column properties
    latest_message_date: Mapped[datetime] = column_property(
        select(func.max(Message.date))
        .where(Message.thread == id)
        .group_by(Message.thread)
        .scalar_subquery()
    )
    user1_name: Mapped[str] = column_property(
        select(User.display_name).where(User.id == user_1_id).scalar_subquery()
    )
    user1_icon: Mapped[UserIconCharacter] = column_property(
        select(User.selected_character).where(User.id == user_1_id).scalar_subquery()
    )
    user1_total_message_count = column_property(
        select(func.count(Message.id))
        .where(
            and_(
                Message.thread == id,
                or_(Message.for_id == user_1_id, Message.from_id == user_1_id),
            )
        )
        .group_by(Message.thread)
        .scalar_subquery()
    )
    user1_message_count = column_property(
        select(func.count(Message.id))
        .where(
            and_(
                Message.thread == id,
                or_(
                    and_(
                        Message.for_id == user_1_id,
                        Message.for_deleted == false(),
                        Message.for_archived == false(),
                    ),
                    and_(
                        Message.from_id == user_1_id,
                        Message.from_deleted == false(),
                        Message.from_archived == false(),
                    ),
                ),
            )
        )
        .group_by(Message.thread)
        .scalar_subquery()
    )
    user1_deleted_message_count = column_property(
        select(func.count(Message.id))
        .where(
            and_(
                Message.thread == id,
                or_(
                    and_(Message.for_id == user_1_id, Message.for_deleted == true()),
                    and_(Message.from_id == user_1_id, Message.from_deleted == true()),
                ),
            )
        )
        .group_by(Message.thread)
        .scalar_subquery()
    )
    user1_archived_message_count = column_property(
        select(func.count(Message.id))
        .where(
            and_(
                Message.thread == id,
                or_(
                    and_(Message.for_id == user_1_id, Message.for_archived == true()),
                    and_(Message.from_id == user_1_id, Message.from_archived == true()),
                ),
            )
        )
        .group_by(Message.thread)
        .scalar_subquery()
    )

    user2_name: Mapped[str] = column_property(
        select(User.display_name).where(User.id == user_2_id).scalar_subquery()
    )
    user2_icon: Mapped[UserIconCharacter] = column_property(
        select(User.selected_character).where(User.id == user_2_id).scalar_subquery()
    )
    user2_total_message_count = column_property(
        select(func.count(Message.id))
        .where(
            and_(
                Message.thread == id,
                or_(Message.for_id == user_2_id, Message.from_id == user_2_id),
            )
        )
        .group_by(Message.thread)
        .scalar_subquery()
    )
    user2_message_count = column_property(
        select(func.count(Message.id))
        .where(
            and_(
                Message.thread == id,
                or_(
                    and_(
                        Message.for_id == user_2_id,
                        Message.for_deleted == false(),
                        Message.for_archived == false(),
                    ),
                    and_(
                        Message.from_id == user_2_id,
                        Message.from_deleted == false(),
                        Message.from_archived == false(),
                    ),
                ),
            )
        )
        .group_by(Message.thread)
        .scalar_subquery()
    )
    user2_deleted_message_count: Mapped[int] = column_property(
        select(func.count(Message.id))
        .where(
            and_(
                Message.thread == id,
                or_(
                    and_(Message.for_id == user_2_id, Message.for_deleted == true()),
                    and_(Message.from_id == user_2_id, Message.from_deleted == true()),
                ),
            )
        )
        .group_by(Message.thread)
        .scalar_subquery()
    )
    user2_archived_message_count: Mapped[int] = column_property(
        select(func.count(Message.id))
        .where(
            and_(
                Message.thread == id,
                or_(
                    and_(Message.for_id == user_2_id, Message.for_archived == true()),
                    and_(Message.from_id == user_2_id, Message.from_archived == true()),
                ),
            )
        )
        .group_by(Message.thread)
        .scalar_subquery()
    )

    @hybrid_property
    def user1_deleted(self):
        return self.user1_deleted_message_count == self.user1_total_message_count

    @user1_deleted.inplace.expression
    @classmethod
    def _user1_deleted(cls):
        return case(
            (cls.user1_deleted_message_count == cls.user1_total_message_count, true()),
            else_=false(),
        )

    @hybrid_property
    def user1_archived(self):
        return self.user1_archived_message_count == self.user1_total_message_count

    @user1_archived.inplace.expression
    @classmethod
    def _user1_archived(cls):
        return case(
            (cls.user1_archived_message_count == cls.user1_total_message_count, true()),
            else_=false(),
        )

    @hybrid_property
    def user2_deleted(self):
        return self.user2_deleted_message_count == self.user2_total_message_count

    @user2_deleted.inplace.expression
    @classmethod
    def _user2_deleted(cls):
        return case(
            (cls.user2_deleted_message_count == cls.user2_total_message_count, true()),
            else_=false(),
        )

    @hybrid_property
    def user2_archived(self):
        return self.user2_archived_message_count == self.user2_total_message_count

    @user2_archived.inplace.expression
    @classmethod
    def _user2_archived(cls):
        return case(
            (cls.user2_archived_message_count == cls.user2_total_message_count, true()),
            else_=false(),
        )

    # Format method
    # Responsible for returning a JSON object
    def format(self, **kwargs) -> DumpedModel:
        current_user_id = kwargs["current_user_id"]

        user1_icon_colours = {
            item.icon_part.value: item.colour for item in self.user1_colours
        }
        user2_icon_colours = {
            item.icon_part.value: item.colour for item in self.user2_colours
        }

        return {
            "id": self.id,
            "user1": {
                "displayName": self.user1_name,
                "selectedIcon": self.user1_icon.value,
                "iconColours": user1_icon_colours,
                "archived": self.user1_archived,
            },
            "user1Id": self.user_1_id,
            "user2": {
                "displayName": self.user2_name,
                "selectedIcon": self.user2_icon.value,
                "iconColours": user2_icon_colours,
                "archived": self.user2_archived,
            },
            "user2Id": self.user_2_id,
            "numMessages": (
                self.user1_message_count
                if current_user_id == self.user_1_id
                else self.user2_message_count
            ),
            "numArchivedMessages": (
                self.user1_archived_message_count
                if current_user_id == self.user_1_id
                else self.user2_archived_message_count
            ),
            "latestMessage": self.latest_message_date,
        }
