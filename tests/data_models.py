from datetime import datetime
from typing import Sequence
import json

from sqlalchemy import select, text

from models.models import (
    Permission,
    Post,
    User,
    Message,
    Thread,
    Report,
    Notification,
    Filter,
    Role,
    NotificationSub,
)
from models.db import SendADatabase


DATETIME_PATTERN = "%Y-%m-%d %H:%M:%S.%f"


async def create_filters(db: SendADatabase):
    """Creates the filters in the test database."""
    filter_1 = Filter(id=1, filter="filtered_word_1")
    filter_2 = Filter(id=2, filter="filtered_word_2")

    try:
        db.session.add_all([filter_1, filter_2])
        await db.session.execute(text("ALTER SEQUENCE filters_id_seq RESTART WITH 3;"))
        await db.session.commit()
    finally:
        await db.session.remove()


async def create_permissions(db: SendADatabase):
    permission_1 = Permission(
        id=1, permission="block:user", description="Block or unblock a user"
    )
    permission_2 = Permission(
        id=2, permission="delete:any-post", description="Delete anyones post"
    )
    permission_3 = Permission(
        id=3, permission="delete:messages", description="Delete my messages"
    )
    permission_4 = Permission(
        id=4, permission="patch:any-post", description="Edit any post"
    )
    permission_5 = Permission(
        id=5, permission="patch:any-user", description="Edit any users display name"
    )
    permission_6 = Permission(
        id=6, permission="post:message", description="Create a new message"
    )
    permission_7 = Permission(
        id=7, permission="post:post", description="Create a new post"
    )
    permission_8 = Permission(
        id=8, permission="post:report", description="Create a new report."
    )
    permission_9 = Permission(
        id=9, permission="read:admin-board", description="View admin dashboard"
    )
    permission_10 = Permission(
        id=10, permission="read:messages", description="Read user messages"
    )
    permission_11 = Permission(
        id=11, permission="read:user", description="Read user data"
    )
    permission_12 = Permission(
        id=12, permission="delete:my-post", description="Delete my own post"
    )
    permission_13 = Permission(
        id=13, permission="patch:user", description="Edit user data"
    )
    permission_14 = Permission(
        id=14, permission="patch:my-post", description="Edit my post"
    )
    permission_15 = Permission(
        id=15, permission="post:user", description="Create a new user"
    )

    try:
        db.session.add_all(
            [
                permission_1,
                permission_2,
                permission_3,
                permission_4,
                permission_5,
                permission_6,
                permission_7,
                permission_8,
                permission_9,
                permission_10,
                permission_11,
                permission_12,
                permission_13,
                permission_14,
                permission_15,
            ]
        )
        await db.session.execute(
            text("ALTER SEQUENCE permissions_id_seq RESTART WITH 16;")
        )
        await db.session.commit()
    finally:
        await db.session.remove()


async def create_roles(db: SendADatabase):
    role_1 = Role(id=1, name="admin")
    role_2 = Role(id=2, name="moderator")
    role_3 = Role(id=3, name="user")
    role_4 = Role(id=4, name="new user")
    role_5 = Role(id=5, name="blocked user")

    try:
        permissions_scalars = await db.session.scalars(
            select(Permission).order_by(Permission.id)
        )
        permissions: Sequence[Permission] = permissions_scalars.all()

        role_1.permissions = [*permissions[0:11]]
        role_2.permissions = [*permissions[2:4], *permissions[5:8], *permissions[9:13]]
        role_3.permissions = [permissions[2], *permissions[5:8], *permissions[9:14]]
        role_4.permissions = [permissions[2], *permissions[5:7], *permissions[9:]]
        role_5.permissions = [
            permissions[2],
            permissions[5],
            permissions[7],
            *permissions[9:],
        ]

        db.session.add_all([role_1, role_2, role_3, role_4, role_5])
        await db.session.execute(text("ALTER SEQUENCE roles_id_seq RESTART WITH 6;"))
        await db.session.commit()
    finally:
        await db.session.remove()


async def create_users(db: SendADatabase):
    """Creates the users in the test database."""
    user_1 = User(
        id=1,
        auth0_id="auth0|5ed34765f0b8e60c8e87ca62",
        received_hugs=12,
        given_hugs=2,
        display_name="shirb",
        login_count=60,
        blocked=False,
        open_report=False,
        release_date=None,
        last_notifications_read=None,
        auto_refresh=False,
        push_enabled=False,
        refresh_rate=0,
        icon_colours='{"character": "#ba9f93", "lbg": "#e2a275", '
        '"rbg": "#f8eee4", "item": "#f4b56a"}',
        selected_character="kitty",
        role_id=3,
        firebase_id="abcd",
    )
    user_2 = User(
        id=4,
        auth0_id="auth0|5ed8e3d0def75d0befbc7e50",
        received_hugs=106,
        given_hugs=117,
        display_name="user14",
        login_count=55,
        blocked=False,
        open_report=False,
        release_date=datetime.strptime("2020-10-30 18:13:21.282", DATETIME_PATTERN),
        last_notifications_read=datetime.strptime(
            "2020-10-30 18:13:21.282054", DATETIME_PATTERN
        ),
        auto_refresh=True,
        push_enabled=False,
        refresh_rate=None,
        icon_colours='{"character": "#ba9f93", "lbg": "#e2a275", '
        '"rbg": "#f8eee4", "item": "#f4b56a"}',
        selected_character="kitty",
        role_id=1,
        firebase_id="ijkl",
    )
    user_3 = User(
        id=5,
        auth0_id="auth0|5ede3e7a0793080013259050",
        received_hugs=2,
        given_hugs=0,
        display_name="user52",
        login_count=7,
        blocked=False,
        open_report=False,
        release_date=None,
        last_notifications_read=None,
        auto_refresh=False,
        push_enabled=False,
        refresh_rate=0,
        icon_colours='{"character": "#ba9f93", "lbg": "#e2a275", '
        '"rbg": "#f8eee4", "item": "#f4b56a"}',
        selected_character="kitty",
        role_id=2,
        firebase_id="efgh",
    )
    user_4 = User(
        id=9,
        auth0_id="auth0|5edf7b060793080013276746",
        received_hugs=0,
        given_hugs=1,
        display_name="user93",
        login_count=2,
        blocked=False,
        open_report=False,
        release_date=None,
        last_notifications_read=None,
        auto_refresh=False,
        push_enabled=False,
        refresh_rate=0,
        icon_colours='{"character": "#ba9f93", "lbg": "#e2a275", '
        '"rbg": "#f8eee4", "item": "#f4b56a"}',
        selected_character="kitty",
        role_id=1,
        firebase_id="zxy",
    )
    user_5 = User(
        id=20,
        auth0_id="auth0|5f4b9fd9915cd400670f4633",
        received_hugs=0,
        given_hugs=0,
        display_name="user24",
        login_count=4,
        blocked=True,
        open_report=False,
        release_date=datetime.strptime("2120-08-11 08:33:22.473", DATETIME_PATTERN),
        last_notifications_read=datetime.strptime(
            "2020-11-03 20:21:13.399365", DATETIME_PATTERN
        ),
        auto_refresh=False,
        push_enabled=False,
        refresh_rate=0,
        icon_colours='{"character": "#ba9f93", "lbg": "#e2a275", '
        '"rbg": "#f8eee4", "item": "#f4b56a"}',
        selected_character="kitty",
        role_id=5,
        firebase_id="twg",
    )

    try:
        db.session.add_all([user_1, user_2, user_3, user_4, user_5])
        await db.session.execute(text("ALTER SEQUENCE users_id_seq RESTART WITH 21;"))
        await db.session.commit()
    finally:
        await db.session.remove()


async def create_posts(db: SendADatabase):
    """Creates the posts in the test database."""
    post_1 = Post(
        id=1,
        user_id=1,
        text="test",
        date=datetime.strptime("2020-06-01 15:05:01.966", DATETIME_PATTERN),
        given_hugs=2,
        open_report=False,
        sent_hugs=[4],
    )
    post_2 = Post(
        id=2,
        user_id=1,
        text="test",
        date=datetime.strptime("2020-06-01 15:10:59.898", DATETIME_PATTERN),
        given_hugs=2,
        open_report=False,
        sent_hugs=[4],
    )
    post_3 = Post(
        id=4,
        user_id=1,
        text="test",
        date=datetime.strptime("2020-06-01 15:17:56.294", DATETIME_PATTERN),
        given_hugs=2,
        open_report=False,
        sent_hugs=[4],
    )
    post_4 = Post(
        id=6,
        user_id=1,
        text="testing",
        date=datetime.strptime("2020-06-01 15:19:41.25", DATETIME_PATTERN),
        given_hugs=1,
        open_report=False,
        sent_hugs=[4],
    )
    post_5 = Post(
        id=7,
        user_id=1,
        text="testing #2",
        date=datetime.strptime("2020-06-01 15:20:11.927", DATETIME_PATTERN),
        given_hugs=1,
        open_report=False,
        sent_hugs=[4],
    )
    post_6 = Post(
        id=9,
        user_id=1,
        text="leeeeeee b :))",
        date=datetime.strptime("2020-06-03 07:11:40.421", DATETIME_PATTERN),
        given_hugs=1,
        open_report=False,
        sent_hugs=[4],
    )
    post_7 = Post(
        id=10,
        user_id=1,
        text="cutie baby lee",
        date=datetime.strptime("2020-06-04 07:56:09.791", DATETIME_PATTERN),
        given_hugs=1,
        open_report=False,
        sent_hugs=[4],
    )
    post_8 = Post(
        id=11,
        user_id=1,
        text="baby lee :))",
        date=datetime.strptime("2020-06-04 08:15:50.811", DATETIME_PATTERN),
        given_hugs=2,
        open_report=False,
        sent_hugs=[4],
    )
    post_9 = Post(
        id=12,
        user_id=5,
        text="new user",
        date=datetime.strptime("2020-06-08 14:07:25.297", DATETIME_PATTERN),
        given_hugs=1,
        open_report=False,
        sent_hugs=[4],
    )
    post_10 = Post(
        id=13,
        user_id=5,
        text="2nd post",
        date=datetime.strptime("2020-06-08 14:30:58.88", DATETIME_PATTERN),
        given_hugs=1,
        open_report=False,
        sent_hugs=[4],
    )
    post_11 = Post(
        id=22,
        user_id=4,
        text="testing service worker",
        date=datetime.strptime("2020-06-27 10:31:24.915", DATETIME_PATTERN),
        given_hugs=1,
        open_report=False,
        sent_hugs=[4],
    )
    post_12 = Post(
        id=23,
        user_id=4,
        text="post",
        date=datetime.strptime("2020-06-27 19:17:31.072", DATETIME_PATTERN),
        given_hugs=2,
        open_report=False,
        sent_hugs=[4],
    )
    post_13 = Post(
        id=25,
        user_id=4,
        text="for report",
        date=datetime.strptime("2020-07-06 08:02:02.184", DATETIME_PATTERN),
        given_hugs=67,
        open_report=False,
        sent_hugs=[4],
    )
    post_14 = Post(
        id=26,
        user_id=4,
        text="testing new design",
        date=datetime.strptime("2020-07-13 18:40:34.806", DATETIME_PATTERN),
        given_hugs=1,
        open_report=False,
        sent_hugs=[4],
    )
    post_15 = Post(
        id=28,
        user_id=4,
        text="testing2",
        date=datetime.strptime("2020-07-13 18:43:51.255", DATETIME_PATTERN),
        given_hugs=9,
        open_report=False,
        sent_hugs=[4],
    )
    post_16 = Post(
        id=30,
        user_id=4,
        text="hello :)",
        date=datetime.strptime("2020-07-18 12:11:39.65", DATETIME_PATTERN),
        given_hugs=24,
        open_report=False,
        sent_hugs=[4],
    )
    post_17 = Post(
        id=35,
        user_id=4,
        text="testing new rule",
        date=datetime.strptime("2020-10-24 12:19:24.199", DATETIME_PATTERN),
        given_hugs=1,
        open_report=False,
        sent_hugs=[4],
    )
    post_18 = Post(
        id=36,
        user_id=4,
        text="post",
        date=datetime.strptime("2020-10-31 14:00:58.851", DATETIME_PATTERN),
        given_hugs=1,
        open_report=False,
        sent_hugs=[4],
    )
    post_19 = Post(
        id=38,
        user_id=4,
        text="test",
        date=datetime.strptime("2020-10-31 14:46:11.378", DATETIME_PATTERN),
        given_hugs=1,
        open_report=False,
        sent_hugs=[4],
    )
    post_20 = Post(
        id=39,
        user_id=4,
        text="testing",
        date=datetime.strptime("2020-10-31 14:59:05.703", DATETIME_PATTERN),
        given_hugs=1,
        open_report=False,
        sent_hugs=[4],
    )
    post_21 = Post(
        id=42,
        user_id=4,
        text="test 2",
        date=datetime.strptime("2020-10-31 15:09:50.26", DATETIME_PATTERN),
        given_hugs=1,
        open_report=False,
        sent_hugs=[4],
    )
    post_22 = Post(
        id=43,
        user_id=4,
        text="test button",
        date=datetime.strptime("2020-10-31 15:20:45.636", DATETIME_PATTERN),
        given_hugs=0,
        open_report=False,
        sent_hugs=[],
    )
    post_23 = Post(
        id=44,
        user_id=4,
        text="button",
        date=datetime.strptime("2020-10-31 15:25:18.172", DATETIME_PATTERN),
        given_hugs=0,
        open_report=False,
        sent_hugs=[],
    )
    post_24 = Post(
        id=45,
        user_id=4,
        text="button 2",
        date=datetime.strptime("2020-10-31 15:26:48.043", DATETIME_PATTERN),
        given_hugs=0,
        open_report=False,
        sent_hugs=[],
    )

    try:
        db.session.add_all(
            [
                post_1,
                post_2,
                post_3,
                post_4,
                post_5,
                post_6,
                post_7,
                post_8,
                post_9,
                post_10,
                post_11,
                post_12,
                post_13,
                post_14,
                post_15,
                post_16,
                post_17,
                post_18,
                post_19,
                post_20,
                post_21,
                post_22,
                post_23,
                post_24,
            ]
        )
        await db.session.execute(text("ALTER SEQUENCE posts_id_seq RESTART WITH 46;"))
        await db.session.commit()
    finally:
        await db.session.remove()


async def create_threads(db: SendADatabase):
    """Creates the threads in the test database."""
    thread_1 = Thread(
        id=1, user_1_id=1, user_2_id=1, user_1_deleted=False, user_2_deleted=False
    )
    thread_2 = Thread(
        id=2, user_1_id=1, user_2_id=5, user_1_deleted=False, user_2_deleted=False
    )
    thread_3 = Thread(
        id=3, user_1_id=1, user_2_id=4, user_1_deleted=False, user_2_deleted=False
    )
    thread_4 = Thread(
        id=6, user_1_id=9, user_2_id=5, user_1_deleted=False, user_2_deleted=False
    )
    thread_5 = Thread(
        id=7, user_1_id=20, user_2_id=4, user_1_deleted=False, user_2_deleted=False
    )
    thread_6 = Thread(
        id=8, user_1_id=20, user_2_id=1, user_1_deleted=True, user_2_deleted=False
    )
    thread_7 = Thread(
        id=4, user_1_id=4, user_2_id=5, user_1_deleted=True, user_2_deleted=False
    )

    try:
        db.session.add_all(
            [thread_1, thread_2, thread_3, thread_4, thread_5, thread_6, thread_7]
        )
        await db.session.execute(text("ALTER SEQUENCE threads_id_seq RESTART WITH 9;"))
        await db.session.commit()
    finally:
        await db.session.remove()


async def create_messages(db: SendADatabase):
    """Creates the messages in the test database."""
    message_1 = Message(
        id=5,
        from_id=4,
        for_id=5,
        text="hellllllllo :)",
        date=datetime.strptime("2020-06-08 14:43:30.593", DATETIME_PATTERN),
        thread=4,
        for_deleted=False,
        from_deleted=True,
    )
    message_2 = Message(
        id=8,
        from_id=5,
        for_id=4,
        text="hi there :)",
        date=datetime.strptime("2020-06-08 14:50:19.006", DATETIME_PATTERN),
        thread=4,
        for_deleted=False,
        from_deleted=True,
    )
    message_3 = Message(
        id=1,
        from_id=1,
        for_id=1,
        text="hang in there :)",
        date=datetime.strptime("2020-06-02 10:39:56.337", DATETIME_PATTERN),
        thread=1,
        for_deleted=False,
        from_deleted=False,
    )
    message_4 = Message(
        id=3,
        from_id=5,
        for_id=1,
        text="you'll be okay <3",
        date=datetime.strptime("2020-06-08 14:42:02.759", DATETIME_PATTERN),
        thread=2,
        for_deleted=False,
        from_deleted=False,
    )
    message_5 = Message(
        id=7,
        from_id=1,
        for_id=5,
        text="more testing",
        date=datetime.strptime("2020-06-08 14:45:05.713", DATETIME_PATTERN),
        thread=2,
        for_deleted=False,
        from_deleted=False,
    )
    message_6 = Message(
        id=9,
        from_id=4,
        for_id=1,
        text="hang in there",
        date=datetime.strptime("2020-06-08 14:43:15.000", DATETIME_PATTERN),
        thread=3,
        for_deleted=False,
        from_deleted=False,
    )
    message_7 = Message(
        id=16,
        from_id=9,
        for_id=5,
        text="hiiiii",
        date=datetime.strptime("2020-06-14 14:25:37.569", DATETIME_PATTERN),
        thread=6,
        for_deleted=False,
        from_deleted=False,
    )
    message_8 = Message(
        id=10,
        from_id=4,
        for_id=1,
        text="hi :)",
        date=datetime.strptime("2020-06-14 14:07:37.49", DATETIME_PATTERN),
        thread=3,
        for_deleted=True,
        from_deleted=False,
    )
    message_9 = Message(
        id=21,
        from_id=4,
        for_id=1,
        text="hi",
        date=datetime.strptime("2020-07-06 17:33:55.712", DATETIME_PATTERN),
        thread=3,
        for_deleted=False,
        from_deleted=False,
    )
    message_10 = Message(
        id=25,
        from_id=20,
        for_id=4,
        text="hang in there <3",
        date=datetime.strptime("2020-11-03 20:16:58.027", DATETIME_PATTERN),
        thread=7,
        for_deleted=False,
        from_deleted=False,
    )
    message_11 = Message(
        id=22,
        from_id=4,
        for_id=1,
        text="test",
        date=datetime.strptime("2020-07-06 17:40:51.288", DATETIME_PATTERN),
        thread=3,
        for_deleted=False,
        from_deleted=False,
    )
    message_12 = Message(
        id=26,
        from_id=20,
        for_id=1,
        text="hiiii :)",
        date=datetime.strptime("2020-11-03 20:21:30.972", DATETIME_PATTERN),
        thread=8,
        for_deleted=True,
        from_deleted=False,
    )
    message_13 = Message(
        id=23,
        from_id=4,
        for_id=5,
        text="testing thread delete",
        date=datetime.strptime("2020-11-03 16:38:06.351", DATETIME_PATTERN),
        thread=4,
        for_deleted=False,
        from_deleted=True,
    )
    message_14 = Message(
        id=24,
        from_id=4,
        for_id=5,
        text="test",
        date=datetime.strptime("2020-11-03 16:48:33.213", DATETIME_PATTERN),
        thread=4,
        for_deleted=False,
        from_deleted=True,
    )

    try:
        db.session.add_all(
            [
                message_1,
                message_2,
                message_3,
                message_4,
                message_5,
                message_6,
                message_7,
                message_8,
                message_9,
                message_10,
                message_11,
                message_12,
                message_13,
                message_14,
            ]
        )
        await db.session.execute(
            text("ALTER SEQUENCE messages_id_seq RESTART WITH 27;")
        )
        await db.session.commit()
    finally:
        await db.session.remove()


async def create_reports(db: SendADatabase):
    """Creates the reports in the test database."""
    report_1 = Report(
        id=1,
        type="Post",
        user_id=1,
        post_id=9,
        reporter=4,
        report_reason="The post is Inappropriate",
        dismissed=True,
        closed=True,
        date=datetime.strptime("2020-06-22 13:38:58.052", DATETIME_PATTERN),
    )
    report_2 = Report(
        id=2,
        type="Post",
        user_id=1,
        post_id=11,
        reporter=4,
        report_reason="The post is Inappropriate",
        dismissed=True,
        closed=True,
        date=datetime.strptime("2020-06-22 14:08:10.401", DATETIME_PATTERN),
    )
    report_3 = Report(
        id=3,
        type="Post",
        user_id=4,
        post_id=None,
        reporter=4,
        report_reason="The post is Inappropriate",
        dismissed=False,
        closed=True,
        date=datetime.strptime("2020-06-22 14:13:25.667", DATETIME_PATTERN),
    )
    report_4 = Report(
        id=4,
        type="Post",
        user_id=4,
        post_id=None,
        reporter=4,
        report_reason="The post is Inappropriate",
        dismissed=False,
        closed=True,
        date=datetime.strptime("2020-06-22 14:30:33.051", DATETIME_PATTERN),
    )
    report_5 = Report(
        id=26,
        type="Post",
        user_id=4,
        post_id=None,
        reporter=4,
        report_reason="The post is Spam",
        dismissed=True,
        closed=True,
        date=datetime.strptime("2020-06-22 20:09:42.139", DATETIME_PATTERN),
    )
    report_6 = Report(
        id=5,
        type="Post",
        user_id=4,
        post_id=None,
        reporter=4,
        report_reason="The post is Inappropriate",
        dismissed=True,
        closed=True,
        date=datetime.strptime("2020-06-22 14:34:46.527", DATETIME_PATTERN),
    )
    report_7 = Report(
        id=6,
        type="User",
        user_id=5,
        post_id=None,
        reporter=4,
        report_reason="The user is posting Spam",
        dismissed=True,
        closed=True,
        date=datetime.strptime("2020-06-22 14:41:30.361", DATETIME_PATTERN),
    )
    report_8 = Report(
        id=7,
        type="User",
        user_id=5,
        post_id=None,
        reporter=4,
        report_reason="The user is posting Spam",
        dismissed=True,
        closed=True,
        date=datetime.strptime("2020-06-22 15:03:27.242", DATETIME_PATTERN),
    )
    report_9 = Report(
        id=8,
        type="Post",
        user_id=1,
        post_id=9,
        reporter=4,
        report_reason="The post is Inappropriate",
        dismissed=True,
        closed=True,
        date=datetime.strptime("2020-06-22 16:27:32.399", DATETIME_PATTERN),
    )
    report_10 = Report(
        id=9,
        type="Post",
        user_id=1,
        post_id=9,
        reporter=4,
        report_reason="The post is Inappropriate",
        dismissed=True,
        closed=True,
        date=datetime.strptime("2020-06-22 16:31:45.47", DATETIME_PATTERN),
    )
    report_11 = Report(
        id=10,
        type="Post",
        user_id=4,
        post_id=None,
        reporter=4,
        report_reason="The post is Inappropriate",
        dismissed=True,
        closed=True,
        date=datetime.strptime("2020-06-22 16:42:40.316", DATETIME_PATTERN),
    )
    report_12 = Report(
        id=11,
        type="Post",
        user_id=4,
        post_id=None,
        reporter=4,
        report_reason="The post is Inappropriate",
        dismissed=True,
        closed=True,
        date=datetime.strptime("2020-06-22 16:44:17.816", DATETIME_PATTERN),
    )
    report_13 = Report(
        id=12,
        type="Post",
        user_id=4,
        post_id=None,
        reporter=4,
        report_reason="The post is Spam",
        dismissed=True,
        closed=True,
        date=datetime.strptime("2020-06-22 19:30:00.082", DATETIME_PATTERN),
    )
    report_14 = Report(
        id=13,
        type="Post",
        user_id=4,
        post_id=None,
        reporter=4,
        report_reason="The post is Inappropriate",
        dismissed=True,
        closed=True,
        date=datetime.strptime("2020-06-22 19:31:40.851", DATETIME_PATTERN),
    )
    report_15 = Report(
        id=14,
        type="Post",
        user_id=4,
        post_id=None,
        reporter=4,
        report_reason="The post is Spam",
        dismissed=True,
        closed=True,
        date=datetime.strptime("2020-06-22 19:32:25.102", DATETIME_PATTERN),
    )
    report_16 = Report(
        id=15,
        type="Post",
        user_id=4,
        post_id=None,
        reporter=4,
        report_reason="The post is Offensive",
        dismissed=True,
        closed=True,
        date=datetime.strptime("2020-06-22 19:53:04.05", DATETIME_PATTERN),
    )
    report_17 = Report(
        id=16,
        type="Post",
        user_id=4,
        post_id=None,
        reporter=4,
        report_reason="The post is Offensive",
        dismissed=True,
        closed=True,
        date=datetime.strptime("2020-06-22 19:54:08.875", DATETIME_PATTERN),
    )
    report_18 = Report(
        id=17,
        type="Post",
        user_id=4,
        post_id=None,
        reporter=4,
        report_reason="The post is Offensive",
        dismissed=True,
        closed=True,
        date=datetime.strptime("2020-06-22 19:55:17.798", DATETIME_PATTERN),
    )
    report_19 = Report(
        id=18,
        type="Post",
        user_id=4,
        post_id=None,
        reporter=4,
        report_reason="The post is Inappropriate",
        dismissed=True,
        closed=True,
        date=datetime.strptime("2020-06-22 19:57:20.996", DATETIME_PATTERN),
    )
    report_20 = Report(
        id=19,
        type="Post",
        user_id=4,
        post_id=None,
        reporter=4,
        report_reason="The post is Inappropriate",
        dismissed=True,
        closed=True,
        date=datetime.strptime("2020-06-22 19:59:34.313", DATETIME_PATTERN),
    )
    report_21 = Report(
        id=20,
        type="Post",
        user_id=4,
        post_id=None,
        reporter=4,
        report_reason="The post is Spam",
        dismissed=True,
        closed=True,
        date=datetime.strptime("2020-06-22 20:00:24.779", DATETIME_PATTERN),
    )
    report_22 = Report(
        id=21,
        type="Post",
        user_id=4,
        post_id=None,
        reporter=4,
        report_reason="The post is Offensive",
        dismissed=True,
        closed=True,
        date=datetime.strptime("2020-06-22 20:03:32.287", DATETIME_PATTERN),
    )
    report_23 = Report(
        id=22,
        type="Post",
        user_id=4,
        post_id=None,
        reporter=4,
        report_reason="The post is Spam",
        dismissed=True,
        closed=True,
        date=datetime.strptime("2020-06-22 20:04:34.395", DATETIME_PATTERN),
    )
    report_24 = Report(
        id=23,
        type="Post",
        user_id=4,
        post_id=None,
        reporter=4,
        report_reason="The post is Spam",
        dismissed=True,
        closed=True,
        date=datetime.strptime("2020-06-22 20:05:31.173", DATETIME_PATTERN),
    )
    report_25 = Report(
        id=24,
        type="Post",
        user_id=4,
        post_id=None,
        reporter=4,
        report_reason="The post is Offensive",
        dismissed=True,
        closed=True,
        date=datetime.strptime("2020-06-22 20:07:16.256", DATETIME_PATTERN),
    )
    report_26 = Report(
        id=25,
        type="Post",
        user_id=4,
        post_id=None,
        reporter=4,
        report_reason="The post is Spam",
        dismissed=True,
        closed=True,
        date=datetime.strptime("2020-06-22 20:08:09.871", DATETIME_PATTERN),
    )
    report_27 = Report(
        id=27,
        type="Post",
        user_id=4,
        post_id=None,
        reporter=4,
        report_reason="The post is Offensive",
        dismissed=False,
        closed=True,
        date=datetime.strptime("2020-06-22 20:10:45.884", DATETIME_PATTERN),
    )
    report_28 = Report(
        id=28,
        type="Post",
        user_id=4,
        post_id=None,
        reporter=4,
        report_reason="The post is Offensive",
        dismissed=False,
        closed=True,
        date=datetime.strptime("2020-06-22 20:11:24.518", DATETIME_PATTERN),
    )
    report_29 = Report(
        id=29,
        type="Post",
        user_id=4,
        post_id=None,
        reporter=4,
        report_reason="The post is Offensive",
        dismissed=False,
        closed=True,
        date=datetime.strptime("2020-06-22 20:13:27.256", DATETIME_PATTERN),
    )
    report_30 = Report(
        id=30,
        type="Post",
        user_id=4,
        post_id=None,
        reporter=4,
        report_reason="The post is Inappropriate",
        dismissed=True,
        closed=True,
        date=datetime.strptime("2020-06-22 20:18:46.182", DATETIME_PATTERN),
    )
    report_31 = Report(
        id=31,
        type="Post",
        user_id=4,
        post_id=None,
        reporter=4,
        report_reason="The post is Offensive",
        dismissed=True,
        closed=True,
        date=datetime.strptime("2020-06-22 20:27:24.199", DATETIME_PATTERN),
    )
    report_32 = Report(
        id=32,
        type="Post",
        user_id=4,
        post_id=None,
        reporter=4,
        report_reason="The post is Offensive",
        dismissed=False,
        closed=True,
        date=datetime.strptime("2020-06-22 20:34:40.16", DATETIME_PATTERN),
    )
    report_33 = Report(
        id=33,
        type="Post",
        user_id=4,
        post_id=None,
        reporter=4,
        report_reason="The post is Offensive",
        dismissed=False,
        closed=True,
        date=datetime.strptime("2020-06-22 20:36:13.622", DATETIME_PATTERN),
    )
    report_34 = Report(
        id=34,
        type="Post",
        user_id=4,
        post_id=None,
        reporter=4,
        report_reason="The post is Spam",
        dismissed=True,
        closed=True,
        date=datetime.strptime("2020-06-22 20:40:57.717", DATETIME_PATTERN),
    )
    report_35 = Report(
        id=35,
        type="User",
        user_id=5,
        post_id=None,
        reporter=4,
        report_reason="The user is posting Spam",
        dismissed=True,
        closed=True,
        date=datetime.strptime("2020-06-22 20:41:47.885", DATETIME_PATTERN),
    )
    report_36 = Report(
        id=36,
        type="Post",
        user_id=4,
        post_id=25,
        reporter=4,
        report_reason="",
        dismissed=True,
        closed=True,
        date=datetime.strptime("2020-07-06 08:14:31.918", DATETIME_PATTERN),
    )
    report_37 = Report(
        id=37,
        type="Post",
        user_id=4,
        post_id=25,
        reporter=4,
        report_reason="The post is Inappropriate",
        dismissed=True,
        closed=True,
        date=datetime.strptime("2020-07-06 10:02:46.046", DATETIME_PATTERN),
    )
    report_38 = Report(
        id=38,
        type="Post",
        user_id=4,
        post_id=25,
        reporter=4,
        report_reason="",
        dismissed=True,
        closed=True,
        date=datetime.strptime("2020-07-06 10:10:34.082", DATETIME_PATTERN),
    )
    report_39 = Report(
        id=41,
        type="Post",
        user_id=4,
        post_id=25,
        reporter=4,
        report_reason="",
        dismissed=True,
        closed=True,
        date=datetime.strptime("2020-07-06 10:17:29.549", DATETIME_PATTERN),
    )
    report_40 = Report(
        id=40,
        type="Post",
        user_id=4,
        post_id=25,
        reporter=4,
        report_reason="",
        dismissed=True,
        closed=True,
        date=datetime.strptime("2020-07-06 10:17:21.702", DATETIME_PATTERN),
    )
    report_41 = Report(
        id=39,
        type="Post",
        user_id=4,
        post_id=25,
        reporter=4,
        report_reason="",
        dismissed=True,
        closed=True,
        date=datetime.strptime("2020-07-06 10:15:07.428", DATETIME_PATTERN),
    )
    report_42 = Report(
        id=42,
        type="Post",
        user_id=4,
        post_id=25,
        reporter=4,
        report_reason="gffdsgfd",
        dismissed=True,
        closed=True,
        date=datetime.strptime("2020-07-06 10:20:37.963", DATETIME_PATTERN),
    )
    report_43 = Report(
        id=43,
        type="Post",
        user_id=4,
        post_id=25,
        reporter=4,
        report_reason="testing",
        dismissed=True,
        closed=True,
        date=datetime.strptime("2020-07-06 10:36:53.98", DATETIME_PATTERN),
    )
    report_44 = Report(
        id=44,
        type="Post",
        user_id=4,
        post_id=28,
        reporter=4,
        report_reason="The post is Inappropriate",
        dismissed=True,
        closed=True,
        date=datetime.strptime("2020-07-13 19:13:48.279", DATETIME_PATTERN),
    )

    try:
        db.session.add_all(
            [
                report_1,
                report_2,
                report_3,
                report_4,
                report_5,
                report_6,
                report_7,
                report_8,
                report_9,
                report_10,
                report_11,
                report_12,
                report_13,
                report_14,
                report_15,
                report_16,
                report_17,
                report_18,
                report_19,
                report_20,
                report_21,
                report_22,
                report_23,
                report_24,
                report_25,
                report_26,
                report_27,
                report_28,
                report_29,
                report_30,
                report_31,
                report_32,
                report_33,
                report_34,
                report_35,
                report_36,
                report_37,
                report_38,
                report_39,
                report_40,
                report_41,
                report_42,
                report_43,
                report_44,
            ]
        )
        await db.session.execute(text("ALTER SEQUENCE reports_id_seq RESTART WITH 45;"))
        await db.session.commit()
    finally:
        await db.session.remove()


async def create_notifications(db: SendADatabase):
    """Creates the notifications in the test database."""
    notification_1 = Notification(
        id=1,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-08 13:05:21.045101", DATETIME_PATTERN),
    )
    notification_2 = Notification(
        id=2,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-08 13:06:14.900956", DATETIME_PATTERN),
    )
    notification_3 = Notification(
        id=3,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-08 13:06:46.626559", DATETIME_PATTERN),
    )
    notification_4 = Notification(
        id=4,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-08 13:14:32.762052", DATETIME_PATTERN),
    )
    notification_5 = Notification(
        id=5,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-08 13:21:54.464433", DATETIME_PATTERN),
    )
    notification_6 = Notification(
        id=6,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-08 18:37:35.118498", DATETIME_PATTERN),
    )
    notification_7 = Notification(
        id=7,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-08 18:42:37.632753", DATETIME_PATTERN),
    )
    notification_41 = Notification(
        id=41,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-14 11:30:07.354089", DATETIME_PATTERN),
    )
    notification_42 = Notification(
        id=42,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-14 11:30:12.560007", DATETIME_PATTERN),
    )
    notification_43 = Notification(
        id=43,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-14 11:55:51.240234", DATETIME_PATTERN),
    )
    notification_46 = Notification(
        id=46,
        for_id=1,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-14 16:00:41.414829", DATETIME_PATTERN),
    )
    notification_53 = Notification(
        id=53,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-20 17:32:19.808169", DATETIME_PATTERN),
    )
    notification_54 = Notification(
        id=54,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-21 14:35:20.297422", DATETIME_PATTERN),
    )
    notification_55 = Notification(
        id=55,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-21 14:35:34.933279", DATETIME_PATTERN),
    )
    notification_58 = Notification(
        id=58,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-22 11:38:02.864273", DATETIME_PATTERN),
    )
    notification_63 = Notification(
        id=63,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-22 12:18:54.286811", DATETIME_PATTERN),
    )
    notification_66 = Notification(
        id=66,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-22 12:23:21.062704", DATETIME_PATTERN),
    )
    notification_70 = Notification(
        id=70,
        for_id=1,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-22 13:40:25.495938", DATETIME_PATTERN),
    )
    notification_71 = Notification(
        id=71,
        for_id=1,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-22 13:41:51.227895", DATETIME_PATTERN),
    )
    notification_72 = Notification(
        id=72,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-22 13:42:35.797629", DATETIME_PATTERN),
    )
    notification_73 = Notification(
        id=73,
        for_id=5,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-22 13:42:40.059274", DATETIME_PATTERN),
    )
    notification_74 = Notification(
        id=74,
        for_id=1,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-22 13:42:44.75568", DATETIME_PATTERN),
    )
    notification_75 = Notification(
        id=75,
        for_id=1,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-22 14:09:01.457204", DATETIME_PATTERN),
    )
    notification_76 = Notification(
        id=76,
        for_id=1,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-22 15:01:45.393836", DATETIME_PATTERN),
    )
    notification_77 = Notification(
        id=77,
        for_id=1,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-22 15:09:58.206196", DATETIME_PATTERN),
    )
    notification_78 = Notification(
        id=78,
        for_id=1,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-22 15:18:49.469451", DATETIME_PATTERN),
    )
    notification_79 = Notification(
        id=79,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-22 15:30:06.395028", DATETIME_PATTERN),
    )
    notification_80 = Notification(
        id=80,
        for_id=5,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-08-10 19:40:21.244178", DATETIME_PATTERN),
    )
    notification_81 = Notification(
        id=81,
        for_id=1,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-09-16 11:08:35.311236", DATETIME_PATTERN),
    )
    notification_82 = Notification(
        id=82,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-10-30 13:36:31.188385", DATETIME_PATTERN),
    )
    notification_83 = Notification(
        id=83,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-10-31 14:01:09.923613", DATETIME_PATTERN),
    )
    notification_84 = Notification(
        id=84,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-10-31 14:19:46.89522", DATETIME_PATTERN),
    )
    notification_85 = Notification(
        id=85,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-10-31 14:26:04.690362", DATETIME_PATTERN),
    )
    notification_86 = Notification(
        id=86,
        for_id=1,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-10-31 14:44:07.598229", DATETIME_PATTERN),
    )
    notification_87 = Notification(
        id=87,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-10-31 14:46:21.747038", DATETIME_PATTERN),
    )
    notification_88 = Notification(
        id=88,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-10-31 14:59:11.313138", DATETIME_PATTERN),
    )
    notification_89 = Notification(
        id=89,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-10-31 15:06:12.339448", DATETIME_PATTERN),
    )
    notification_90 = Notification(
        id=90,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-10-31 15:07:41.99315", DATETIME_PATTERN),
    )
    notification_91 = Notification(
        id=91,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-10-31 15:09:55.344578", DATETIME_PATTERN),
    )
    notification_92 = Notification(
        id=92,
        for_id=5,
        from_id=4,
        type="message",
        text="You have a new message",
        date=datetime.strptime("2020-11-03 16:38:06.351", DATETIME_PATTERN),
    )
    notification_93 = Notification(
        id=93,
        for_id=5,
        from_id=4,
        type="message",
        text="You have a new message",
        date=datetime.strptime("2020-11-03 16:48:33.213", DATETIME_PATTERN),
    )
    notification_94 = Notification(
        id=94,
        for_id=4,
        from_id=20,
        type="message",
        text="You have a new message",
        date=datetime.strptime("2020-11-03 20:16:58.027", DATETIME_PATTERN),
    )
    notification_95 = Notification(
        id=95,
        for_id=1,
        from_id=20,
        type="message",
        text="You have a new message",
        date=datetime.strptime("2020-11-03 20:21:30.972", DATETIME_PATTERN),
    )

    try:
        db.session.add_all(
            [
                notification_1,
                notification_2,
                notification_3,
                notification_4,
                notification_5,
                notification_6,
                notification_7,
                notification_41,
                notification_42,
                notification_43,
                notification_46,
                notification_53,
                notification_54,
                notification_55,
                notification_58,
                notification_63,
                notification_66,
                notification_70,
                notification_71,
                notification_72,
                notification_73,
                notification_74,
                notification_75,
                notification_76,
                notification_77,
                notification_78,
                notification_79,
                notification_80,
                notification_81,
                notification_82,
                notification_83,
                notification_84,
                notification_85,
                notification_86,
                notification_87,
                notification_88,
                notification_89,
                notification_90,
                notification_91,
                notification_92,
                notification_93,
                notification_94,
                notification_95,
            ]
        )
        await db.session.execute(
            text("ALTER SEQUENCE notifications_id_seq RESTART WITH 96;")
        )
        await db.session.commit()
    finally:
        await db.session.remove()


async def create_subscriptions(db: SendADatabase):
    """Creates the push subscriptions in the database"""
    sub_1 = NotificationSub(
        id=1,
        user=1,
        endpoint="https://fcm.googleapis.com/fcm/send/epyhl2GD",
        subscription_data=json.dumps(
            {
                "endpoint": "https://fcm.googleapis.com/fcm/send/epyhl2GD",
                "expirationTime": None,
                "keys": {"p256dh": "fdsfd", "auth": "dfs"},
            }
        ),
    )
    sub_2 = NotificationSub(
        id=2,
        user=5,
        endpoint="https://fcm.googleapis.com/fcm/send/epyhl2GD",
        subscription_data=json.dumps(
            {
                "endpoint": "https://fcm.googleapis.com/fcm/send/epyhl2GD",
                "expirationTime": None,
                "keys": {"p256dh": "fdsfd", "auth": "dfs"},
            }
        ),
    )
    sub_3 = NotificationSub(
        id=3,
        user=4,
        endpoint="https://fcm.googleapis.com/fcm/send/epyhl2GD",
        subscription_data=json.dumps(
            {
                "endpoint": "https://fcm.googleapis.com/fcm/send/epyhl2GD",
                "expirationTime": None,
                "keys": {"p256dh": "fdsfd", "auth": "dfs"},
            }
        ),
    )

    try:
        db.session.add_all([sub_1, sub_2, sub_3])
        await db.session.execute(
            text("ALTER SEQUENCE subscriptions_id_seq RESTART WITH 4;")
        )
        await db.session.commit()
    finally:
        await db.session.close()


async def update_sequences(db: SendADatabase):
    """Updates the values of all sequences."""
    try:
        await db.session.execute(
            text("ALTER SEQUENCE permissions_id_seq RESTART WITH 16;")
        )
        await db.session.execute(text("ALTER SEQUENCE filters_id_seq RESTART WITH 3;"))
        await db.session.execute(text("ALTER SEQUENCE roles_id_seq RESTART WITH 6;"))
        await db.session.execute(text("ALTER SEQUENCE users_id_seq RESTART WITH 21;"))
        await db.session.execute(text("ALTER SEQUENCE posts_id_seq RESTART WITH 46;"))
        await db.session.execute(
            text("ALTER SEQUENCE messages_id_seq RESTART WITH 27;")
        )
        await db.session.execute(text("ALTER SEQUENCE threads_id_seq RESTART WITH 9;"))
        await db.session.execute(text("ALTER SEQUENCE reports_id_seq RESTART WITH 45;"))
        await db.session.execute(
            text("ALTER SEQUENCE notifications_id_seq RESTART WITH 96;")
        )
        await db.session.execute(
            text("ALTER SEQUENCE subscriptions_id_seq RESTART WITH 4;")
        )
        await db.session.commit()
    finally:
        await db.session.close()


async def create_data(db: SendADatabase):
    """Creates the data in the test database."""
    await create_filters(db)
    await create_permissions(db)
    await create_roles(db)
    await create_users(db)
    await create_posts(db)
    await create_threads(db)
    await create_messages(db)
    await create_reports(db)
    await create_notifications(db)
    await create_subscriptions(db)

    await db.session.remove()
