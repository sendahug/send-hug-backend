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
import json
import os
from typing import Any, Literal, Sequence, cast

from quart import Quart, Response, abort, jsonify, request
from quart_cors import cors
from sqlalchemy import Text, and_, delete, desc, false, func, or_, select, true, update

from auth import AuthError, UserData, requires_auth
from config import sah_config
from controllers import routers
from controllers.common import DATETIME_PATTERN, validator

from models import (
    BLOCKED_USER_ROLE_ID,
    Filter,
    Message,
    Notification,
    NotificationSub,
    Post,
    Report,
    User,
)
from models.schemas.messages import Thread
from utils.push_notifications import RawPushData
from utils.validator import ValidationError


def create_app() -> Quart:
    # create and configure the app
    app = Quart("SendAHug")
    sah_config.db.init_app(app=app)
    sah_config.db.set_default_per_page(per_page=5)
    # Utilities
    cors(app)

    @app.after_request
    def after_request(response: Response):
        # CORS Setup
        response.headers.add(
            "Access-Control-Allow-Origin", str(os.environ.get("FRONTEND"))
        )
        response.headers.add(
            "Access-Control-Allow-Methods",
            "GET, POST, PATCH, DELETE, OPTIONS",
        )
        response.headers.add(
            "Access-Control-Allow-Headers",
            "Authorization, Content-Type",
        )
        # Security Headers, based on
        # https://owasp.org/www-project-secure-headers/index.html#div-bestpractices
        response.headers.add(
            "Strict-Transport-Security", "max-age=31536000; includeSubDomains"
        )
        response.headers.add("X-Frame-Options", "deny")
        response.headers.add("X-Content-Type-Options", "nosniff")
        response.headers.add(
            "Content-Security-Policy",
            (
                "default-src 'self'; form-action 'self'; object-src 'none'; "
                "frame-ancestors 'none'; upgrade-insecure-requests; "
                "block-all-mixed-content"
            ),
        )
        response.headers.add("X-Permitted-Cross-Domain-Policies", "none")
        response.headers.add("Referrer-Policy", "no-referrer")
        response.headers.add("Cross-Origin-Resource-Policy", "same-origin")
        response.headers.add("Cross-Origin-Embedder-Policy", "require-corp")
        response.headers.add("Cross-Origin-Opener-Policy", "same-origin")
        response.headers.add("Cache-Control", "no-store, max-age=0")
        response.headers.add("Pragma", "no-cache")  # HTTP 1.0

        return response

    for router in routers:
        app.register_blueprint(router)

    # Endpoint: GET /messages
    # Description: Gets the user's messages.
    # Parameters: None.
    # Authorization: read:messages.
    @app.route("/messages")
    @requires_auth(sah_config, ["read:messages"])
    async def get_user_messages(token_payload: UserData):
        page = request.args.get("page", 1, type=int)
        type = request.args.get("type", "inbox", type=str)
        thread_id = request.args.get("threadID", None, type=int)

        if type in ["inbox", "outbox", "thread"]:
            messages_query = select(Message)

            # For inbox, gets all incoming messages
            if type == "inbox":
                messages_query = messages_query.filter(
                    Message.for_deleted == false()
                ).filter(Message.for_id == token_payload["id"])
            # For outbox, gets all outgoing messages
            elif type == "outbox":
                messages_query = messages_query.filter(
                    Message.from_deleted == false()
                ).filter(Message.from_id == token_payload["id"])
            # Gets a specific thread's messages
            else:
                message = await sah_config.db.session.scalar(
                    select(Thread).filter(Thread.id == thread_id)
                )
                # Check if there's a thread with that ID at all
                if message:
                    # If the user is trying to view a thread that belongs to other
                    # users, raise an AuthError
                    if (message.user_1_id != token_payload["id"]) and (
                        message.user_2_id != token_payload["id"]
                    ):
                        raise AuthError(
                            {
                                "code": 403,
                                "description": "You do not have permission "
                                "to view another user's messages.",
                            },
                            403,
                        )
                else:
                    abort(404)

                messages_query = messages_query.filter(
                    (
                        (Message.for_id == token_payload["id"])
                        & (Message.for_deleted == false())
                    )
                    | (
                        (Message.from_id == token_payload["id"])
                        & (Message.from_deleted == false())
                    )
                ).filter(Message.thread == thread_id)

            messages = await sah_config.db.paginate(
                messages_query.order_by(desc(Message.date)),
                current_page=page,
            )

            # formats each message in the list
            formatted_messages = messages.resource
            total_pages = messages.total_pages

        # For threads, gets all threads' data
        else:
            # Get the thread ID, and users' names and IDs
            threads_messages = await sah_config.db.paginate(
                select(Thread)
                .filter(
                    or_(
                        and_(
                            Thread.user_1_id == token_payload["id"],
                            Thread.user1_deleted == false(),
                        ),
                        and_(
                            Thread.user_2_id == token_payload["id"],
                            Thread.user2_deleted == false(),
                        ),
                    )
                )
                .order_by(Thread.id),
                current_page=page,
                current_user_id=token_payload["id"],
            )

            total_pages = threads_messages.total_pages
            # Threads data formatting
            formatted_messages = threads_messages.resource

        return jsonify(
            {
                "success": True,
                "messages": formatted_messages,
                "current_page": int(page),
                "total_pages": total_pages,
            }
        )

    # Endpoint: POST /messages
    # Description: Adds a new message to the messages table.
    # Parameters: None.
    # Authorization: post:message.
    @app.route("/messages", methods=["POST"])
    @requires_auth(sah_config, ["post:message"])
    async def add_message(token_payload: UserData):
        # Gets the new message's data
        message_data = await request.get_json()

        validator.validate_post_or_message(
            text=message_data["messageText"],
            type="message",
            filtered_words=await get_current_filters(),
        )

        thread_id = await get_thread_id_for_users(
            user1_id=token_payload["id"],
            user2_id=message_data["forId"],
            current_user_id=token_payload["id"],
        )

        # Create a new message
        new_message = Message(
            from_id=token_payload["id"],
            for_id=int(message_data["forId"]),
            text=message_data["messageText"],
            date=datetime.strptime(message_data["date"], DATETIME_PATTERN),
            thread=thread_id,
        )

        # Create a notification for the user getting the message
        notification = Notification(
            for_id=int(message_data["forId"]),
            from_id=token_payload["id"],
            type="message",
            text="You have a new message",
            date=datetime.strptime(message_data["date"], DATETIME_PATTERN),
        )
        push_notification: RawPushData = {
            "type": "message",
            "text": f"{token_payload['displayName']} sent you a message",
        }
        notification_for = message_data["forId"]

        # Try to add the message to the database
        added = await sah_config.db.add_multiple_objects(
            objects=[new_message, notification]
        )
        sent_message = [item for item in added if "threadID" in item.keys()]
        await send_push_notification(user_id=notification_for, data=push_notification)

        return jsonify({"success": True, "message": sent_message[0]})

    # Endpoint: DELETE /messages/<mailbox_type>/<item_id>
    # Description: Deletes a message/thread from the database.
    # Parameters: mailbox_type - the type of message to delete.
    #             item_id - ID of the message/thread to delete.
    # Authorization: delete:messages.
    @app.route("/messages/<mailbox_type>/<item_id>", methods=["DELETE"])
    @requires_auth(sah_config, ["delete:messages"])
    async def delete_thread(  # TODO: This should be renamed to delete_message
        token_payload: UserData,
        mailbox_type: Literal["inbox", "outbox", "thread", "threads"],
        item_id: int,
    ):
        # Variable indicating whether to delete the message from the databse
        # or leave it in it (for the other user)
        delete_message: bool = False
        delete_item: Message | Thread | None = None

        validator.check_type(item_id, "Message ID")

        # If the mailbox type is inbox or outbox, search for a message
        # with that ID
        if mailbox_type in ["inbox", "outbox", "thread"]:
            delete_item = await sah_config.db.one_or_404(
                item_id=int(item_id),
                item_type=Message,
            )
        # If the mailbox type is threads, search for a thread with that ID
        elif mailbox_type == "threads":
            delete_item = await sah_config.db.one_or_404(
                item_id=int(item_id),
                item_type=Thread,
            )
        else:
            abort(400)

        # If the user is attempting to delete another user's messages
        # TODO: This condition is so overcomplicated, it really needs to be simpler.
        if (
            isinstance(delete_item, Message)
            and (
                (mailbox_type == "inbox" and token_payload["id"] != delete_item.for_id)
                or (
                    mailbox_type == "outbox"
                    and token_payload["id"] != delete_item.from_id
                )
            )
            or (
                isinstance(delete_item, Thread)
                and (token_payload["id"] != delete_item.user_1_id)
                and (token_payload["id"] != delete_item.user_2_id)
            )
        ):
            raise AuthError(
                {
                    "code": 403,
                    "description": "You do not have permission to "
                    "delete another user's messages.",
                },
                403,
            )

        # If the mailbox type is inbox/outbox/thread
        if isinstance(delete_item, Message) and mailbox_type in [
            "inbox",
            "outbox",
            "thread",
        ]:
            if delete_item.for_id == token_payload["id"]:
                delete_item.for_deleted = True
            else:
                delete_item.from_deleted = True

        # Check the type of item and which user deleted the message/thread
        if (
            type(delete_item) is Message
            and delete_item.for_deleted
            and delete_item.from_deleted
        ):
            delete_message = True
        elif (
            type(delete_item) is Thread
            and delete_item.user1_deleted
            and delete_item.user2_deleted
        ):
            delete_message = True
        else:
            delete_message = False

        # Try to delete the thread
        # If both users deleted the message/thread, delete it from
        # the database entirely
        if delete_message:
            await sah_config.db.delete_object(delete_item)
        # Otherwise, just update the appropriate deleted property
        else:
            if type(delete_item) == Thread:
                # For each message that wasn't deleted by the other user, the
                # value of for_deleted/from_deleted (depending on which of the users
                # it is) is updated to True
                from_stmt = (
                    update(Message)
                    .where(
                        and_(
                            Message.thread == delete_item.id,
                            Message.for_id == token_payload["id"],
                            Message.from_deleted == false(),
                        )
                    )
                    .values(for_deleted=true())
                )

                for_stmt = (
                    update(Message)
                    .where(
                        and_(
                            Message.thread == delete_item.id,
                            Message.from_id == token_payload["id"],
                            Message.for_deleted == false(),
                        )
                    )
                    .values(from_deleted=true())
                )

                delete_stmt = delete(Message).where(
                    and_(
                        Message.thread == delete_item.id,
                        or_(
                            and_(
                                Message.for_id == token_payload["id"],
                                Message.from_deleted == true(),
                            ),
                            and_(
                                Message.from_id == token_payload["id"],
                                Message.for_deleted == true(),
                            ),
                        ),
                    )
                )

                await sah_config.db.update_object(
                    obj=delete_item, current_user_id=token_payload["id"]
                )
                await sah_config.db.update_multiple_objects_with_dml(
                    update_stmts=[from_stmt, for_stmt]
                )
                await sah_config.db.delete_multiple_objects(delete_stmt=delete_stmt)

            else:
                await sah_config.db.update_object(
                    delete_item, current_user_id=token_payload["id"]
                )

        return jsonify({"success": True, "deleted": int(item_id)})

    # Endpoint: DELETE /messages/<mailbox_type>
    # Description: Clears the selected mailbox (deleting all messages in it).
    # Parameters: mailbox_type - Type of mailbox to clear.
    # Authorization: delete:messages.
    @app.route("/messages/<mailbox_type>", methods=["DELETE"])
    @requires_auth(sah_config, ["delete:messages"])
    async def clear_mailbox(
        token_payload: UserData,
        mailbox_type: Literal["inbox", "outbox", "thread", "threads"],
    ):
        num_messages = 0

        # If the user is trying to clear their inbox
        if mailbox_type == "inbox":
            num_messages = await sah_config.db.session.scalar(
                select(func.count(Message.id)).filter(
                    Message.for_id == token_payload["id"]
                )
            )
            # If there are no messages, abort
            if num_messages == 0:
                abort(404)

            # Separates messages that were deleted by the other user (and are
            # thus okay to delete completely) from messages that weren't
            # (so that these will only be deleted for one user rather than
            # for both)
            # delete_stmt = delete(Message).where(
            #     and_(Message.for_id == user_id, Message.from_deleted == true())
            # )

            # For each message that wasn't deleted by the other user, the
            # value of for_deleted (indicating whether the user the message
            # is for deleted it) is updated to True
            update_stmt = (
                update(Message)
                .where(
                    and_(
                        Message.for_id == token_payload["id"],
                        Message.from_deleted == false(),
                    )
                )
                .values(for_deleted=true())
            )

            # sah_config.db.delete_multiple_objects(delete_stmt=delete_stmt)
            await sah_config.db.update_multiple_objects_with_dml(
                update_stmts=update_stmt
            )

        # If the user is trying to clear their outbox
        if mailbox_type == "outbox":
            num_messages = await sah_config.db.session.scalar(
                select(func.count(Message.id)).filter(
                    Message.from_id == token_payload["id"]
                )
            )
            # If there are no messages, abort
            if num_messages == 0:
                abort(404)

            # Separates messages that were deleted by the other user (and are
            # thus okay to delete completely) from messages that weren't
            # (so that these will only be deleted for one user rather than
            # for both)
            delete_stmt = delete(Message).where(
                and_(
                    Message.from_id == token_payload["id"],
                    Message.for_deleted == true(),
                )
            )

            # For each message that wasn't deleted by the other user, the
            # value of from_deleted (indicating whether the user who wrote
            # the message deleted it) is updated to True
            update_stmt = (
                update(Message)
                .where(
                    and_(
                        Message.from_id == token_payload["id"],
                        Message.for_deleted == false(),
                    )
                )
                .values(from_deleted=true())
            )

            await sah_config.db.delete_multiple_objects(delete_stmt=delete_stmt)
            await sah_config.db.update_multiple_objects_with_dml(
                update_stmts=update_stmt
            )

        # If the user is trying to clear their threads mailbox
        if mailbox_type == "threads":
            num_messages = await sah_config.db.session.scalar(
                select(func.count(Thread.id)).filter(
                    or_(
                        and_(
                            Thread.user_1_id == token_payload["id"],
                            Thread.user1_deleted == false(),
                        ),
                        and_(
                            Thread.user_2_id == token_payload["id"],
                            Thread.user2_deleted == false(),
                        ),
                    )
                )
            )
            # If there are no messages, abort
            if num_messages == 0:
                abort(404)

            # Fetch all the messages that need to be updated, then the threads
            # that need to be updated
            from_messages_stmt = (
                update(Message)
                .where(
                    and_(
                        Message.from_id == token_payload["id"],
                        Message.for_deleted == false(),
                    )
                )
                .values(from_deleted=true())
            )

            for_messages_stmt = (
                update(Message)
                .where(
                    and_(
                        Message.for_id == token_payload["id"],
                        Message.from_deleted == false(),
                    )
                )
                .values(for_deleted=true())
            )

            update_stmts = [
                from_messages_stmt,
                for_messages_stmt,
            ]

            # The compile the delete statements for everything that needs to be
            # deleted.
            delete_messages_stmt = delete(Message).where(
                or_(
                    and_(
                        Message.for_id == token_payload["id"],
                        Message.from_deleted == true(),
                    ),
                    and_(
                        Message.from_id == token_payload["id"],
                        Message.for_deleted == true(),
                    ),
                )
            )

            delete_threads_stmt = delete(Thread).where(
                or_(
                    and_(
                        Thread.user_1_id == token_payload["id"],
                        Thread.user2_deleted == true(),
                    ),
                    and_(
                        Thread.user_2_id == token_payload["id"],
                        Thread.user1_deleted == true(),
                    ),
                )
            )

            await sah_config.db.delete_multiple_objects(
                delete_stmt=delete_messages_stmt
            )
            await sah_config.db.delete_multiple_objects(delete_stmt=delete_threads_stmt)
            await sah_config.db.update_multiple_objects_with_dml(
                update_stmts=update_stmts
            )

        return jsonify(
            {"success": True, "userID": token_payload["id"], "deleted": num_messages}
        )

    # Endpoint: GET /reports
    # Description: Gets the currently open reports.
    # Parameters: None.
    # Authorization: read:admin-board.
    @app.route("/reports")
    @requires_auth(sah_config, ["read:admin-board"])
    async def get_open_reports(token_payload: UserData):
        reports: dict[str, list[dict[str, Any]]] = {
            "User": [],
            "Post": [],
        }

        total_pages: dict[str, int] = {
            "User": 0,
            "Post": 0,
        }

        for report_type in reports.keys():
            reports_page = request.args.get(f"{report_type.lower()}Page", 1, type=int)

            paginated_reports = await sah_config.db.paginate(
                select(Report)
                .filter(Report.closed == false())
                .filter(Report.type == report_type)
                .order_by(Report.date),
                current_page=reports_page,
            )

            total_pages[report_type] = paginated_reports.total_pages
            reports[report_type] = paginated_reports.resource

        return jsonify(
            {
                "success": True,
                "userReports": reports["User"],
                "totalUserPages": total_pages["User"],
                "postReports": reports["Post"],
                "totalPostPages": total_pages["Post"],
            }
        )

    # Endpoint: POST /reports
    # Description: Add a new report to the database.
    # Parameters: None.
    # Authorization: post:report.
    @app.route("/reports", methods=["POST"])
    @requires_auth(sah_config, ["post:report"])
    async def create_new_report(token_payload: UserData):
        report_data = await request.get_json()

        # Check the length adn  type of the report reason
        validator.check_length(report_data["reportReason"], "report")
        validator.check_type(report_data["reportReason"], "report reason")

        # If the reported item is a post
        if report_data["type"].lower() == "post":
            # If there's no post ID, abort
            if report_data["postID"] is None:
                abort(422)

            # Get the post. If this post doesn't exist, abort
            await sah_config.db.one_or_404(
                item_id=report_data["postID"],
                item_type=Post,
            )

            report = Report(
                type=report_data["type"],
                date=datetime.strptime(report_data["date"], DATETIME_PATTERN),
                user_id=int(report_data["userID"]),
                post_id=int(report_data["postID"]),
                reporter=token_payload["id"],
                report_reason=report_data["reportReason"],
                dismissed=False,
                closed=False,
            )
        # Otherwise the reported item is a user
        else:
            # If there's no user ID, abort
            if report_data["userID"] is None:
                abort(422)

            # Get the user. If this user doesn't exist, abort
            await sah_config.db.one_or_404(
                item_id=report_data["userID"],
                item_type=User,
            )

            report = Report(
                type=report_data["type"],
                date=datetime.strptime(report_data["date"], DATETIME_PATTERN),
                user_id=int(report_data["userID"]),
                reporter=token_payload["id"],
                report_reason=report_data["reportReason"],
                dismissed=False,
                closed=False,
            )

        # Try to add the report to the database
        added_report = await sah_config.db.add_object(obj=report)

        return jsonify({"success": True, "report": added_report})

    # Endpoint: PATCH /reports/<report_id>
    # Description: Update the status of the report with the given ID.
    # Parameters: report_id - The ID of the report to update.
    # Authorization: read:admin-board.
    @app.route("/reports/<report_id>", methods=["PATCH"])
    @requires_auth(sah_config, ["read:admin-board"])
    async def update_report_status(token_payload: UserData, report_id: int):
        updated_report = await request.get_json()
        report: Report | None = await sah_config.db.session.scalar(
            select(Report).filter(Report.id == int(report_id))
        )

        # If there's no report with that ID, abort
        if report is None:
            abort(404)

        validator.check_type(report_id, "Report ID")

        # If the item reported is a user
        if report.type.lower() == "user":
            if not updated_report.get("userID", None):
                abort(422)
        # If the item reported is a post
        else:
            if not updated_report.get("postID", None):
                abort(422)

        # Set the dismissed and closed values to those of the updated report
        report.dismissed = updated_report["dismissed"]
        report.closed = updated_report["closed"]

        # Try to update the report in the database
        return_report = await sah_config.db.update_object(obj=report)

        return jsonify({"success": True, "updated": return_report})

    # Endpoint: GET /filters
    # Description: Get a paginated list of filtered words.
    # Parameters: None.
    # Authorization: read:admin-board.
    @app.route("/filters")
    @requires_auth(sah_config, ["read:admin-board"])
    async def get_filters(token_payload: UserData):
        page = request.args.get("page", 1, type=int)
        words_per_page = 10
        filtered_words = await sah_config.db.paginate(
            select(Filter).order_by(Filter.id),
            current_page=page,
            per_page=words_per_page,
        )

        return jsonify(
            {
                "success": True,
                "words": filtered_words.resource,
                "total_pages": filtered_words.total_pages,
            }
        )

    # Endpoint: POST /filters
    # Description: Add a word or phrase to the list of filtered words.
    # Parameters: None.
    # Authorization: read:admin-board.
    @app.route("/filters", methods=["POST"])
    @requires_auth(sah_config, ["read:admin-board"])
    async def add_filter(token_payload: UserData):
        new_filter = json.loads(await request.data)["word"]

        # Check if the filter is empty; if it is, abort
        validator.check_length(new_filter, "Phrase to filter")

        # If the word already exists in the filters list, abort
        existing_filter: Filter | None = await sah_config.db.session.scalar(
            select(Filter).filter(Filter.filter == new_filter.lower())
        )

        if existing_filter:
            abort(409)

        # Try to add the word to the filters list
        filter = Filter(filter=new_filter.lower())
        added = await sah_config.db.add_object(filter)

        return jsonify({"success": True, "added": added})

    # Endpoint: DELETE /filters/<filter_id>
    # Description: Delete a word from the filtered words list.
    # Parameters: filter_id - the index of the word to delete.
    # Authorization: read:admin-board.
    @app.route("/filters/<filter_id>", methods=["DELETE"])
    @requires_auth(sah_config, ["read:admin-board"])
    async def delete_filter(token_payload: UserData, filter_id: int):
        validator.check_type(filter_id, "Filter ID")

        # If there's no word in that index
        to_delete: Filter = await sah_config.db.one_or_404(
            item_id=int(filter_id),
            item_type=Filter,
        )

        # Otherwise, try to delete it
        removed = to_delete.format()
        await sah_config.db.delete_object(to_delete)

        return jsonify({"success": True, "deleted": removed})

    # Endpoint: GET /notifications
    # Description: Gets the latest notifications for the given user.
    # Parameters: None.
    # Authorization: read:messages.
    @app.route("/notifications")
    @requires_auth(sah_config, ["read:messages"])
    async def get_latest_notifications(token_payload: UserData):
        silent_refresh = request.args.get("silentRefresh", True)
        user: User = await sah_config.db.one_or_404(
            item_id=token_payload["id"],
            item_type=User,
        )

        user_id = user.id
        last_read = user.last_notifications_read

        # If there's no last_read date, it means the user never checked
        # their notifications, so set it to the time this feature was added
        if last_read is None:
            last_read = datetime(2020, 7, 1, 12, 00)

        # Gets all new notifications
        notifications_scalars = await sah_config.db.session.scalars(
            select(Notification)
            .filter(Notification.for_id == user_id)
            .filter(Notification.date > last_read)
            .order_by(Notification.date)
        )
        notifications: Sequence[Notification] = notifications_scalars.all()

        formatted_notifications = [
            notification.format() for notification in notifications
        ]

        # Updates the user's 'last read' time only if this fetch was
        # triggered by the user (meaning, they're looking at the
        # notifications tab right now).
        if silent_refresh == "false":
            # Update the user's last-read date
            user.last_notifications_read = datetime.now()
            await sah_config.db.update_object(obj=user)

        return jsonify({"success": True, "notifications": formatted_notifications})

    # Endpoint: POST /notifications
    # Description: Add a new PushSubscription to the database (for push
    #              notifications).
    # Parameters: None.
    # Authorization: read:messages.
    @app.route("/notifications", methods=["POST"])
    @requires_auth(sah_config, ["read:messages"])
    async def add_notification_subscription(token_payload: UserData):
        request_data = await request.data

        # if the request is empty, return 204. This happens due to a bug
        # in the frontend that causes the request to be sent twice, once
        # with subscription data and once with an empty object
        if not request_data:
            return ("", 204)

        subscription_json = request_data.decode("utf8").replace("'", '"')
        subscription_data = json.loads(subscription_json)

        # Create a new subscription object with the given data
        subscription = NotificationSub(
            user=token_payload["id"],
            endpoint=subscription_data["endpoint"],
            subscription_data=json.dumps(subscription_data),
        )

        # Try to add it to the database
        subscribed = token_payload["displayName"]
        sub = await sah_config.db.add_object(subscription)

        return {
            "success": True,
            "subscribed": subscribed,
            "subId": sub["id"],
        }

    # Endpoint: PATCH /notifications
    # Description: Add a new PushSubscription to the database (for push
    #              notifications).
    # Parameters: None.
    # Authorization: read:messages.
    @app.route("/notifications/<sub_id>", methods=["PATCH"])
    @requires_auth(sah_config, ["read:messages"])
    async def update_notification_subscription(token_payload: UserData, sub_id: int):
        request_data = await request.data

        # if the request is empty, return 204. This happens due to a bug
        # in the frontend that causes the request to be sent twice, once
        # with subscription data and once with an empty object
        if not request_data:
            return ("", 204)

        subscription_json = request_data.decode("utf8").replace("'", '"')
        subscription_data = json.loads(subscription_json)
        old_sub: NotificationSub = await sah_config.db.one_or_404(
            item_id=int(sub_id), item_type=NotificationSub
        )

        old_sub.endpoint = subscription_data["endpoint"]
        old_sub.subscription_data = cast(Text, json.dumps(subscription_data))

        # Try to add it to the database
        subscribed = token_payload["displayName"]
        subId = old_sub.id
        await sah_config.db.update_object(obj=old_sub)

        return {"success": True, "subscribed": subscribed, "subId": subId}

    # Error Handlers
    # -----------------------------------------------------------------
    # Bad request error handler
    @app.errorhandler(400)
    def bad_request(error):
        return (
            jsonify(
                {
                    "success": False,
                    "code": 400,
                    "message": "Bad request. Fix your request and try again.",
                }
            ),
            400,
        )

    # Not found error handler
    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify(
                {
                    "success": False,
                    "code": 404,
                    "message": "The resource you were looking for wasn't found.",
                }
            ),
            404,
        )

    # Method not allowed handler
    @app.errorhandler(405)
    def method_not_allowed(error):
        return (
            jsonify(
                {
                    "success": False,
                    "code": 405,
                    "message": "This HTTP method is not allowed at this endpoint.",
                }
            ),
            405,
        )

    # Conflict error handler
    @app.errorhandler(409)
    def conflict(error):
        return (
            jsonify(
                {
                    "success": False,
                    "code": 409,
                    "message": "Conflict. The resource you were trying to create "
                    "already exists.",
                }
            ),
            409,
        )

    # Unprocessable error handler
    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify(
                {
                    "success": False,
                    "code": 422,
                    "message": f"Unprocessable request. {error.description}",
                }
            ),
            422,
        )

    # Internal server error handler
    @app.errorhandler(500)
    def internal_server_error(error):
        return (
            jsonify(
                {
                    "success": False,
                    "code": 500,
                    "message": "An internal server error occurred. "
                    f"{error.description}",
                }
            ),
            500,
        )

    # Authentication error handler
    @app.errorhandler(AuthError)
    def auth_error(error):
        return (
            jsonify(
                {"success": False, "code": error.status_code, "message": error.error}
            ),
            error.status_code,
        )

    # Validation error handler
    @app.errorhandler(ValidationError)
    def validation_error(error):
        return (
            jsonify(
                {"success": False, "code": error.status_code, "message": error.error}
            ),
            error.status_code,
        )

    return app
