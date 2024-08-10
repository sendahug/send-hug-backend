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
from typing import TYPE_CHECKING, List

from models.base_models import BaseModel, DumpedModel

if TYPE_CHECKING:
    from .reports import Report
    from .users import User
else:
    Report = "Report"
    User = "User"

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    and_,
    case,
    column,
    false,
    func,
    select,
    table,
    true,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, column_property, mapped_column, relationship


from datetime import datetime

# Table objects for column_property
# -----------------------------------------------------------------
reports_post_table = table(
    "reports", column("id"), column("post_id"), column("closed")
).alias("reports_post")


class Post(BaseModel):
    __tablename__ = "posts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        # TODO: This will break if a user is deleted
        ForeignKey("users.id", onupdate="CASCADE", ondelete="SET NULL"),
        nullable=False,
    )
    user: Mapped["User"] = relationship("User", back_populates="posts", lazy="selectin")
    text: Mapped[str] = mapped_column(String(480), nullable=False)
    date: Mapped[datetime | None] = mapped_column(DateTime)
    given_hugs: Mapped[int] = mapped_column(Integer, default=0)
    sent_hugs: Mapped[List[int] | None] = mapped_column(ARRAY(Integer))
    reports: Mapped[List["Report"] | None] = relationship(
        "Report",
        back_populates="post",
    )
    # Column properties
    open_reports_count = column_property(
        select(func.count(reports_post_table.table_valued()))
        .where(
            and_(
                reports_post_table.c.post_id == id,
                reports_post_table.c.closed == false(),
            )
        )
        .scalar_subquery()
    )

    @hybrid_property
    def user_name(self):
        return self.user.display_name

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
            "userId": self.user_id,
            "user": self.user_name,
            "text": self.text,
            "date": self.date,
            "givenHugs": self.given_hugs,
            "sentHugs": list(filter(None, self.sent_hugs)) if self.sent_hugs else [],
        }
