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

from models.schemas.threads import Thread
from models.base_models import BaseModel, DumpedModel
from models.schemas.users import User


from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, select
from sqlalchemy.orm import Mapped, column_property, mapped_column, relationship


import json
from datetime import datetime


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
    date: Mapped[datetime | None] = mapped_column(DateTime)
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
    def format(self, **kwargs) -> DumpedModel:
        return {
            "id": self.id,
            "fromId": self.from_id,
            "from": {
                "displayName": self.from_name,
                "selectedIcon": self.from_icon,
                "iconColours": (
                    json.loads(self.from_colours)
                    if self.from_colours
                    else self.from_colours
                ),
            },
            "forId": self.for_id,
            "for": {
                "displayName": self.for_name,
                "selectedIcon": self.for_icon,
                "iconColours": (
                    json.loads(self.for_colours)
                    if self.for_colours
                    else self.for_colours
                ),
            },
            "messageText": self.text,
            "date": self.date,
            "threadID": self.thread,
        }
