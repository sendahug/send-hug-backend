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

from dataclasses import dataclass
import math
from typing import Protocol, Sequence, Type, TypeVar
import os

from flask import Flask, abort
from sqlalchemy import Delete, Engine, create_engine, Select, func, select
from sqlalchemy.orm import sessionmaker, Session, scoped_session, Mapped
from sqlalchemy.exc import DataError, IntegrityError

from .models import BaseModel, HugModelType, DumpedModel


T = TypeVar("T", bound=BaseModel)


# Database configuration
database_path = os.environ.get("DATABASE_URL", "")


class CoreSAHModel(Protocol[HugModelType]):
    id: Mapped[int]

    def format(self) -> DumpedModel:
        ...


@dataclass
class PaginationResult:
    resource: list[DumpedModel]
    current_page: int
    per_page: int
    total_items: int
    total_pages: int


# TODO: Add number of deleted items
@dataclass
class BulkActionResult:
    added: list[DumpedModel]
    updated: list[DumpedModel]


class SendADatabase:
    """
    The main database handler for running all CRUD operations against
    SQLAlchemy (as well as manage engines and sessions).

    Named this way primarily for amusement.
    """

    engine: Engine
    session_factory: sessionmaker[Session]

    def __init__(
        self,
        default_per_page: int = 5,
        app: Flask | None = None,
        db_url: str | None = None,
    ):
        """
        Initialises the class.

        param default_per_page: A default per_page value for the pagination method.
        param app: The Flask app to connect to.
        param db_url: The URL of the database.
        """
        self.default_per_page = default_per_page

        if app is not None and db_url is not None:
            self.init_app(db_url=db_url, app=app)

    def init_app(self, db_url: str, app: Flask) -> None:
        """
        Initialises the connection w ith the Flask App (Flask-SQLAlchemy style).

        param db_url: The URL of the database.
        param app: The Flask app to connect to.
        """
        app.config["SQLALCHEMY_DATABASE_URI"] = db_url
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        self.app = app
        self.engine = create_engine(db_url)
        self._create_session_factory()
        self.session = self.create_scoped_session()
        self.app.teardown_appcontext(self._remove_session)

    def _create_session_factory(self):
        """
        Creates the session factory to be used to generate scoped sessions.
        """
        session_factory = sessionmaker(
            bind=self.engine,
            class_=Session,
        )
        self.session_factory = session_factory

    def create_scoped_session(self):
        """
        Creates a new scoped session.
        """
        return scoped_session(session_factory=self.session_factory)

    def _remove_session(self, exception: BaseException | None):
        """
        Removes the sesion once the app context is torn down.
        Copied from Flask-SQLAlchemy.
        """
        self.session.remove()

    # READ
    # -----------------------------------------------------------------
    def paginate(
        self,
        query: Select,  # TODO: This select needs to be Select[tuple[CoreSAHModel]]
        current_page: int,
        per_page: int | None = None,
    ) -> PaginationResult:
        """
        Return a paginated result from a query. This includes the items in the given
        page, the total number of pages and the total number of items.

        param query: The base query to execute.
        param current_page: The current page to fetch the items for.
        param per_page: The amount of items to include in each page.
        """
        session = self.create_scoped_session()

        if per_page is None:
            per_page = self.default_per_page

        with session() as sess:
            try:
                items = sess.scalars(
                    query.limit(per_page).offset((current_page - 1) * per_page)
                ).all()
                total_items = (
                    sess.scalar(select(func.count()).select_from(query.cte())) or 0
                )

                return PaginationResult(
                    resource=[item.format() for item in list(items)],
                    current_page=current_page,
                    per_page=per_page,
                    total_items=total_items,
                    total_pages=math.ceil(total_items / per_page),
                )

            except Exception as err:
                abort(422, str(err))

    def one_or_404(self, item_id: int, item_type: Type[T]) -> T:
        """
        Fetch a single item or return 404 if it doesn't exist. Inspired by
        Flask-SQLAlchemy 3's `get_or_404` method.
        """
        try:
            item = self.session.get(item_type, item_id)

            if item is None:
                abort(404)

            return item

        except Exception as err:
            abort(422, str(err))

    # CREATE
    # -----------------------------------------------------------------
    def add_object(self, obj: CoreSAHModel) -> CoreSAHModel:
        """
        Inserts a new record into the database.

        param obj: Object to insert.
        """
        # Try to add the object to the database
        try:
            self.session.add(obj)
            self.session.commit()

            return obj
        # If there's a database error
        except (DataError, IntegrityError) as err:
            self.session.rollback()
            abort(422, str(err.orig))
        # If there's an error, rollback
        except Exception as err:
            self.session.rollback()
            abort(500, str(err))

    # Bulk add
    def add_multiple_objects(self, objects: list[CoreSAHModel]) -> list[DumpedModel]:
        """
        Inserts multiple records into the database.

        param objects: The list of objects to add to the database.
        """
        # Try to add the objects to the database
        try:
            self.session.add_all(objects)
            self.session.commit()

            return [item.format() for item in objects]
        # If there's a database error
        except (DataError, IntegrityError) as err:
            self.session.rollback()
            abort(422, str(err.orig))
        # If there's an error, rollback
        except Exception as err:
            self.session.rollback()
            abort(500, str(err))

    # UPDATE
    # -----------------------------------------------------------------
    def update_object(self, obj: CoreSAHModel) -> CoreSAHModel:
        """
        Updates an existing record.

        param obj: Updated object to commit.
        """
        # Try to update the object in the database
        try:
            self.session.commit()
            self.session.refresh(obj)

            return obj
        # If there's a database error
        except (DataError, IntegrityError) as err:
            self.session.rollback()
            abort(422, str(err.orig))
        # If there's an error, rollback
        except Exception as err:
            self.session.rollback()
            abort(500, str(err))

    # Bulk Update
    def update_multiple_objects(
        self, objects: Sequence[CoreSAHModel]
    ) -> list[DumpedModel]:
        """
        Updates multiple records.

        param objects: A list with all objects to update.
        """
        updated_objects = []

        # Try to update the objects in the database
        try:
            self.session.commit()

            for obj in objects:
                self.session.refresh(obj)
                updated_objects.append(obj.format())

            return updated_objects
        # If there's a database error
        except (DataError, IntegrityError) as err:
            self.session.rollback()
            abort(422, str(err.orig))
        # If there's an error, rollback
        except Exception as err:
            self.session.rollback()
            abort(500, str(err))

    # DELETE
    # -----------------------------------------------------------------
    def delete_object(self, object: CoreSAHModel) -> int:
        """
        Deletes an existing record.

        param obj: Object to delete.
        """
        # Try to delete the record from the database
        try:
            self.session.delete(object)
            self.session.commit()
            return object.id
        # If there's a database error
        except (DataError, IntegrityError) as err:
            self.session.rollback()
            abort(422, str(err.orig))
        # If there's an error, rollback
        except Exception as err:
            self.session.rollback()
            abort(500, str(err))

    # Bulk delete
    # TODO: Return the number of deleted items
    def delete_multiple_objects(self, delete_stmt: Delete):
        """
        Executes a delete statement to delete multiple objects.

        param delete_stmt: The delete statement to execute.
        """
        # Try to delete the objects from the database
        try:
            self.session.execute(delete_stmt)
            self.session.commit()
        # If there's a database error
        except (DataError, IntegrityError) as err:
            self.session.rollback()
            abort(422, str(err.orig))
        # If there's an error, rollback
        except Exception as err:
            self.session.rollback()
            abort(500, str(err))

    # MIXED BULK ACTIONS
    # -----------------------------------------------------------------
    # TODO: We really shouldn't be doing it all at the same time.
    def make_bulk_updates(
        self,
        add_objects: list[CoreSAHModel],
        update_objects: list[CoreSAHModel],
        delete_stmts: list[Delete],
    ):
        """
        Runs the given list of bulk updates (create and/or edit and/or delete).

        param add_objects: Objects to add.
        param update_objects: Objects to update.
        param delete_stmts: Delete statements to execute to delete multiple items.
        """
        # Try to update the object in the database
        try:
            self.session.add_all(add_objects)

            for delete_stmt in delete_stmts:
                self.session.execute(delete_stmt)

            self.session.commit()

            return BulkActionResult(
                added=[item.format() for item in add_objects],
                updated=[item.format() for item in update_objects],
            )
        # If there's a database error
        except (DataError, IntegrityError) as err:
            self.session.rollback()
            abort(422, str(err.orig))
        # If there's an error, rollback
        except Exception as err:
            self.session.rollback()
            abort(500, str(err))


db = SendADatabase()
