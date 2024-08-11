import json
import os
from typing import Sequence, cast

from pywebpush import WebPushException, webpush  # type: ignore
from quart import current_app
from sqlalchemy import and_, or_, select

from config import sah_config

from models import Filter, NotificationSub, Thread
from utils.push_notifications import (
    RawPushData,
    generate_push_data,
    generate_vapid_claims,
)
from utils.validator import Validator

DATETIME_PATTERN = "%Y-%m-%dT%H:%M:%S.%fZ"

validator = Validator(
    {
        "post": {"max": 480, "min": 1},
        "message": {"max": 480, "min": 1},
        "user": {"max": 60, "min": 1},
        "report": {"max": 120, "min": 1},
    }
)


# Send push notification
async def send_push_notification(user_id: int, data: RawPushData):
    vapid_key = os.environ.get("PRIVATE_VAPID_KEY")
    notification_data = generate_push_data(data)
    vapid_claims = generate_vapid_claims()
    subscriptions_scalars = await sah_config.db.session.scalars(
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
        current_app.logger.error(e)


async def get_current_filters() -> list[str]:
    """Fetches the current filters from the database."""
    filters = await sah_config.db.session.scalars(select(Filter))
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
    thread: Thread | None = await sah_config.db.session.scalar(
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
        added_thread = await sah_config.db.add_object(
            new_thread, current_user_id=current_user_id
        )
        return added_thread["id"]
    # If there's a thread between the users
    else:
        return thread.id
