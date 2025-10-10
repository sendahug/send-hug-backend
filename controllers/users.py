from datetime import datetime
from typing import Sequence

from quart import Blueprint, Response, abort, jsonify, request
from sqlalchemy import delete, func, select, true

from auth import AuthError, UserData, requires_auth
from config.config import sah_config

from controllers.common import (
    get_archive_action_from_body,
    send_push_notification,
    validator,
)
from models import (
    BLOCKED_USER_ROLE_ID,
    Notification,
    Post,
    User,
    UserIconColour,
    UserSetting,
)
from models.schemas.enums import UserIconCharacter, UserIconPart
from utils.push_notifications import RawPushData

users_endpoints = Blueprint("users", __name__)


# Endpoint: GET /users
# Description: Gets users by a given type.
# Parameters: None.
# Authorization: read:admin-board.
@users_endpoints.route("/users")
@requires_auth(sah_config, ["read:admin-board"])
async def get_users(token_payload: UserData) -> Response:
    page = request.args.get("page", 1, type=int)
    blocked = request.args.get("blocked", None, type=bool)

    # If the type of users to fetch is blocked users
    if blocked is True:
        # Check which users need to be unblocked
        current_date = datetime.now()
        user_scalars = await sah_config.db.session.scalars(
            select(User).filter(User.release_date < current_date)
        )
        users_to_unblock: Sequence[User] = user_scalars.all()
        to_unblock = []

        for user in users_to_unblock:
            user.release_date = None
            user.role_id = 3  # regular user
            to_unblock.append(user)

        # Try to update the database
        await sah_config.db.update_multiple_objects(objects=to_unblock)

        # Get all blocked users
        paginated_users = await sah_config.db.paginate(
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


# Endpoint: GET /users/<user_id>
# Description: Gets the user's data.
# Parameters: user_id - The user's Firebase ID / internal ID.
# Authorization: read:user.
@users_endpoints.route("/users/<user_id>")
@requires_auth(sah_config, ["read:user"])
async def get_user_data(token_payload: UserData, user_id: int | str) -> Response:
    # Try to convert it to a number; if it's a number, it's a
    # regular ID, so try to find the user with that ID
    try:
        int(user_id)
        user_data = await sah_config.db.session.scalar(
            select(User).filter(User.id == int(user_id))
        )
    # Otherwise, it's a Firebase ID
    except ValueError:
        user_data = await sah_config.db.session.scalar(
            select(User).filter(User.firebase_id == user_id)
        )

    # If there's no user with that Firebase ID, abort
    if user_data is None:
        abort(404)

    formatted_user = user_data.format(current_user=token_payload["id"])

    # If the user is currently blocked, compare their release date to
    # the current date and time.
    if user_data.release_date:
        current_date = datetime.now()
        # If it's past the user's release date, unblock them
        if user_data.release_date < current_date:
            user_data.release_date = None
            user_data.role_id = 3  # regular user

            # Try to update the database
            formatted_user = await sah_config.db.update_object(
                user_data, current_user=token_payload["id"]
            )

    return jsonify({"success": True, "user": formatted_user})


# Endpoint: POST /users
# Description: Adds a new user to the users table.
# Parameters: None.
# Authorization: post:user.
@users_endpoints.route("/users", methods=["POST"])
@requires_auth(sah_config, ["post:user"])
async def add_user(token_payload) -> Response:
    # Gets the user's data
    user_data = await request.get_json()

    # If the user is attempting to add a user that isn't themselves to
    # the database, aborts
    if user_data["firebaseId"] != token_payload["uid"]:
        abort(422)

    # Checks whether a user with that Firebase ID already exists
    # If it is, aborts
    database_user: User | None = await sah_config.db.session.scalar(
        select(User).filter(User.firebase_id == user_data["firebaseId"])
    )

    if database_user:
        abort(409)

    new_user = User(
        display_name=user_data["displayName"],
        login_count=0,
        selected_character=UserIconCharacter.KITTY,
        icon_colours=[
            UserIconColour(icon_part=UserIconPart.CHARACTER, colour="#BA9F93"),
            UserIconColour(icon_part=UserIconPart.LBG, colour="#e2a275"),
            UserIconColour(icon_part=UserIconPart.RBG, colour="#f8eee4"),
            UserIconColour(icon_part=UserIconPart.ITEM, colour="#f4b56a"),
        ],
        role_id=4,  # Set the new user role
        firebase_id=user_data["firebaseId"],
        email=token_payload["email"],
        user_settings=UserSetting(
            email_notifications_enabled=user_data.get(
                "emailNotificationsEnabled", False
            ),
            message_notifications=False,
            hugs_digest_notifications=False,
            you_okay_notifications=False,
            previous_interaction_notifications=False,
            last_updated_at=datetime.now(),
            auto_refresh_enabled=False,
            refresh_rate=20,
            push_enabled=False,
        ),
    )

    # Try to add the user to the database
    added_user = await sah_config.db.add_object(
        new_user, current_user=token_payload["uid"]
    )

    return jsonify({"success": True, "user": added_user})


# Endpoint: PATCH /users/<user_id>
# Description: Updates a user in the database.
# Parameters: user_id - ID of the user to update.
# Authorization: patch:user or patch:any-user.
@users_endpoints.route("/users/<user_id>", methods=["PATCH"])
@requires_auth(sah_config, ["patch:user", "patch:any-user"])
async def edit_user(token_payload: UserData, user_id: int) -> Response:
    # Check if the user ID isn't an integer; if it isn't, abort
    validator.check_type(user_id, "User ID")

    updated_user = await request.get_json()
    user_to_update: User = await sah_config.db.one_or_404(
        item_id=int(user_id),
        item_type=User,
    )
    if user_to_update.archived:
        raise AuthError(
            {
                "code": 422,
                "description": "You cannot edit an archived user.",
            },
            422,
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
    if "blocked" in updated_user and updated_user["blocked"] != user_to_update.blocked:
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
        or "preferences" in updated_user
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

    if not user_to_update.user_settings:
        user_to_update.user_settings = UserSetting(last_updated_at=datetime.now())

    # If the user is changing their settings
    user_to_update.user_settings.auto_refresh_enabled = updated_user.get(
        "autoRefresh", user_to_update.user_settings.auto_refresh_enabled
    )
    user_to_update.user_settings.push_enabled = updated_user.get(
        "pushEnabled", user_to_update.user_settings.push_enabled
    )
    user_to_update.user_settings.refresh_rate = updated_user.get(
        "refreshRate", user_to_update.user_settings.refresh_rate
    )
    user_to_update.selected_character = UserIconCharacter(
        updated_user.get("selectedIcon", user_to_update.selected_character.value)
    )

    updated_preferences = updated_user.get("preferences", {})
    user_to_update.user_settings.email_notifications_enabled = updated_preferences.get(
        "emailNotificationsEnabled",
        (
            user_to_update.user_settings.email_notifications_enabled
            if user_to_update.user_settings
            else False
        ),
    )
    user_to_update.user_settings.message_notifications = updated_preferences.get(
        "messageNotifications",
        (
            user_to_update.user_settings.message_notifications
            if user_to_update.user_settings
            else False
        ),
    )
    user_to_update.user_settings.hugs_digest_notifications = updated_preferences.get(
        "hugsDigestNotifications",
        (
            user_to_update.user_settings.hugs_digest_notifications
            if user_to_update.user_settings
            else False
        ),
    )
    user_to_update.user_settings.you_okay_notifications = updated_preferences.get(
        "youOkayNotifications",
        (
            user_to_update.user_settings.you_okay_notifications
            if user_to_update.user_settings
            else False
        ),
    )
    user_to_update.user_settings.previous_interaction_notifications = (
        updated_preferences.get(
            "previousInteractionNotifications",
            (
                user_to_update.user_settings.previous_interaction_notifications
                if user_to_update.user_settings
                else False
            ),
        )
    )
    user_to_update.user_settings.last_updated_at = datetime.now()

    # If the user is changing their character colours
    if "iconColours" in updated_user:
        for icon_colour in user_to_update.icon_colours:
            icon_colour.colour = updated_user["iconColours"][
                icon_colour.icon_part.value
            ]

    # If the user clicked the "verify email" link, get the value from the
    # token payload. It should be true
    if "emailVerified" in updated_user:
        user_to_update.email_verified = token_payload["email_verified"]

        # If they verified their email and their current role is new user, update it
        if token_payload["email_verified"] and user_to_update.role_id == 4:
            user_to_update.role_id = 3  # user

    # Try to update it in the database
    updated = await sah_config.db.update_object(
        obj=user_to_update, current_user=token_payload["id"]
    )

    return jsonify({"success": True, "updated": updated})


# Endpoint: GET /users/<user_id>/posts
# Description: Gets a specific user's posts.
# Parameters: user_id - whose posts to fetch.
# Authorization: read:user.
@users_endpoints.route("/users/<user_id>/posts")
@requires_auth(sah_config, ["read:user"])
async def get_user_posts(token_payload: UserData, user_id: int) -> Response:
    page = request.args.get("page", 1, type=int)

    # if there's no user ID provided, abort with 'Bad Request'
    if user_id is None:
        abort(400)

    validator.check_type(user_id, "User ID")

    # Gets all posts written by the given user
    user_posts = await sah_config.db.paginate(
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


# Endpoint: DELETE /users/<user_id>/posts
# Description: Deletes a specific user's posts.
# Parameters: user_id - whose posts to delete.
# Authorization: delete:my-post or delete:any-post
@users_endpoints.route("/users/<user_id>/posts", methods=["DELETE"])
@requires_auth(sah_config, ["delete:my-post", "delete:any-post"])
async def delete_user_posts(token_payload: UserData, user_id: int) -> Response:
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
    post_count: int | None = await sah_config.db.session.scalar(
        select(func.count(Post.id)).filter(Post.user_id == int(user_id))
    )

    # If the user has no posts, abort
    if not post_count:
        abort(404)

    # Try to delete
    await sah_config.db.delete_multiple_objects(
        delete_stmt=delete(Post).where(Post.user_id == int(user_id))
    )

    return jsonify({"success": True, "userID": int(user_id), "deleted": post_count})


# Endpoint: POST /users/<user_id>/hugs
# Description: Sends a hug to a specific user.
# Parameters: user_id - the user to send a hug to.
# Authorization: read:user
@users_endpoints.route("/users/<user_id>/hugs", methods=["POST"])
@requires_auth(sah_config, ["read:user"])
async def send_hug_to_user(token_payload: UserData, user_id: int) -> Response:
    validator.check_type(user_id, "User ID")
    user_to_hug: User = await sah_config.db.one_or_404(
        item_id=int(user_id),
        item_type=User,
    )
    if user_to_hug.archived:
        raise AuthError(
            {
                "code": 422,
                "description": "This user cannot receive any hugs at the moment",
            },
            422,
        )

    # Fetch the current user to update their 'given hugs' value
    current_user: User = await sah_config.db.one_or_404(
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

    await sah_config.db.add_object(obj=notification)
    await sah_config.db.update_multiple_objects(objects=to_update)
    await send_push_notification(user_id=user_to_hug.id, data=push_notification)

    return jsonify(
        {
            "success": True,
            "updated": f"Successfully sent hug to {user_to_hug.display_name}",
        }
    )


# Endpoint: PATCH /users/<user_id>/archive
# Description: Archives a user in the database.
# Parameters: user_id - ID of the user to update.
# Authorization: patch:my-user or patch:any-user.
@users_endpoints.route("/users/<user_id>/archive", methods=["PATCH"])
@requires_auth(sah_config, ["archive:user"])
async def archive_user(token_payload: UserData, user_id: int) -> Response:
    action = await get_archive_action_from_body(await request.get_json())

    # Check if the user ID isn't an integer; if it isn't, abort
    validator.check_type(user_id, "User ID")
    original_user: User = await sah_config.db.one_or_404(
        item_id=int(user_id),
        item_type=User,
    )

    # Otherwise, the user either attempted to un/archive their own user, or
    # they're allowed to un/archive any user, so let them update the user
    if action == "archive":
        original_user.archived = True
    else:
        original_user.archived = False

    # Try to update the database
    archived = await sah_config.db.update_object(obj=original_user)

    return jsonify({"success": True, f"{action}d": archived})
