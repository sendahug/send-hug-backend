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

from typing import Any, TypedDict

from flask import abort
from sqlalchemy import Delete
from sqlalchemy.exc import DataError, IntegrityError

from .models import db


class DBReturnModel(TypedDict):
    success: bool
    resource: dict[str, Any]


class DBBulkModel(TypedDict):
    success: bool
    resource: list[dict[str, Any]]


class DBDeleteModel(TypedDict):
    success: bool
    deleted: int | str


# Database management methods
# -----------------------------------------------------------------
def add(obj: db.Model) -> DBReturnModel:  # type: ignore[name-defined]
    """
    Inserts a new record into the database.

    param obj: Object to insert (User, Post or Message).
    """
    return_object = {}

    # Try to add the object to the database
    try:
        db.session.add(obj)
        db.session.commit()
        return_object = obj.format()
    # If there's a database error
    except (DataError, IntegrityError) as err:
        db.session.rollback()
        abort(422, str(err.orig))
    # If there's an error, rollback
    except Exception as err:
        db.session.rollback()
        abort(500, str(err))
    # Close the connection once the attempt is complete
    finally:
        db.session.close()

    return {"success": True, "resource": return_object}


def update(obj: db.Model) -> DBReturnModel:  # type: ignore[name-defined]
    """
    Updates an existing record.

    param obj: Updated object (User, Post or Message).
    """
    updated_object = {}

    # Try to update the object in the database
    try:
        db.session.commit()
        updated_object = obj.format()
    # If there's a database error
    except (DataError, IntegrityError) as err:
        db.session.rollback()
        abort(422, str(err.orig))
    # If there's an error, rollback
    except Exception as err:
        db.session.rollback()
        abort(500, str(err))
    # Close the connection once the attempt is complete
    finally:
        db.session.close()

    return {"success": True, "resource": updated_object}


def update_multiple(
    objs: list[db.Model] = [],  # type: ignore[name-defined]
) -> DBBulkModel:
    """
    Updates multiple records.

    param objs: A list with all objects to update.
    """
    updated_objects = []

    # Try to update the object in the database
    try:
        db.session.commit()

        for obj in objs:
            updated_objects.append(obj.format())
    # If there's a database error
    except (DataError, IntegrityError) as err:
        db.session.rollback()
        abort(422, str(err.orig))
    # If there's an error, rollback
    except Exception as err:
        db.session.rollback()
        abort(500, str(err))
    # Close the connection once the attempt is complete
    finally:
        db.session.close()

    return {"success": True, "resource": updated_objects}


def add_or_update_multiple(
    add_objs: list[db.Model] = [],  # type: ignore[name-defined]
    update_objs: list[db.Model] = [],  # type: ignore[name-defined]
) -> DBBulkModel:
    """
    Inserts or updates multiple records at once.

    param add_objs: Objects to add to the database.
    param update_objs: Objects to update in the database.
    """
    updated_or_added_objects = []

    # Try to update the object in the database
    try:
        db.session.add_all(add_objs)
        db.session.commit()

        for obj in update_objs:
            updated_or_added_objects.append(obj.format())

        for obj in add_objs:
            updated_or_added_objects.append(obj.format())
    # If there's a database error
    except (DataError, IntegrityError) as err:
        db.session.rollback()
        abort(422, str(err.orig))
    # If there's an error, rollback
    except Exception as err:
        db.session.rollback()
        abort(500, str(err))
    # Close the connection once the attempt is complete
    finally:
        db.session.close()

    return {"success": True, "resource": updated_or_added_objects}


def delete_object(obj: db.Model) -> DBDeleteModel:  # type: ignore[name-defined]
    """
    Deletes an existing record.

    param obj: Object (User, Post or Message) to delete.
    """
    # Try to delete the record from the database
    try:
        db.session.delete(obj)
        db.session.commit()
        deleted: int = obj.id
    # If there's a database error
    except (DataError, IntegrityError) as err:
        db.session.rollback()
        abort(422, str(err.orig))
    # If there's an error, rollback
    except Exception as err:
        db.session.rollback()
        abort(500, str(err))
    # Close the connection once the attempt is complete
    finally:
        db.session.close()

    return {"success": True, "deleted": deleted}


def bulk_delete_and_update(
    delete_stmts: list[Delete],
    to_update: list[db.Model] = [],  # type: ignore[name-defined]
) -> DBBulkModel:
    """
    Run multiple delete statements and possible updates within the same
    session.

    param delete_stmts: Delete statements to run.
    param to_update: Objects to update in the database.
    """
    updated_objects = []

    # Try to delete the records
    try:
        for delete_stmt in delete_stmts:
            db.session.execute(delete_stmt)

        db.session.commit()

        for obj in to_update:
            updated_objects.append(obj.format())
    # If there's a database error
    except (DataError, IntegrityError) as err:
        db.session.rollback()
        abort(422, str(err.orig))
    # If there's an error, rollback
    except Exception as err:
        db.session.rollback()
        abort(500, str(err))
    # Close the connection once the attempt is complete
    finally:
        db.session.close()

    return {"success": True, "resource": updated_objects}
