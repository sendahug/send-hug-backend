from datetime import datetime
from typing import Literal, cast

from quart import Blueprint, Response, abort, jsonify, request
from sqlalchemy import desc, false, select

from auth import AuthError, UserData, requires_auth
from config import sah_config

from .common import (
    DATETIME_PATTERN,
    get_current_filters,
    get_thread_id_for_users,
    send_push_notification,
    validator,
)
from models import CoreSAHModel, Message, Notification, Post, User
from utils.push_notifications import RawPushData

posts_endpoints = Blueprint("posts", __name__)


# Endpoint: POST /posts
# Description: Add a new post to the database.
# Parameters: None.
# Authorization: post:post.
@posts_endpoints.route("/posts", methods=["POST"])
@requires_auth(sah_config, ["post:post"])
async def add_post(token_payload: UserData) -> Response:
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
    added_post = await sah_config.db.add_object(new_post)

    return jsonify({"success": True, "posts": added_post})


# Endpoint: PATCH /posts/<post_id>
# Description: Updates a post (either its text or its hugs) in the
#              database.
# Parameters: post_id - ID of the post to update.
# Authorization: patch:my-post or patch:any-post.
@posts_endpoints.route("/posts/<post_id>", methods=["PATCH"])
@requires_auth(sah_config, ["patch:my-post", "patch:any-post"])
async def edit_post(token_payload: UserData, post_id: int) -> Response:
    # Check if the post ID isn't an integer; if it isn't, abort
    validator.check_type(post_id, "Post ID")

    updated_post = await request.get_json()
    original_post: Post = await sah_config.db.one_or_404(
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
    updated = await sah_config.db.update_object(obj=original_post)

    return jsonify({"success": True, "updated": updated})


# Endpoint: POST /posts/<post_id>/hugs
# Description: Sends a hug to a specific user.
# Parameters: user_id - the user to send a hug to.
# Authorization: read:user
@posts_endpoints.route("/posts/<post_id>/hugs", methods=["POST"])
@requires_auth(sah_config, ["patch:my-post", "patch:any-post"])
async def send_hug_for_post(token_payload: UserData, post_id: int) -> Response:
    # Check if the post ID isn't an integer; if it isn't, abort
    validator.check_type(post_id, "Post ID")
    message_details = await request.get_json()

    original_post: Post = await sah_config.db.one_or_404(
        item_id=int(post_id),
        item_type=Post,
    )

    # Gets the current user so we can update their 'sent hugs' value
    current_user: User = await sah_config.db.one_or_404(
        item_id=token_payload["id"],
        item_type=User,
    )

    hugs = original_post.sent_hugs or []
    post_author: User | None = await sah_config.db.session.scalar(
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
        base_push_notification_message = f"{current_user.display_name} sent you a hug"

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
        await sah_config.db.add_multiple_objects(objects=to_add)

    await sah_config.db.update_multiple_objects(objects=to_update)

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
@posts_endpoints.route("/posts/<post_id>", methods=["DELETE"])
@requires_auth(sah_config, ["delete:my-post", "delete:any-post"])
async def delete_post(token_payload: UserData, post_id: int) -> Response:
    # Check if the post ID isn't an integer; if it isn't, abort
    validator.check_type(post_id, "Post ID")

    # Gets the post to delete
    post_data: Post = await sah_config.db.one_or_404(
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
                    "description": "You do not have permission to delete " "this post.",
                },
                403,
            )

    # Otherwise, it's either their post or they're allowed to delete any
    # post.
    # Try to delete the post
    await sah_config.db.delete_object(post_data)

    return jsonify({"success": True, "deleted": int(post_id)})


# Endpoint: GET /posts/<type>
# Description: Gets all new posts.
# Parameters: type - Type of posts (new or suggested) to fetch.
# Authorization: None.
@posts_endpoints.route("/posts/<type>")
async def get_new_posts(type: Literal["new", "suggested"]) -> Response:
    page = request.args.get("page", 1, type=int)

    full_posts_query = select(Post).filter(Post.open_report == false())

    if type == "new":
        full_posts_query = full_posts_query.order_by(desc(Post.date))
    else:
        full_posts_query = full_posts_query.order_by(Post.given_hugs, Post.date)

    paginated_posts = await sah_config.db.paginate(full_posts_query, current_page=page)

    return jsonify(
        {
            "success": True,
            "posts": paginated_posts.resource,
            "total_pages": paginated_posts.total_pages,
        }
    )
