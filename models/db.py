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

from asyncio import current_task
import logging
import math
from typing import Sequence, Type, TypeVar, cast, overload

from quart import Quart, abort
from sqlalchemy import URL, Delete, NullPool, Select, Update, func, select
from sqlalchemy.exc import DataError, IntegrityError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)
from werkzeug.exceptions import HTTPException

from .common import BaseModel, CoreSAHModel, DumpedModel, PaginationResult

T = TypeVar("T", bound=BaseModel)
LOGGER = logging.getLogger("SendAHug")


class SendADatabase:
    """
    The main database handler for running all CRUD operations against
    SQLAlchemy (as well as manage engines and sessions).

    Named this way primarily for amusement. The design is loosely based
    on Flask-SQLAlchemy's `SQLAlchemy` class.
    """

    database_url: URL
    engine: AsyncEngine
    session_factory: async_sessionmaker[AsyncSession]

    def __init__(
        self,
        database_url: URL,
        default_per_page: int = 5,
    ):
        """
        Initialises the class.

        param default_per_page: A default per_page value for the pagination method.
        param db_url: The URL of the database.
        """
        # Temporary second variable
        self.database_url = database_url
        self.default_per_page = default_per_page
        # we set poolclass to make tests work, otherwise we get:
        # sqlalchemy.exc.InterfaceError: cannot perform operation: another operation is
        # in progress
        # it's a hack fix from https://github.com/MagicStack/asyncpg/issues/863 so
        # really should be fixed proprely at some point
        self.engine = create_async_engine(
            self.database_url, poolclass=NullPool, echo=True
        )
        self._create_session_factory()
        self.session = self.create_session()

    def init_app(self, app: Quart) -> None:
        """
        Initialises the connection with the Quart App (Flask-SQLAlchemy style).

        param db_url: The URL of the database.
        param app: The Quart app to connect to.
        """
        app.config["SQLALCHEMY_DATABASE_URI"] = self.database_url
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        self.app = app
        self.app.teardown_appcontext(self._remove_session)

    def _create_session_factory(self):
        """
        Creates the async session factory to be used to generate scoped sessions.
        """
        session_factory = async_sessionmaker(self.engine, expire_on_commit=False)
        self.session_factory = session_factory

    # TODO: Do we want to continue with this pattern? According to
    # https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html#using-asyncio-scoped-session
    # it's not really recommended anymore.
    def create_session(self):
        """
        Creates a new async scoped session.
        """
        return async_scoped_session(
            session_factory=self.session_factory, scopefunc=current_task
        )

    async def _remove_session(self, exception: BaseException | None):
        """ """
        await self.session.remove()

    def set_default_per_page(self, per_page: int):
        """
        Updates the default 'per page' value.
        """
        self.default_per_page = per_page

    # READ
    # -----------------------------------------------------------------
    async def paginate(
        self,
        query: Select,  # TODO: This select needs to be Select[tuple[CoreSAHModel]]
        current_page: int,
        per_page: int | None = None,
        **kwargs,
    ) -> PaginationResult:
        """
        Return a paginated result from a query. This includes the items in the given
        page, the total number of pages and the total number of items.

        param query: The base query to execute.
        param current_page: The current page to fetch the items for.
        param per_page: The amount of items to include in each page.
        """
        LOGGER.debug(f"Fetching items for page {current_page}")

        if per_page is None:
            per_page = self.default_per_page

        try:
            items_scalars = await self.session.scalars(
                query.limit(per_page).offset((current_page - 1) * per_page)
            )
            items = items_scalars.all()
            total_items = (
                await self.session.scalar(select(func.count()).select_from(query.cte()))
                or 0
            )

            return PaginationResult(
                resource=[item.format(**kwargs) for item in list(items)],
                current_page=current_page,
                per_page=per_page,
                total_items=total_items,
                total_pages=math.ceil(total_items / per_page),
            )

        except Exception as err:
            LOGGER.error(str(err))
            abort(500, str(err))

    async def one_or_404(self, item_id: int, item_type: Type[T]) -> T:
        """
        Fetch a single item or return 404 if it doesn't exist. Inspired by
        Flask-SQLAlchemy 3's `get_or_404` method.
        """
        LOGGER.debug(f"Fetching item {item_id}")
        try:
            item = await self.session.get(item_type, item_id)

            if item is None:
                abort(404)

            return item

        except HTTPException as exc:
            LOGGER.error(str(exc))
            raise exc

        except Exception as err:
            LOGGER.error(str(err))
            abort(422, str(err))

    # CREATE
    # -----------------------------------------------------------------
    async def add_object(self, obj: CoreSAHModel, **kwargs) -> DumpedModel:
        """
        Inserts a new record into the database.

        param obj: Object to insert.
        """
        # Try to add the object to the database
        try:
            self.session.add(obj)
            await self.session.commit()
            await self.session.refresh(obj)

            return obj.format(**kwargs)
        # If there's a database error
        except (DataError, IntegrityError) as err:
            await self.session.rollback()
            LOGGER.error(str(err))
            abort(422, str(err.orig))
        # If there's an error, rollback
        except Exception as err:
            await self.session.rollback()
            LOGGER.error(str(err))
            abort(500, str(err))

    # Bulk add
    async def add_multiple_objects(
        self,
        objects: list[CoreSAHModel],
        **kwargs,
    ) -> list[DumpedModel]:
        """
        Inserts multiple records into the database.

        param objects: The list of objects to add to the database.
        """
        formatted_objects: list[DumpedModel] = []

        # Try to add the objects to the database
        try:
            self.session.add_all(objects)
            await self.session.commit()

            for object in objects:
                await self.session.refresh(object)
                formatted_objects.append(object.format(**kwargs))

            return formatted_objects
        # If there's a database error
        except (DataError, IntegrityError) as err:
            await self.session.rollback()
            LOGGER.error(str(err))
            abort(422, str(err.orig))
        # If there's an error, rollback
        except Exception as err:
            await self.session.rollback()
            LOGGER.error(str(err))
            abort(500, str(err))

    # UPDATE
    # -----------------------------------------------------------------
    async def update_object(self, obj: CoreSAHModel, **kwargs) -> DumpedModel:
        """
        Updates an existing record.

        param obj: Updated object to commit.
        """
        # Try to update the object in the database
        try:
            await self.session.commit()
            await self.session.refresh(obj)

            return obj.format(**kwargs)
        # If there's a database error
        except (DataError, IntegrityError) as err:
            await self.session.rollback()
            LOGGER.error(str(err))
            abort(422, str(err.orig))
        # If there's an error, rollback
        except Exception as err:
            await self.session.rollback()
            LOGGER.error(str(err))
            abort(500, str(err))

    # Bulk Update
    async def update_multiple_objects(
        self,
        objects: Sequence[CoreSAHModel],
        **kwargs,
    ) -> list[DumpedModel]:
        """
        Updates multiple records.

        param objects: A list with all objects to update.
        """
        updated_objects = []

        # Try to update the objects in the database
        try:
            await self.session.commit()

            for obj in objects:
                await self.session.refresh(obj)
                updated_objects.append(obj.format(**kwargs))

            return updated_objects
        # If there's a database error
        except (DataError, IntegrityError) as err:
            await self.session.rollback()
            LOGGER.error(str(err))
            abort(422, str(err.orig))
        # If there's an error, rollback
        except Exception as err:
            await self.session.rollback()
            LOGGER.error(str(err))
            abort(500, str(err))

    @overload
    async def update_multiple_objects_with_dml(self, update_stmts: Update):
        ...

    @overload
    async def update_multiple_objects_with_dml(self, update_stmts: list[Update]):
        ...

    async def update_multiple_objects_with_dml(self, update_stmts):
        """
        Updates multiple objects with a single UPDATE statement.

        param update_stmt: The UPDATE statement to execute.
        """
        try:
            if isinstance(update_stmts, list):
                for stmt in cast(list[Update], update_stmts):
                    await self.session.execute(stmt)
            else:
                await self.session.execute(update_stmts)

            await self.session.commit()
        # If there's a database error
        except (DataError, IntegrityError) as err:
            await self.session.rollback()
            LOGGER.error(str(err))
            abort(422, str(err.orig))
        # If there's an error, rollback
        except Exception as err:
            await self.session.rollback()
            LOGGER.error(str(err))
            abort(500, str(err))

    # DELETE
    # -----------------------------------------------------------------
    async def delete_object(self, object: CoreSAHModel) -> int:
        """
        Deletes an existing record.

        param obj: Object to delete.
        """
        # Try to delete the record from the database
        try:
            await self.session.delete(object)
            await self.session.commit()
            return object.id
        # If there's a database error
        except (DataError, IntegrityError) as err:
            await self.session.rollback()
            LOGGER.error(str(err))
            abort(422, str(err.orig))
        # If there's an error, rollback
        except Exception as err:
            await self.session.rollback()
            LOGGER.error(str(err))
            abort(500, str(err))

    # Bulk delete
    # TODO: Return the number of deleted items
    async def delete_multiple_objects(self, delete_stmt: Delete):
        """
        Executes a delete statement to delete multiple objects.

        param delete_stmt: The DELETE statement to execute.
        """
        # Try to delete the objects from the database
        try:
            await self.session.execute(delete_stmt)
            await self.session.commit()
        # If there's a database error
        except (DataError, IntegrityError) as err:
            await self.session.rollback()
            LOGGER.error(str(err))
            abort(422, str(err.orig))
        # If there's an error, rollback
        except Exception as err:
            await self.session.rollback()
            LOGGER.error(str(err))
            abort(500, str(err))
