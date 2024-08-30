from datetime import datetime
import json
from typing import Sequence, cast

from quart import Blueprint, Response, jsonify, request
from sqlalchemy import Text, select

from auth import UserData, requires_auth
from config import sah_config

from models import Notification, NotificationSub, User

notifications_endpoints = Blueprint("notifications", __name__)


# Endpoint: GET /notifications
# Description: Gets the latest notifications for the given user.
# Parameters: None.
# Authorization: read:messages.
@notifications_endpoints.route("/notifications")
@requires_auth(sah_config, ["read:messages"])
async def get_latest_notifications(token_payload: UserData) -> Response:
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

    formatted_notifications = [notification.format() for notification in notifications]

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
@notifications_endpoints.route("/notifications", methods=["POST"])
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
