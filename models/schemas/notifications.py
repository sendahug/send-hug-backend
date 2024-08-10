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

from models.base_models import BaseModel, DumpedModel
from models.schemas.users import User


from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, select
from sqlalchemy.orm import Mapped, column_property, mapped_column


from datetime import datetime


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
    # Column properties
    from_name = column_property(
        select(User.display_name).where(User.id == from_id).scalar_subquery()
    )
    for_name = column_property(
        select(User.display_name).where(User.id == for_id).scalar_subquery()
    )

    # Format method
    def format(self, **kwargs) -> DumpedModel:
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
    def format(self, **kwargs) -> DumpedModel:
        return {
            "id": self.id,
            "user_id": self.user,
            "endpoint": self.endpoint,
            "subscription_data": self.subscription_data,
        }
