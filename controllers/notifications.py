import json
from typing import cast

from quart import Blueprint, Response, abort, jsonify, request
from sqlalchemy import Text, and_, false, func, select, true, update

from auth import AuthError, UserData, requires_auth
from config import sah_config

from models import Notification, NotificationSub

notifications_endpoints = Blueprint("notifications", __name__)


# Endpoint: GET /notifications
# Description: Gets the latest notifications for the given user.
# Parameters: None.
# Authorization: read:messages.
@notifications_endpoints.route("/notifications")
@requires_auth(sah_config, ["read:messages"])
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
    notifications = await sah_config.db.paginate(
        query=get_query,
        current_page=current_page,
        per_page=20,
    )

    new_notifications_count = await sah_config.db.session.scalar(
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
@notifications_endpoints.route("/notifications", methods=["PATCH"])
@requires_auth(sah_config, ["read:messages"])
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

        existing_notifications = await sah_config.db.session.scalars(
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

    await sah_config.db.update_multiple_objects_with_dml(update_stmts=update_query)

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
@notifications_endpoints.route("/push_subscriptions", methods=["POST"])
@requires_auth(sah_config, ["read:messages"])
async def add_notification_subscription(token_payload: UserData) -> Response:
    request_data = await request.data

    # if the request is empty, return 204. This happens due to a bug
    # in the frontend that causes the request to be sent twice, once
    # with subscription data and once with an empty object
    if not request_data:
        return Response({}, status=204)

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

    return jsonify(
        {
            "success": True,
            "subscribed": subscribed,
            "subId": sub["id"],
        }
    )


# Endpoint: PATCH /notifications
# Description: Add a new PushSubscription to the database (for push
#              notifications).
# Parameters: None.
# Authorization: read:messages.
@notifications_endpoints.route("/notifications/<sub_id>", methods=["PATCH"])
@requires_auth(sah_config, ["read:messages"])
async def update_notification_subscription(
    token_payload: UserData, sub_id: int
) -> Response:
    request_data = await request.data

    # if the request is empty, return 204. This happens due to a bug
    # in the frontend that causes the request to be sent twice, once
    # with subscription data and once with an empty object
    if not request_data:
        return Response({}, status=204)

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

    return jsonify({"success": True, "subscribed": subscribed, "subId": subId})
