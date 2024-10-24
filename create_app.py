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

from pywebpush import WebPushException, webpush  # type: ignore
from quart import Quart, Response, abort, jsonify, request
from quart_cors import cors
from sqlalchemy import Text, and_, delete, desc, false, func, or_, select, true, update

from auth import AuthError, UserData, requires_auth
from config import SAHConfig

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
from models.common import CoreSAHModel
from models.schemas.messages import Thread
from utils.push_notifications import (
    RawPushData,
    generate_push_data,
    generate_vapid_claims,
)
from utils.validator import ValidationError, Validator

DATETIME_PATTERN = "%Y-%m-%dT%H:%M:%S.%fZ"


def create_app(config: SAHConfig) -> Quart:
    # create and configure the app
    app = Quart("SendAHug")
    config.db.init_app(app=app)
    config.db.set_default_per_page(per_page=5)
    # Utilities
    cors(app)
    validator = Validator(
        {
            "post": {"max": 480, "min": 1},
            "message": {"max": 480, "min": 1},
            "user": {"max": 60, "min": 1},
            "report": {"max": 120, "min": 1},
        }
    )

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

    # Send push notification
    async def send_push_notification(user_id: int, data: RawPushData):
        vapid_key = os.environ.get("PRIVATE_VAPID_KEY")
        notification_data = generate_push_data(data)
        vapid_claims = generate_vapid_claims()
        subscriptions_scalars = await config.db.session.scalars(
            select(NotificationSub).filter(NotificationSub.user == int(user_id))
        )
        subscriptions: Sequence[NotificationSub] = subscriptions_scalars.all()

        # Try to send the push notification
        try:
            for subscription in subscriptions:
                sub_data = json.loads(str(subscription.subscription_data))
                webpush(
                    subscription_info=sub_data,
                    data=json.dumps(notification_data),
                    vapid_private_key=vapid_key,
                    vapid_claims=cast(dict, vapid_claims),
                )
        # If there's an error, print the details
        except WebPushException as e:
            app.logger.error(e)

    async def get_current_filters() -> list[str]:
        """Fetches the current filters from the database."""
        filters = await config.db.session.scalars(select(Filter))
        return [filter.filter for filter in filters.all()]

    async def get_thread_id_for_users(
        user1_id: int, user2_id: int, current_user_id: int
    ) -> int:
        """
        Gets a thread ID for messaging between two users.
        If there's no existing thread, it creates a new thread.
        """
        # Checks if there's an existing thread between the users (with user 1
        # being the sender and user 2 being the recipient)
        thread: Thread | None = await config.db.session.scalar(
            select(Thread).filter(
                or_(
                    and_(
                        Thread.user_1_id == int(user1_id),
                        Thread.user_2_id == int(user2_id),
                    ),
                    and_(
                        Thread.user_1_id == int(user2_id),
                        Thread.user_2_id == int(user1_id),
                    ),
                )
            )
        )

        # If there's no thread between the users
        if thread is None:
            new_thread = Thread(
                user_1_id=int(user1_id),
                user_2_id=int(user2_id),
            )
            # Try to create the new thread
            added_thread = await config.db.add_object(
                new_thread, current_user_id=current_user_id
            )
            return added_thread["id"]
        # If there's a thread between the users
        else:
            return thread.id

    # Routes
    # -----------------------------------------------------------------
    # Endpoint: GET /
    # Description: Gets recent and suggested posts.
    # Parameters: None.
    # Authorization: None.
    @app.route("/")
    async def index():
        posts: dict[str, list[dict[str, Any]]] = {
            "recent": [],
            "suggested": [],
        }

        for target in posts.keys():
            posts_query = select(Post).filter(Post.open_report == false())

            # Gets the ten most recent posts
            if target == "recent":
                posts_query = posts_query.order_by(desc(Post.date))
            # Gets the ten posts with the least hugs
            else:
                posts_query = posts_query.order_by(Post.given_hugs, Post.date)

            posts_scalars = await config.db.session.scalars(posts_query.limit(10))
            post_instances: Sequence[Post] = posts_scalars.all()

            # formats each post in the list
            posts[target] = [post.format() for post in post_instances]

        return jsonify(
            {
                "success": True,
                "recent": posts["recent"],
                "suggested": posts["suggested"],
            }
        )

    # Endpoint: POST /
    # Description: Run a search.
    # Parameters: None.
    # Authorization: None.
    @app.route("/", methods=["POST"])
    async def search():
        search_query = json.loads(await request.data)["search"]
        current_page = request.args.get("page", 1, type=int)

        # Check if the search query is empty; if it is, abort
        validator.check_length(search_query, "Search query")
        # Check if the search query isn't a string; if it isn't, abort
        validator.check_type(search_query, "Search query")

        # Get the users with the search query in their display name
        users_scalars = await config.db.session.scalars(
            select(User).filter(User.display_name.ilike(f"%{search_query}%"))
        )
        users: Sequence[User] = users_scalars.all()

        posts = await config.db.paginate(
            select(Post)
            .order_by(desc(Post.date))
            .filter(Post.text.ilike(f"%{search_query}%"))
            .filter(Post.open_report == false()),
            current_page=current_page,
        )

        # Formats the users' data
        formatted_users = [user.format() for user in users]

        return jsonify(
            {
                "success": True,
                "users": formatted_users,
                "posts": posts.resource,
                "user_results": len(users),
                "post_results": posts.total_items,
                "current_page": int(current_page),
                "total_pages": posts.total_pages,
            }
        )

    # Endpoint: POST /posts
    # Description: Add a new post to the database.
    # Parameters: None.
    # Authorization: post:post.
    @app.route("/posts", methods=["POST"])
    @requires_auth(config, ["post:post"])
    async def add_post(token_payload: UserData):
        new_post_data = await request.get_json()
        validator.validate_post_or_message(
            text=new_post_data["text"],
            type="post",
            filtered_words=await get_current_filters(),
        )

        # Create a new post object
        new_post = Post(
            user_id=token_payload["id"],
            text=new_post_data["text"],
            date=datetime.strptime(new_post_data["date"], DATETIME_PATTERN),
            given_hugs=0,
            sent_hugs=[],
        )

        # Try to add the post to the database
        added_post = await config.db.add_object(new_post)

        return jsonify({"success": True, "posts": added_post})

    # Endpoint: PATCH /posts/<post_id>
    # Description: Updates a post (either its text or its hugs) in the
    #              database.
    # Parameters: post_id - ID of the post to update.
    # Authorization: patch:my-post or patch:any-post.
    @app.route("/posts/<post_id>", methods=["PATCH"])
    @requires_auth(config, ["patch:my-post", "patch:any-post"])
    async def edit_post(token_payload: UserData, post_id: int):
        # Check if the post ID isn't an integer; if it isn't, abort
        validator.check_type(post_id, "Post ID")

        updated_post = await request.get_json()
        original_post: Post = await config.db.one_or_404(
            item_id=int(post_id),
            item_type=Post,
        )

        # If the user's permission is 'patch my' the user can only edit
        # their own posts. If it's a user trying to edit the text
        # of a post that doesn't belong to them, throw an auth error
        if (
            "patch:my-post" in token_payload["role"]["permissions"]
            and original_post.user_id != token_payload["id"]
            and original_post.text != updated_post["text"]
        ):
            raise AuthError(
                {
                    "code": 403,
                    "description": "You do not have permission to edit this post.",
                },
                403,
            )

        # Otherwise, the user either attempted to edit their own post, or
        # they're allowed to edit any post, so let them update the post
        # If the text was changed
        if original_post.text != updated_post["text"]:
            validator.validate_post_or_message(
                text=updated_post["text"],
                type="post",
                filtered_words=await get_current_filters(),
            )
            original_post.text = updated_post["text"]

        # Try to update the database
        updated = await config.db.update_object(obj=original_post)

        return jsonify({"success": True, "updated": updated})

    # Endpoint: POST /posts/<post_id>/hugs
    # Description: Sends a hug to a specific user.
    # Parameters: user_id - the user to send a hug to.
    # Authorization: read:user
    @app.route("/posts/<post_id>/hugs", methods=["POST"])
    @requires_auth(config, ["patch:my-post", "patch:any-post"])
    async def send_hug_for_post(token_payload: UserData, post_id: int):
        # Check if the post ID isn't an integer; if it isn't, abort
        validator.check_type(post_id, "Post ID")
        message_details = await request.get_json()

        original_post: Post = await config.db.one_or_404(
            item_id=int(post_id),
            item_type=Post,
        )

        # Gets the current user so we can update their 'sent hugs' value
        current_user: User = await config.db.one_or_404(
            item_id=token_payload["id"],
            item_type=User,
        )

        hugs = original_post.sent_hugs or []
        post_author: User | None = await config.db.session.scalar(
            select(User).filter(User.id == original_post.user_id)
        )
        notification: Notification | None = None
        push_notification: RawPushData | None = None

        # If the current user already sent a hug on this post, abort
        if current_user.id in hugs:
            abort(409)

        # Otherwise, continue adding the new hug
        original_post.given_hugs += 1
        current_user.given_hugs += 1
        hugs.append(current_user.id)
        original_post.sent_hugs = [*hugs]

        to_add: list[CoreSAHModel] = []
        sent_message = False

        # Create a notification for the user getting the hug
        if post_author:
            post_author.received_hugs += 1
            today = datetime.now()

            if message_details.get("messageText"):
                validator.validate_post_or_message(
                    text=message_details["messageText"],
                    type="message",
                    filtered_words=await get_current_filters(),
                )

                thread_id = await get_thread_id_for_users(
                    user1_id=current_user.id,
                    user2_id=original_post.user_id,
                    current_user_id=current_user.id,
                )

                message = Message(
                    from_id=current_user.id,
                    for_id=original_post.user_id,
                    text=message_details["messageText"],
                    date=today,
                    thread=thread_id,
                )
                to_add.append(message)
                sent_message = True

            base_notification_message = "You got a hug"
            base_push_notification_message = (
                f"{current_user.display_name} sent you a hug"
            )

            notification = Notification(
                for_id=post_author.id,
                from_id=current_user.id,
                type="hug",
                text=(
                    f"{base_notification_message} and a message"
                    if sent_message
                    else base_notification_message
                ),
                date=today,
            )
            push_notification = {
                "type": "hug",
                "text": (
                    f"{base_push_notification_message} and a message"
                    if sent_message
                    else base_push_notification_message
                ),
            }
            to_add.append(notification)

        # Try to update the database
        # Objects to update
        to_update: list[CoreSAHModel] = [
            original_post,
            current_user,
            cast(User, post_author),
        ]

        if len(to_add):
            await config.db.add_multiple_objects(objects=to_add)

        await config.db.update_multiple_objects(objects=to_update)

        if post_author and push_notification:
            await send_push_notification(user_id=post_author.id, data=push_notification)

        return jsonify(
            {
                "success": True,
                "updated": (
                    f"Successfully sent hug for post {int(post_id)} "
                    f"and a message to user {int(original_post.user_id)}"
                    if sent_message
                    else f"Successfully sent hug for post {int(post_id)}"
                ),
            }
        )

    # Endpoint: DELETE /posts/<post_id>
    # Description: Deletes a post from the database.
    # Parameters: post_id - ID of the post to delete.
    # Authorization: delete:my-post or delete:any-post.
    @app.route("/posts/<post_id>", methods=["DELETE"])
    @requires_auth(config, ["delete:my-post", "delete:any-post"])
    async def delete_post(token_payload: UserData, post_id: int):
        # Check if the post ID isn't an integer; if it isn't, abort
        validator.check_type(post_id, "Post ID")

        # Gets the post to delete
        post_data: Post = await config.db.one_or_404(
            item_id=int(post_id),
            item_type=Post,
        )

        # If the user only has permission to delete their own posts
        if "delete:my-post" in token_payload["role"]["permissions"]:
            # If it's not the same user, they can't delete the post, so an
            # auth error is raised
            if post_data.user_id != token_payload["id"]:
                raise AuthError(
                    {
                        "code": 403,
                        "description": "You do not have permission to delete "
                        "this post.",
                    },
                    403,
                )

        # Otherwise, it's either their post or they're allowed to delete any
        # post.
        # Try to delete the post
        await config.db.delete_object(post_data)

        return jsonify({"success": True, "deleted": int(post_id)})

    # Endpoint: GET /posts/<type>
    # Description: Gets all new posts.
    # Parameters: type - Type of posts (new or suggested) to fetch.
    # Authorization: None.
    @app.route("/posts/<type>")
    async def get_new_posts(type: Literal["new", "suggested"]):
        page = request.args.get("page", 1, type=int)

        full_posts_query = select(Post).filter(Post.open_report == false())

        if type == "new":
            full_posts_query = full_posts_query.order_by(desc(Post.date))
        else:
            full_posts_query = full_posts_query.order_by(Post.given_hugs, Post.date)

        paginated_posts = await config.db.paginate(full_posts_query, current_page=page)

        return jsonify(
            {
                "success": True,
                "posts": paginated_posts.resource,
                "total_pages": paginated_posts.total_pages,
            }
        )

    # Endpoint: GET /users/<type>
    # Description: Gets users by a given type.
    # Parameters: type - A type by which to filter the users.
    # Authorization: read:admin-board.
    @app.route("/users/<type>")
    @requires_auth(config, ["read:admin-board"])
    async def get_users_by_type(token_payload: UserData, type: str):
        page = request.args.get("page", 1, type=int)

        # If the type of users to fetch is blocked users
        if type.lower() == "blocked":
            # Check which users need to be unblocked
            current_date = datetime.now()
            user_scalars = await config.db.session.scalars(
                select(User).filter(User.release_date < current_date)
            )
            users_to_unblock: Sequence[User] = user_scalars.all()
            to_unblock = []

            for user in users_to_unblock:
                user.release_date = None
                user.role_id = 3  # regular user
                to_unblock.append(user)

            # Try to update the database
            await config.db.update_multiple_objects(objects=to_unblock)

            # Get all blocked users
            paginated_users = await config.db.paginate(
                select(User).filter(User.blocked == true()).order_by(User.release_date),
                current_page=page,
            )

        else:
            abort(500, "This isn't supported right now")

        return jsonify(
            {
                "success": True,
                "users": paginated_users.resource,
                "total_pages": paginated_users.total_pages,
            }
        )

    # Endpoint: GET /users/all/<user_id>
    # Description: Gets the user's data.
    # Parameters: user_id - The user's Firebase ID / internal ID.
    # Authorization: read:user.
    @app.route("/users/all/<user_id>")
    @requires_auth(config, ["read:user"])
    async def get_user_data(token_payload: UserData, user_id: int | str):
        print(token_payload["firebaseId"])
        # Try to convert it to a number; if it's a number, it's a
        # regular ID, so try to find the user with that ID
        try:
            int(user_id)
            user_data = await config.db.session.scalar(
                select(User).filter(User.id == int(user_id))
            )
        # Otherwise, it's a Firebase ID
        except ValueError:
            user_data = await config.db.session.scalar(
                select(User).filter(User.firebase_id == user_id)
            )

        # If there's no user with that Firebase ID, abort
        if user_data is None:
            abort(404)

        formatted_user = user_data.format()

        # If the user is currently blocked, compare their release date to
        # the current date and time.
        if user_data.release_date:
            current_date = datetime.now()
            # If it's past the user's release date, unblock them
            if user_data.release_date < current_date:
                user_data.release_date = None
                user_data.role_id = 3  # regular user

                # Try to update the database
                formatted_user = await config.db.update_object(user_data)

        return jsonify({"success": True, "user": formatted_user})

    # Endpoint: POST /users
    # Description: Adds a new user to the users table.
    # Parameters: None.
    # Authorization: post:user.
    @app.route("/users", methods=["POST"])
    @requires_auth(config, ["post:user"])
    async def add_user(token_payload):
        # Gets the user's data
        user_data = await request.get_json()

        # If the user is attempting to add a user that isn't themselves to
        # the database, aborts
        if user_data["firebaseId"] != token_payload["uid"]:
            abort(422)

        # Checks whether a user with that Firebase ID already exists
        # If it is, aborts
        database_user: User | None = await config.db.session.scalar(
            select(User).filter(User.firebase_id == user_data["firebaseId"])
        )

        if database_user:
            abort(409)

        new_user = User(
            display_name=user_data["displayName"],
            last_notifications_read=datetime.now(),
            login_count=0,
            auto_refresh=False,
            refresh_rate=20,
            push_enabled=False,
            selected_character="kitty",
            icon_colours='{"character":"#BA9F93","lbg":"#e2a275",'
            '"rbg":"#f8eee4","item":"#f4b56a"}',
            role_id=4,  # Set the new user role
            firebase_id=user_data["firebaseId"],
        )

        # Try to add the user to the database
        added_user = await config.db.add_object(new_user)

        return jsonify({"success": True, "user": added_user})

    # Endpoint: PATCH /users/all/<user_id>
    # Description: Updates a user in the database.
    # Parameters: user_id - ID of the user to update.
    # Authorization: patch:user or patch:any-user.
    @app.route("/users/all/<user_id>", methods=["PATCH"])
    @requires_auth(config, ["patch:user", "patch:any-user"])
    async def edit_user(token_payload: UserData, user_id: int):
        # Check if the user ID isn't an integer; if it isn't, abort
        validator.check_type(user_id, "User ID")

        updated_user = await request.get_json()
        user_to_update: User = await config.db.one_or_404(
            item_id=int(user_id),
            item_type=User,
        )

        # If there's a login count (meaning, the user is editing their own
        # data), update it
        user_to_update.login_count = updated_user.get(
            "loginCount", user_to_update.login_count
        )

        # If the user is attempting to change a user's display name, check
        # their permissions
        if "displayName" in updated_user:
            # if the name changed and the user is only allowed to
            # change their own name (user / mod)
            if (
                updated_user["displayName"] != user_to_update.display_name
                and "patch:user" in token_payload["role"]["permissions"]
            ):
                # If it's not the current user, abort
                if token_payload["id"] != user_to_update.id:
                    raise AuthError(
                        {
                            "code": 403,
                            "description": "You do not have permission to "
                            "edit this user's display name.",
                        },
                        403,
                    )

            # Otherwise, check the length and type of the user's display name
            validator.check_length(updated_user["displayName"], "display name")
            validator.check_type(updated_user["displayName"], "display name")

            user_to_update.display_name = updated_user["displayName"]

        # If the request was in done in order to block or unblock a user
        if (
            "blocked" in updated_user
            and updated_user["blocked"] != user_to_update.blocked
        ):
            # If the user doesn't have permission to block/unblock a user
            if "block:user" not in token_payload["role"]["permissions"]:
                raise AuthError(
                    {
                        "code": 403,
                        "description": "You do not have permission to block this user.",
                    },
                    403,
                )

            # Otherwise, the user is a manager, so they can block a user.
            # In that case, block / unblock the user as requested.
            user_to_update.release_date = updated_user["releaseDate"]
            user_to_update.role_id = BLOCKED_USER_ROLE_ID  # blocked user

        # If the user is attempting to change a user's settings, check
        # whether it's the current user
        if (
            "autoRefresh" in updated_user
            or "pushEnabled" in updated_user
            or "refreshRate" in updated_user
        ):
            # If it's not the current user, abort
            if token_payload["id"] != user_to_update.id:
                raise AuthError(
                    {
                        "code": 403,
                        "description": "You do not have permission to edit "
                        "another user's settings.",
                    },
                    403,
                )

        # If the user is changing their settings
        if updated_user.get("autoRefresh") and updated_user.get("refreshRate", 0) < 20:
            abort(422)

        # If the user is changing their settings
        user_to_update.auto_refresh = updated_user.get(
            "autoRefresh", user_to_update.auto_refresh
        )
        user_to_update.push_enabled = updated_user.get(
            "pushEnabled", user_to_update.push_enabled
        )
        user_to_update.refresh_rate = updated_user.get(
            "refreshRate", user_to_update.refresh_rate
        )
        user_to_update.selected_character = updated_user.get(
            "selectedIcon", user_to_update.selected_character
        )

        # If the user is changing their character colours
        if "iconColours" in updated_user:
            user_to_update.icon_colours = json.dumps(updated_user["iconColours"])

        # If the user clicked the "verify email" link, get the value from the
        # token payload. It should be true
        if "emailVerified" in updated_user:
            user_to_update.email_verified = token_payload["email_verified"]

            # If they verified their email and their current role is new user, update it
            if token_payload["email_verified"] and user_to_update.role_id == 4:
                user_to_update.role_id = 3  # user

        # Try to update it in the database
        updated = await config.db.update_object(obj=user_to_update)

        return jsonify({"success": True, "updated": updated})

    # Endpoint: GET /users/all/<user_id>/posts
    # Description: Gets a specific user's posts.
    # Parameters: user_id - whose posts to fetch.
    # Authorization: read:user.
    @app.route("/users/all/<user_id>/posts")
    @requires_auth(config, ["read:user"])
    async def get_user_posts(token_payload: UserData, user_id: int):
        page = request.args.get("page", 1, type=int)

        # if there's no user ID provided, abort with 'Bad Request'
        if user_id is None:
            abort(400)

        validator.check_type(user_id, "User ID")

        # Gets all posts written by the given user
        user_posts = await config.db.paginate(
            select(Post).filter(Post.user_id == int(user_id)).order_by(Post.date),
            current_page=page,
        )

        return jsonify(
            {
                "success": True,
                "posts": user_posts.resource,
                "page": int(page),
                "total_pages": user_posts.total_pages,
            }
        )

    # Endpoint: DELETE /users/all/<user_id>/posts
    # Description: Deletes a specific user's posts.
    # Parameters: user_id - whose posts to delete.
    # Authorization: delete:my-post or delete:any-post
    @app.route("/users/all/<user_id>/posts", methods=["DELETE"])
    @requires_auth(config, ["delete:my-post", "delete:any-post"])
    async def delete_user_posts(token_payload: UserData, user_id: int):
        validator.check_type(user_id, "User ID")

        # If the user making the request isn't the same as the user
        # whose posts should be deleted
        # If the user can only delete their own posts, they're not
        # allowed to delete others' posts, so raise an AuthError
        if (
            token_payload["id"] != int(user_id)
            and "delete:my-post" in token_payload["role"]["permissions"]
        ):
            raise AuthError(
                {
                    "code": 403,
                    "description": "You do not have permission to delete "
                    "another user's posts.",
                },
                403,
            )

        # Otherwise, the user is either trying to delete their own posts or
        # they're allowed to delete others' posts, so let them continue
        post_count: int | None = await config.db.session.scalar(
            select(func.count(Post.id)).filter(Post.user_id == int(user_id))
        )

        # If the user has no posts, abort
        if not post_count:
            abort(404)

        # Try to delete
        await config.db.delete_multiple_objects(
            delete_stmt=delete(Post).where(Post.user_id == int(user_id))
        )

        return jsonify({"success": True, "userID": int(user_id), "deleted": post_count})

    # Endpoint: POST /users/all/<user_id>/hugs
    # Description: Sends a hug to a specific user.
    # Parameters: user_id - the user to send a hug to.
    # Authorization: read:user
    @app.route("/users/all/<user_id>/hugs", methods=["POST"])
    @requires_auth(config, ["read:user"])
    async def send_hug_to_user(token_payload: UserData, user_id: int):
        validator.check_type(user_id, "User ID")
        user_to_hug: User = await config.db.one_or_404(
            item_id=int(user_id),
            item_type=User,
        )
        # Fetch the current user to update their 'given hugs' value
        current_user: User = await config.db.one_or_404(
            item_id=token_payload["id"], item_type=User
        )

        current_user.given_hugs += 1
        user_to_hug.received_hugs += 1
        today = datetime.now()
        notification = Notification(
            for_id=user_to_hug.id,
            from_id=current_user.id,
            type="hug",
            text="You got a hug",
            date=today,
        )
        push_notification: RawPushData = {
            "type": "hug",
            "text": f"{current_user.display_name} sent you a hug",
        }

        # Try to update it in the database
        to_update = [user_to_hug, current_user]

        await config.db.add_object(obj=notification)
        await config.db.update_multiple_objects(objects=to_update)
        await send_push_notification(user_id=user_to_hug.id, data=push_notification)

        return jsonify(
            {
                "success": True,
                "updated": f"Successfully sent hug to {user_to_hug.display_name}",
            }
        )

    # Endpoint: GET /messages
    # Description: Gets the user's messages.
    # Parameters: None.
    # Authorization: read:messages.
    @app.route("/messages")
    @requires_auth(config, ["read:messages"])
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
                message = await config.db.session.scalar(
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

            messages = await config.db.paginate(
                messages_query.order_by(desc(Message.date)),
                current_page=page,
            )

            # formats each message in the list
            formatted_messages = messages.resource
            total_pages = messages.total_pages

        # For threads, gets all threads' data
        else:
            # Get the thread ID, and users' names and IDs
            threads_messages = await config.db.paginate(
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
    @requires_auth(config, ["post:message"])
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
        added = await config.db.add_multiple_objects(
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
    @requires_auth(config, ["delete:messages"])
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
            delete_item = await config.db.one_or_404(
                item_id=int(item_id),
                item_type=Message,
            )
        # If the mailbox type is threads, search for a thread with that ID
        elif mailbox_type == "threads":
            delete_item = await config.db.one_or_404(
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
            await config.db.delete_object(delete_item)
        # Otherwise, just update the appropriate deleted property
        else:
            if type(delete_item) is Thread:
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

                await config.db.update_object(
                    obj=delete_item, current_user_id=token_payload["id"]
                )
                await config.db.update_multiple_objects_with_dml(
                    update_stmts=[from_stmt, for_stmt]
                )
                await config.db.delete_multiple_objects(delete_stmt=delete_stmt)

            else:
                await config.db.update_object(
                    delete_item, current_user_id=token_payload["id"]
                )

        return jsonify({"success": True, "deleted": int(item_id)})

    # Endpoint: DELETE /messages/<mailbox_type>
    # Description: Clears the selected mailbox (deleting all messages in it).
    # Parameters: mailbox_type - Type of mailbox to clear.
    # Authorization: delete:messages.
    @app.route("/messages/<mailbox_type>", methods=["DELETE"])
    @requires_auth(config, ["delete:messages"])
    async def clear_mailbox(
        token_payload: UserData,
        mailbox_type: Literal["inbox", "outbox", "thread", "threads"],
    ):
        num_messages = 0

        # If the user is trying to clear their inbox
        if mailbox_type == "inbox":
            num_messages = await config.db.session.scalar(
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

            # config.db.delete_multiple_objects(delete_stmt=delete_stmt)
            await config.db.update_multiple_objects_with_dml(update_stmts=update_stmt)

        # If the user is trying to clear their outbox
        if mailbox_type == "outbox":
            num_messages = await config.db.session.scalar(
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

            await config.db.delete_multiple_objects(delete_stmt=delete_stmt)
            await config.db.update_multiple_objects_with_dml(update_stmts=update_stmt)

        # If the user is trying to clear their threads mailbox
        if mailbox_type == "threads":
            num_messages = await config.db.session.scalar(
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

            await config.db.delete_multiple_objects(delete_stmt=delete_messages_stmt)
            await config.db.delete_multiple_objects(delete_stmt=delete_threads_stmt)
            await config.db.update_multiple_objects_with_dml(update_stmts=update_stmts)

        return jsonify(
            {"success": True, "userID": token_payload["id"], "deleted": num_messages}
        )

    # Endpoint: GET /reports
    # Description: Gets the currently open reports.
    # Parameters: None.
    # Authorization: read:admin-board.
    @app.route("/reports")
    @requires_auth(config, ["read:admin-board"])
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

            paginated_reports = await config.db.paginate(
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
    @requires_auth(config, ["post:report"])
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
            await config.db.one_or_404(
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
            await config.db.one_or_404(
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
        added_report = await config.db.add_object(obj=report)

        return jsonify({"success": True, "report": added_report})

    # Endpoint: PATCH /reports/<report_id>
    # Description: Update the status of the report with the given ID.
    # Parameters: report_id - The ID of the report to update.
    # Authorization: read:admin-board.
    @app.route("/reports/<report_id>", methods=["PATCH"])
    @requires_auth(config, ["read:admin-board"])
    async def update_report_status(token_payload: UserData, report_id: int):
        updated_report = await request.get_json()
        report: Report | None = await config.db.session.scalar(
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
        return_report = await config.db.update_object(obj=report)

        return jsonify({"success": True, "updated": return_report})

    # Endpoint: GET /filters
    # Description: Get a paginated list of filtered words.
    # Parameters: None.
    # Authorization: read:admin-board.
    @app.route("/filters")
    @requires_auth(config, ["read:admin-board"])
    async def get_filters(token_payload: UserData):
        page = request.args.get("page", 1, type=int)
        words_per_page = 10
        filtered_words = await config.db.paginate(
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
    @requires_auth(config, ["read:admin-board"])
    async def add_filter(token_payload: UserData):
        new_filter = json.loads(await request.data)["word"]

        # Check if the filter is empty; if it is, abort
        validator.check_length(new_filter, "Phrase to filter")

        # If the word already exists in the filters list, abort
        existing_filter: Filter | None = await config.db.session.scalar(
            select(Filter).filter(Filter.filter == new_filter.lower())
        )

        if existing_filter:
            abort(409)

        # Try to add the word to the filters list
        filter = Filter(filter=new_filter.lower())
        added = await config.db.add_object(filter)

        return jsonify({"success": True, "added": added})

    # Endpoint: DELETE /filters/<filter_id>
    # Description: Delete a word from the filtered words list.
    # Parameters: filter_id - the index of the word to delete.
    # Authorization: read:admin-board.
    @app.route("/filters/<filter_id>", methods=["DELETE"])
    @requires_auth(config, ["read:admin-board"])
    async def delete_filter(token_payload: UserData, filter_id: int):
        validator.check_type(filter_id, "Filter ID")

        # If there's no word in that index
        to_delete: Filter = await config.db.one_or_404(
            item_id=int(filter_id),
            item_type=Filter,
        )

        # Otherwise, try to delete it
        removed = to_delete.format()
        await config.db.delete_object(to_delete)

        return jsonify({"success": True, "deleted": removed})

    # Endpoint: GET /notifications
    # Description: Gets the latest notifications for the given user.
    # Parameters: None.
    # Authorization: read:messages.
    @app.route("/notifications")
    @requires_auth(config, ["read:messages"])
    async def get_latest_notifications(token_payload: UserData):
        current_page = request.args.get("page", 1, type=int)
        read_status = request.args.get("readStatus", None)

        get_query = (
            select(Notification)
            .order_by(Notification.date.desc())
            .filter(Notification.for_id == token_payload["id"])
        )

        if read_status == "true":
            get_query = get_query.filter(Notification.read == true())
        elif read_status == "false":
            get_query = get_query.filter(Notification.read == false())

        # Gets all notifications
        notifications = await config.db.paginate(
            query=get_query,
            current_page=current_page,
            per_page=20,
        )

        new_notifications_count = await config.db.session.scalar(
            select(func.count())
            .select_from(Notification)
            .where(
                and_(
                    Notification.read == false(),
                    Notification.for_id == token_payload["id"],
                )
            )
        )

        return jsonify(
            {
                "success": True,
                "notifications": notifications.resource,
                "newCount": new_notifications_count,
                # TODO: Left these in snake case for consistency with the other
                # endpoints, but it really should be camel case
                "current_page": int(current_page),
                "total_pages": notifications.total_pages,
                "totalItems": notifications.total_items,
            }
        )

    # Endpoint: PATCH /notifications
    # Description: Updates one or more notifications' read status.
    # Parameters: None.
    # Authorization: read:messages.
    @app.route("/notifications", methods=["PATCH"])
    @requires_auth(config, ["read:messages"])
    async def update_notifications(token_payload: UserData):
        request_data = json.loads(await request.data)

        if (
            not request_data.get("notification_ids")
            or request_data.get("read", None) is None
        ):
            abort(400)

        if request_data["notification_ids"] == "all":
            update_query = (
                update(Notification)
                .where(Notification.for_id == token_payload["id"])
                .values(read=request_data["read"])
            )
        else:
            notification_ids: list[int] = request_data["notification_ids"]

            existing_notifications = await config.db.session.scalars(
                select(Notification.id).where(
                    and_(
                        Notification.id.in_(notification_ids),
                        Notification.for_id == token_payload["id"],
                    ),
                )
            )

            # Make sure the user has permission to see all the notifications
            if len(list(existing_notifications)) != len(notification_ids):
                raise AuthError(
                    {
                        "code": 403,
                        "description": "You do not have permission to update some "
                        "of the provided notifications. Ensure all notifications "
                        "are meant for you and try again.",
                    },
                    403,
                )

            update_query = (
                update(Notification)
                .where(
                    and_(
                        Notification.id.in_(notification_ids),
                        Notification.for_id == token_payload["id"],
                    )
                )
                .values(read=request_data["read"])
            )

        await config.db.update_multiple_objects_with_dml(update_stmts=update_query)

        return {
            "success": True,
            "updated": request_data["notification_ids"],
            "read": request_data["read"],
        }

    # Endpoint: POST /push_subscriptions
    # Description: Add a new PushSubscription to the database (for push
    #              notifications).
    # Parameters: None.
    # Authorization: read:messages.
    @app.route("/push_subscriptions", methods=["POST"])
    @requires_auth(config, ["read:messages"])
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
        sub = await config.db.add_object(subscription)

        return {
            "success": True,
            "subscribed": subscribed,
            "subId": sub["id"],
        }

    # Endpoint: PATCH /push_subscriptions/<sub_id>
    # Description: Add a new PushSubscription to the database (for push
    #              notifications).
    # Parameters: None.
    # Authorization: read:messages.
    @app.route("/push_subscriptions/<sub_id>", methods=["PATCH"])
    @requires_auth(config, ["read:messages"])
    async def update_notification_subscription(token_payload: UserData, sub_id: int):
        request_data = await request.data

        # if the request is empty, return 204. This happens due to a bug
        # in the frontend that causes the request to be sent twice, once
        # with subscription data and once with an empty object
        if not request_data:
            return ("", 204)

        subscription_json = request_data.decode("utf8").replace("'", '"')
        subscription_data = json.loads(subscription_json)
        old_sub: NotificationSub = await config.db.one_or_404(
            item_id=int(sub_id), item_type=NotificationSub
        )

        old_sub.endpoint = subscription_data["endpoint"]
        old_sub.subscription_data = cast(Text, json.dumps(subscription_data))

        # Try to add it to the database
        subscribed = token_payload["displayName"]
        subId = old_sub.id
        await config.db.update_object(obj=old_sub)

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
