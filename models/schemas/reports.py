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

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, select
from sqlalchemy.orm import Mapped, column_property, mapped_column, relationship

from models.common import BaseModel, DumpedModel
from models.schemas.posts import Post
from models.schemas.users import User


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
    user: Mapped["User"] = relationship(
        "User", foreign_keys="Report.user_id", back_populates="reports"
    )
    post_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("posts.id", onupdate="CASCADE", ondelete="SET NULL")
    )
    post: Mapped[Post | None] = relationship("Post", back_populates="reports")
    reporter: Mapped[int] = mapped_column(
        Integer,
        # TODO: This will fail if the user is deleted
        ForeignKey("users.id", onupdate="CASCADE", ondelete="SET NULL"),
        nullable=False,
    )
    report_reason: Mapped[str] = mapped_column(String(120), nullable=False)
    date: Mapped[datetime | None] = mapped_column(DateTime)
    dismissed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    closed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    # Column properties
    user_name = column_property(
        select(User.display_name).where(User.id == user_id).scalar_subquery()
    )
    post_text = column_property(
        select(Post.text).where(Post.id == post_id).scalar_subquery()
    )

    # Format method
    # Responsible for returning a JSON object
    def format(self, **kwargs) -> DumpedModel:
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
