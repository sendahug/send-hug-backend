from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

from models.models import Post, User, Message, Thread, Report, Notification, Filter


DATETIME_PATTERN = "%Y-%m-%d %H:%M:%S.%f"


def create_filters(db: SQLAlchemy):
    filter_1 = Filter(id=1, filter="filtered_word_1")  # type: ignore
    filter_2 = Filter(id=2, filter="filtered_word_2")  # type: ignore

    try:
        db.session.add_all([filter_1, filter_2])
        db.session.execute(text("ALTER SEQUENCE filters_id_seq RESTART WITH 3;"))
        db.session.commit()
    finally:
        db.session.close()


def create_users(db: SQLAlchemy):
    user_1 = User(
        id=1,
        auth0_id="auth0|5ed34765f0b8e60c8e87ca62",
        received_hugs=12,
        given_hugs=2,
        display_name="shirb",
        login_count=60,
        role="admin",
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
    )  # type: ignore
    user_2 = User(
        id=4,
        auth0_id="auth0|5ed8e3d0def75d0befbc7e50",
        received_hugs=106,
        given_hugs=117,
        display_name="user14",
        login_count=55,
        role="admin",
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
    )  # type: ignore
    user_3 = User(
        id=5,
        auth0_id="auth0|5ede3e7a0793080013259050",
        received_hugs=2,
        given_hugs=0,
        display_name="user52",
        login_count=7,
        role="moderator",
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
    )  # type: ignore
    user_4 = User(
        id=9,
        auth0_id="auth0|5edf7b060793080013276746",
        received_hugs=0,
        given_hugs=1,
        display_name="user93",
        login_count=2,
        role="admin",
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
    )  # type: ignore
    user_5 = User(
        id=20,
        auth0_id="auth0|5f4b9fd9915cd400670f4633",
        received_hugs=0,
        given_hugs=0,
        display_name="user24",
        login_count=4,
        role="user",
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
    )  # type: ignore

    try:
        db.session.add_all([user_1, user_2, user_3, user_4, user_5])
        db.session.execute(text("ALTER SEQUENCE users_id_seq RESTART WITH 21;"))
        db.session.commit()
    finally:
        db.session.close()


def create_posts(db: SQLAlchemy):
    post_1 = Post(
        id=1,
        user_id=1,
        text="test",
        date=datetime.strptime("2020-06-01 15:05:01.966", DATETIME_PATTERN),
        given_hugs=2,
        open_report=False,
        sent_hugs=[4],
    )  # type: ignore
    post_2 = Post(
        id=2,
        user_id=1,
        text="test",
        date=datetime.strptime("2020-06-01 15:10:59.898", DATETIME_PATTERN),
        given_hugs=2,
        open_report=False,
        sent_hugs=[4],
    )  # type: ignore
    post_3 = Post(
        id=4,
        user_id=1,
        text="test",
        date=datetime.strptime("2020-06-01 15:17:56.294", DATETIME_PATTERN),
        given_hugs=2,
        open_report=False,
        sent_hugs=[4],
    )  # type: ignore
    post_4 = Post(
        id=6,
        user_id=1,
        text="testing",
        date=datetime.strptime("2020-06-01 15:19:41.25", DATETIME_PATTERN),
        given_hugs=1,
        open_report=False,
        sent_hugs=[4],
    )  # type: ignore
    post_5 = Post(
        id=7,
        user_id=1,
        text="testing #2",
        date=datetime.strptime("2020-06-01 15:20:11.927", DATETIME_PATTERN),
        given_hugs=1,
        open_report=False,
        sent_hugs=[4],
    )  # type: ignore
    post_6 = Post(
        id=9,
        user_id=1,
        text="leeeeeee b :))",
        date=datetime.strptime("2020-06-03 07:11:40.421", DATETIME_PATTERN),
        given_hugs=1,
        open_report=False,
        sent_hugs=[4],
    )  # type: ignore
    post_7 = Post(
        id=10,
        user_id=1,
        text="cutie baby lee",
        date=datetime.strptime("2020-06-04 07:56:09.791", DATETIME_PATTERN),
        given_hugs=1,
        open_report=False,
        sent_hugs=[4],
    )  # type: ignore
    post_8 = Post(
        id=11,
        user_id=1,
        text="baby lee :))",
        date=datetime.strptime("2020-06-04 08:15:50.811", DATETIME_PATTERN),
        given_hugs=2,
        open_report=False,
        sent_hugs=[4],
    )  # type: ignore
    post_9 = Post(
        id=12,
        user_id=5,
        text="new user",
        date=datetime.strptime("2020-06-08 14:07:25.297", DATETIME_PATTERN),
        given_hugs=1,
        open_report=False,
        sent_hugs=[4],
    )  # type: ignore
    post_10 = Post(
        id=13,
        user_id=5,
        text="2nd post",
        date=datetime.strptime("2020-06-08 14:30:58.88", DATETIME_PATTERN),
        given_hugs=1,
        open_report=False,
        sent_hugs=[4],
    )  # type: ignore
    post_11 = Post(
        id=22,
        user_id=4,
        text="testing service worker",
        date=datetime.strptime("2020-06-27 10:31:24.915", DATETIME_PATTERN),
        given_hugs=1,
        open_report=False,
        sent_hugs=[4],
    )  # type: ignore
    post_12 = Post(
        id=23,
        user_id=4,
        text="post",
        date=datetime.strptime("2020-06-27 19:17:31.072", DATETIME_PATTERN),
        given_hugs=2,
        open_report=False,
        sent_hugs=[4],
    )  # type: ignore
    post_13 = Post(
        id=25,
        user_id=4,
        text="for report",
        date=datetime.strptime("2020-07-06 08:02:02.184", DATETIME_PATTERN),
        given_hugs=67,
        open_report=False,
        sent_hugs=[4],
    )  # type: ignore
    post_14 = Post(
        id=26,
        user_id=4,
        text="testing new design",
        date=datetime.strptime("2020-07-13 18:40:34.806", DATETIME_PATTERN),
        given_hugs=1,
        open_report=False,
        sent_hugs=[4],
    )  # type: ignore
    post_15 = Post(
        id=28,
        user_id=4,
        text="testing2",
        date=datetime.strptime("2020-07-13 18:43:51.255", DATETIME_PATTERN),
        given_hugs=9,
        open_report=False,
        sent_hugs=[4],
    )  # type: ignore
    post_16 = Post(
        id=30,
        user_id=4,
        text="hello :)",
        date=datetime.strptime("2020-07-18 12:11:39.65", DATETIME_PATTERN),
        given_hugs=24,
        open_report=False,
        sent_hugs=[4],
    )  # type: ignore
    post_17 = Post(
        id=35,
        user_id=4,
        text="testing new rule",
        date=datetime.strptime("2020-10-24 12:19:24.199", DATETIME_PATTERN),
        given_hugs=1,
        open_report=False,
        sent_hugs=[4],
    )  # type: ignore
    post_18 = Post(
        id=36,
        user_id=4,
        text="post",
        date=datetime.strptime("2020-10-31 14:00:58.851", DATETIME_PATTERN),
        given_hugs=1,
        open_report=False,
        sent_hugs=[4],
    )  # type: ignore
    post_19 = Post(
        id=38,
        user_id=4,
        text="test",
        date=datetime.strptime("2020-10-31 14:46:11.378", DATETIME_PATTERN),
        given_hugs=1,
        open_report=False,
        sent_hugs=[4],
    )  # type: ignore
    post_20 = Post(
        id=39,
        user_id=4,
        text="testing",
        date=datetime.strptime("2020-10-31 14:59:05.703", DATETIME_PATTERN),
        given_hugs=1,
        open_report=False,
        sent_hugs=[4],
    )  # type: ignore
    post_21 = Post(
        id=42,
        user_id=4,
        text="test 2",
        date=datetime.strptime("2020-10-31 15:09:50.26", DATETIME_PATTERN),
        given_hugs=1,
        open_report=False,
        sent_hugs=[4],
    )  # type: ignore
    post_22 = Post(
        id=43,
        user_id=4,
        text="test button",
        date=datetime.strptime("2020-10-31 15:20:45.636", DATETIME_PATTERN),
        given_hugs=0,
        open_report=False,
        sent_hugs=[],
    )  # type: ignore
    post_23 = Post(
        id=44,
        user_id=4,
        text="button",
        date=datetime.strptime("2020-10-31 15:25:18.172", DATETIME_PATTERN),
        given_hugs=0,
        open_report=False,
        sent_hugs=[],
    )  # type: ignore
    post_24 = Post(
        id=45,
        user_id=4,
        text="button 2",
        date=datetime.strptime("2020-10-31 15:26:48.043", DATETIME_PATTERN),
        given_hugs=0,
        open_report=False,
        sent_hugs=[],
    )  # type: ignore

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
        db.session.execute(text("ALTER SEQUENCE posts_id_seq RESTART WITH 46;"))
        db.session.commit()
    finally:
        db.session.close()


def create_threads(db: SQLAlchemy):
    thread_1 = Thread(
        id=1, user_1_id=1, user_2_id=1, user_1_deleted=False, user_2_deleted=False
    )  # type: ignore
    thread_2 = Thread(
        id=2, user_1_id=1, user_2_id=5, user_1_deleted=False, user_2_deleted=False
    )  # type: ignore
    thread_3 = Thread(
        id=3, user_1_id=1, user_2_id=4, user_1_deleted=False, user_2_deleted=False
    )  # type: ignore
    thread_4 = Thread(
        id=6, user_1_id=9, user_2_id=5, user_1_deleted=False, user_2_deleted=False
    )  # type: ignore
    thread_5 = Thread(
        id=7, user_1_id=20, user_2_id=4, user_1_deleted=False, user_2_deleted=False
    )  # type: ignore
    thread_6 = Thread(
        id=8, user_1_id=20, user_2_id=1, user_1_deleted=True, user_2_deleted=False
    )  # type: ignore
    thread_7 = Thread(
        id=4, user_1_id=4, user_2_id=5, user_1_deleted=True, user_2_deleted=False
    )  # type: ignore

    try:
        db.session.add_all(
            [thread_1, thread_2, thread_3, thread_4, thread_5, thread_6, thread_7]
        )
        db.session.execute(text("ALTER SEQUENCE threads_id_seq RESTART WITH 9;"))
        db.session.commit()
    finally:
        db.session.close()


def create_messages(db: SQLAlchemy):
    message_1 = Message(
        id=5,
        from_id=4,
        for_id=5,
        text="hellllllllo :)",
        date=datetime.strptime("2020-06-08 14:43:30.593", DATETIME_PATTERN),
        thread=4,
        for_deleted=False,
        from_deleted=True,
    )  # type: ignore
    message_2 = Message(
        id=8,
        from_id=5,
        for_id=4,
        text="hi there :)",
        date=datetime.strptime("2020-06-08 14:50:19.006", DATETIME_PATTERN),
        thread=4,
        for_deleted=False,
        from_deleted=True,
    )  # type: ignore
    message_3 = Message(
        id=1,
        from_id=1,
        for_id=1,
        text="hang in there :)",
        date=datetime.strptime("2020-06-02 10:39:56.337", DATETIME_PATTERN),
        thread=1,
        for_deleted=False,
        from_deleted=False,
    )  # type: ignore
    message_4 = Message(
        id=3,
        from_id=5,
        for_id=1,
        text="you'll be okay <3",
        date=datetime.strptime("2020-06-08 14:42:02.759", DATETIME_PATTERN),
        thread=2,
        for_deleted=False,
        from_deleted=False,
    )  # type: ignore
    message_5 = Message(
        id=7,
        from_id=1,
        for_id=5,
        text="more testing",
        date=datetime.strptime("2020-06-08 14:45:05.713", DATETIME_PATTERN),
        thread=2,
        for_deleted=False,
        from_deleted=False,
    )  # type: ignore
    message_6 = Message(
        id=9,
        from_id=4,
        for_id=1,
        text="hang in there",
        date=datetime.strptime("2020-06-08 14:43:15.000", DATETIME_PATTERN),
        thread=3,
        for_deleted=False,
        from_deleted=False,
    )  # type: ignore
    message_7 = Message(
        id=16,
        from_id=9,
        for_id=5,
        text="hiiiii",
        date=datetime.strptime("2020-06-14 14:25:37.569", DATETIME_PATTERN),
        thread=6,
        for_deleted=False,
        from_deleted=False,
    )  # type: ignore
    message_8 = Message(
        id=10,
        from_id=4,
        for_id=1,
        text="hi :)",
        date=datetime.strptime("2020-06-14 14:07:37.49", DATETIME_PATTERN),
        thread=3,
        for_deleted=True,
        from_deleted=False,
    )  # type: ignore
    message_9 = Message(
        id=21,
        from_id=4,
        for_id=1,
        text="hi",
        date=datetime.strptime("2020-07-06 17:33:55.712", DATETIME_PATTERN),
        thread=3,
        for_deleted=False,
        from_deleted=False,
    )  # type: ignore
    message_10 = Message(
        id=25,
        from_id=20,
        for_id=4,
        text="hang in there <3",
        date=datetime.strptime("2020-11-03 20:16:58.027", DATETIME_PATTERN),
        thread=7,
        for_deleted=False,
        from_deleted=False,
    )  # type: ignore
    message_11 = Message(
        id=22,
        from_id=4,
        for_id=1,
        text="test",
        date=datetime.strptime("2020-07-06 17:40:51.288", DATETIME_PATTERN),
        thread=3,
        for_deleted=False,
        from_deleted=False,
    )  # type: ignore
    message_12 = Message(
        id=26,
        from_id=20,
        for_id=1,
        text="hiiii :)",
        date=datetime.strptime("2020-11-03 20:21:30.972", DATETIME_PATTERN),
        thread=8,
        for_deleted=True,
        from_deleted=False,
    )  # type: ignore
    message_13 = Message(
        id=23,
        from_id=4,
        for_id=5,
        text="testing thread delete",
        date=datetime.strptime("2020-11-03 16:38:06.351", DATETIME_PATTERN),
        thread=4,
        for_deleted=False,
        from_deleted=True,
    )  # type: ignore
    message_14 = Message(
        id=24,
        from_id=4,
        for_id=5,
        text="test",
        date=datetime.strptime("2020-11-03 16:48:33.213", DATETIME_PATTERN),
        thread=4,
        for_deleted=False,
        from_deleted=True,
    )  # type: ignore

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
        db.session.execute(text("ALTER SEQUENCE messages_id_seq RESTART WITH 27;"))
        db.session.commit()
    finally:
        db.session.close()


def create_reports(db: SQLAlchemy):
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
    )  # type: ignore
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
    )  # type: ignore
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
    )  # type: ignore
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
    )  # type: ignore
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
    )  # type: ignore
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
    )  # type: ignore
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
    )  # type: ignore
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
    )  # type: ignore
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
    )  # type: ignore
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
    )  # type: ignore
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
    )  # type: ignore
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
    )  # type: ignore
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
    )  # type: ignore
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
    )  # type: ignore
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
    )  # type: ignore
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
    )  # type: ignore
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
    )  # type: ignore
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
    )  # type: ignore
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
    )  # type: ignore
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
    )  # type: ignore
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
    )  # type: ignore
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
    )  # type: ignore
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
    )  # type: ignore
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
    )  # type: ignore
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
    )  # type: ignore
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
    )  # type: ignore
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
    )  # type: ignore
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
    )  # type: ignore
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
    )  # type: ignore
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
    )  # type: ignore
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
    )  # type: ignore
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
    )  # type: ignore
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
    )  # type: ignore
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
    )  # type: ignore
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
    )  # type: ignore
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
    )  # type: ignore
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
    )  # type: ignore
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
    )  # type: ignore
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
    )  # type: ignore
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
    )  # type: ignore
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
    )  # type: ignore
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
    )  # type: ignore
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
    )  # type: ignore
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
    )  # type: ignore

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
        db.session.execute(text("ALTER SEQUENCE reports_id_seq RESTART WITH 45;"))
        db.session.commit()
    finally:
        db.session.close()


def create_notifications(db: SQLAlchemy):
    notification_1 = Notification(
        id=1,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-08 13:05:21.045101", DATETIME_PATTERN),
    )  # type: ignore
    notification_2 = Notification(
        id=2,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-08 13:06:14.900956", DATETIME_PATTERN),
    )  # type: ignore
    notification_3 = Notification(
        id=3,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-08 13:06:46.626559", DATETIME_PATTERN),
    )  # type: ignore
    notification_4 = Notification(
        id=4,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-08 13:14:32.762052", DATETIME_PATTERN),
    )  # type: ignore
    notification_5 = Notification(
        id=5,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-08 13:21:54.464433", DATETIME_PATTERN),
    )  # type: ignore
    notification_6 = Notification(
        id=6,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-08 18:37:35.118498", DATETIME_PATTERN),
    )  # type: ignore
    notification_7 = Notification(
        id=7,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-08 18:42:37.632753", DATETIME_PATTERN),
    )  # type: ignore
    notification_8 = Notification(
        id=8,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-08 18:57:28.370055", DATETIME_PATTERN),
    )  # type: ignore
    notification_9 = Notification(
        id=9,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-08 19:30:17.662651", DATETIME_PATTERN),
    )  # type: ignore
    notification_10 = Notification(
        id=10,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-08 19:34:20.655902", DATETIME_PATTERN),
    )  # type: ignore
    notification_11 = Notification(
        id=11,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-08 20:10:30.903444", DATETIME_PATTERN),
    )  # type: ignore
    notification_12 = Notification(
        id=12,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-08 20:30:46.662853", DATETIME_PATTERN),
    )  # type: ignore
    notification_13 = Notification(
        id=13,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-08 20:53:58.684166", DATETIME_PATTERN),
    )  # type: ignore
    notification_14 = Notification(
        id=14,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-08 21:02:28.006988", DATETIME_PATTERN),
    )  # type: ignore
    notification_15 = Notification(
        id=15,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-08 21:03:53.611889", DATETIME_PATTERN),
    )  # type: ignore
    notification_16 = Notification(
        id=16,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-09 11:55:51.856126", DATETIME_PATTERN),
    )  # type: ignore
    notification_17 = Notification(
        id=17,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-09 12:14:16.781994", DATETIME_PATTERN),
    )  # type: ignore
    notification_18 = Notification(
        id=18,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-09 12:17:19.870488", DATETIME_PATTERN),
    )  # type: ignore
    notification_19 = Notification(
        id=19,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-09 12:20:40.981412", DATETIME_PATTERN),
    )  # type: ignore
    notification_20 = Notification(
        id=20,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-09 13:03:50.612026", DATETIME_PATTERN),
    )  # type: ignore
    notification_21 = Notification(
        id=21,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-09 13:18:52.64558", DATETIME_PATTERN),
    )  # type: ignore
    notification_22 = Notification(
        id=22,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-09 13:22:14.386318", DATETIME_PATTERN),
    )  # type: ignore
    notification_23 = Notification(
        id=23,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-09 13:26:26.147308", DATETIME_PATTERN),
    )  # type: ignore
    notification_24 = Notification(
        id=24,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-09 13:46:58.322147", DATETIME_PATTERN),
    )  # type: ignore
    notification_25 = Notification(
        id=25,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-09 13:49:59.420843", DATETIME_PATTERN),
    )  # type: ignore
    notification_26 = Notification(
        id=26,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-09 13:53:31.563989", DATETIME_PATTERN),
    )  # type: ignore
    notification_27 = Notification(
        id=27,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-09 14:39:37.324127", DATETIME_PATTERN),
    )  # type: ignore
    notification_28 = Notification(
        id=28,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-09 15:57:50.574972", DATETIME_PATTERN),
    )  # type: ignore
    notification_29 = Notification(
        id=29,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-13 16:06:07.646147", DATETIME_PATTERN),
    )  # type: ignore
    notification_31 = Notification(
        id=31,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-13 16:12:23.553046", DATETIME_PATTERN),
    )  # type: ignore
    notification_30 = Notification(
        id=30,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-13 16:09:47.367847", DATETIME_PATTERN),
    )  # type: ignore
    notification_32 = Notification(
        id=32,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-13 16:14:33.286915", DATETIME_PATTERN),
    )  # type: ignore
    notification_33 = Notification(
        id=33,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-13 17:52:00.180463", DATETIME_PATTERN),
    )  # type: ignore
    notification_34 = Notification(
        id=34,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-13 17:52:54.081449", DATETIME_PATTERN),
    )  # type: ignore
    notification_35 = Notification(
        id=35,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-13 21:18:54.994732", DATETIME_PATTERN),
    )  # type: ignore
    notification_36 = Notification(
        id=36,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-13 21:31:14.229423", DATETIME_PATTERN),
    )  # type: ignore
    notification_37 = Notification(
        id=37,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-13 21:32:58.786522", DATETIME_PATTERN),
    )  # type: ignore
    notification_38 = Notification(
        id=38,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-13 21:35:48.566696", DATETIME_PATTERN),
    )  # type: ignore
    notification_39 = Notification(
        id=39,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-13 21:36:02.392095", DATETIME_PATTERN),
    )  # type: ignore
    notification_40 = Notification(
        id=40,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-13 21:36:12.524953", DATETIME_PATTERN),
    )  # type: ignore
    notification_41 = Notification(
        id=41,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-14 11:30:07.354089", DATETIME_PATTERN),
    )  # type: ignore
    notification_42 = Notification(
        id=42,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-14 11:30:12.560007", DATETIME_PATTERN),
    )  # type: ignore
    notification_43 = Notification(
        id=43,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-14 11:55:51.240234", DATETIME_PATTERN),
    )  # type: ignore
    notification_44 = Notification(
        id=44,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-14 13:02:42.709881", DATETIME_PATTERN),
    )  # type: ignore
    notification_45 = Notification(
        id=45,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-14 13:08:21.978572", DATETIME_PATTERN),
    )  # type: ignore
    notification_46 = Notification(
        id=46,
        for_id=1,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-14 16:00:41.414829", DATETIME_PATTERN),
    )  # type: ignore
    notification_47 = Notification(
        id=47,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-14 16:00:48.658501", DATETIME_PATTERN),
    )  # type: ignore
    notification_48 = Notification(
        id=48,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-14 16:00:52.290504", DATETIME_PATTERN),
    )  # type: ignore
    notification_49 = Notification(
        id=49,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-14 16:00:57.635331", DATETIME_PATTERN),
    )  # type: ignore
    notification_50 = Notification(
        id=50,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-20 17:30:57.513678", DATETIME_PATTERN),
    )  # type: ignore
    notification_51 = Notification(
        id=51,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-20 17:31:18.728888", DATETIME_PATTERN),
    )  # type: ignore
    notification_52 = Notification(
        id=52,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-20 17:31:45.554583", DATETIME_PATTERN),
    )  # type: ignore
    notification_53 = Notification(
        id=53,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-20 17:32:19.808169", DATETIME_PATTERN),
    )  # type: ignore
    notification_54 = Notification(
        id=54,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-21 14:35:20.297422", DATETIME_PATTERN),
    )  # type: ignore
    notification_55 = Notification(
        id=55,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-21 14:35:34.933279", DATETIME_PATTERN),
    )  # type: ignore
    notification_56 = Notification(
        id=56,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-21 14:36:00.316687", DATETIME_PATTERN),
    )  # type: ignore
    notification_57 = Notification(
        id=57,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-21 14:36:05.76754", DATETIME_PATTERN),
    )  # type: ignore
    notification_58 = Notification(
        id=58,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-22 11:38:02.864273", DATETIME_PATTERN),
    )  # type: ignore
    notification_59 = Notification(
        id=59,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-22 11:39:45.109452", DATETIME_PATTERN),
    )  # type: ignore
    notification_60 = Notification(
        id=60,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-22 11:45:57.699555", DATETIME_PATTERN),
    )  # type: ignore
    notification_61 = Notification(
        id=61,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-22 11:47:10.258195", DATETIME_PATTERN),
    )  # type: ignore
    notification_62 = Notification(
        id=62,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-22 12:16:14.657724", DATETIME_PATTERN),
    )  # type: ignore
    notification_63 = Notification(
        id=63,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-22 12:18:54.286811", DATETIME_PATTERN),
    )  # type: ignore
    notification_64 = Notification(
        id=64,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-22 12:22:00.067407", DATETIME_PATTERN),
    )  # type: ignore
    notification_65 = Notification(
        id=65,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-22 12:22:54.884349", DATETIME_PATTERN),
    )  # type: ignore
    notification_66 = Notification(
        id=66,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-22 12:23:21.062704", DATETIME_PATTERN),
    )  # type: ignore
    notification_67 = Notification(
        id=67,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-22 12:37:08.019144", DATETIME_PATTERN),
    )  # type: ignore
    notification_68 = Notification(
        id=68,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-22 13:20:59.398594", DATETIME_PATTERN),
    )  # type: ignore
    notification_69 = Notification(
        id=69,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-22 13:36:52.419098", DATETIME_PATTERN),
    )  # type: ignore
    notification_70 = Notification(
        id=70,
        for_id=1,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-22 13:40:25.495938", DATETIME_PATTERN),
    )  # type: ignore
    notification_71 = Notification(
        id=71,
        for_id=1,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-22 13:41:51.227895", DATETIME_PATTERN),
    )  # type: ignore
    notification_72 = Notification(
        id=72,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-22 13:42:35.797629", DATETIME_PATTERN),
    )  # type: ignore
    notification_73 = Notification(
        id=73,
        for_id=5,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-22 13:42:40.059274", DATETIME_PATTERN),
    )  # type: ignore
    notification_74 = Notification(
        id=74,
        for_id=1,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-22 13:42:44.75568", DATETIME_PATTERN),
    )  # type: ignore
    notification_75 = Notification(
        id=75,
        for_id=1,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-22 14:09:01.457204", DATETIME_PATTERN),
    )  # type: ignore
    notification_76 = Notification(
        id=76,
        for_id=1,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-22 15:01:45.393836", DATETIME_PATTERN),
    )  # type: ignore
    notification_77 = Notification(
        id=77,
        for_id=1,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-22 15:09:58.206196", DATETIME_PATTERN),
    )  # type: ignore
    notification_78 = Notification(
        id=78,
        for_id=1,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-22 15:18:49.469451", DATETIME_PATTERN),
    )  # type: ignore
    notification_79 = Notification(
        id=79,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-07-22 15:30:06.395028", DATETIME_PATTERN),
    )  # type: ignore
    notification_80 = Notification(
        id=80,
        for_id=5,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-08-10 19:40:21.244178", DATETIME_PATTERN),
    )  # type: ignore
    notification_81 = Notification(
        id=81,
        for_id=1,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-09-16 11:08:35.311236", DATETIME_PATTERN),
    )  # type: ignore
    notification_82 = Notification(
        id=82,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-10-30 13:36:31.188385", DATETIME_PATTERN),
    )  # type: ignore
    notification_83 = Notification(
        id=83,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-10-31 14:01:09.923613", DATETIME_PATTERN),
    )  # type: ignore
    notification_84 = Notification(
        id=84,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-10-31 14:19:46.89522", DATETIME_PATTERN),
    )  # type: ignore
    notification_85 = Notification(
        id=85,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-10-31 14:26:04.690362", DATETIME_PATTERN),
    )  # type: ignore
    notification_86 = Notification(
        id=86,
        for_id=1,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-10-31 14:44:07.598229", DATETIME_PATTERN),
    )  # type: ignore
    notification_87 = Notification(
        id=87,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-10-31 14:46:21.747038", DATETIME_PATTERN),
    )  # type: ignore
    notification_88 = Notification(
        id=88,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-10-31 14:59:11.313138", DATETIME_PATTERN),
    )  # type: ignore
    notification_89 = Notification(
        id=89,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-10-31 15:06:12.339448", DATETIME_PATTERN),
    )  # type: ignore
    notification_90 = Notification(
        id=90,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-10-31 15:07:41.99315", DATETIME_PATTERN),
    )  # type: ignore
    notification_91 = Notification(
        id=91,
        for_id=4,
        from_id=4,
        type="hug",
        text="You got a hug",
        date=datetime.strptime("2020-10-31 15:09:55.344578", DATETIME_PATTERN),
    )  # type: ignore
    notification_92 = Notification(
        id=92,
        for_id=5,
        from_id=4,
        type="message",
        text="You have a new message",
        date=datetime.strptime("2020-11-03 16:38:06.351", DATETIME_PATTERN),
    )  # type: ignore
    notification_93 = Notification(
        id=93,
        for_id=5,
        from_id=4,
        type="message",
        text="You have a new message",
        date=datetime.strptime("2020-11-03 16:48:33.213", DATETIME_PATTERN),
    )  # type: ignore
    notification_94 = Notification(
        id=94,
        for_id=4,
        from_id=20,
        type="message",
        text="You have a new message",
        date=datetime.strptime("2020-11-03 20:16:58.027", DATETIME_PATTERN),
    )  # type: ignore
    notification_95 = Notification(
        id=95,
        for_id=1,
        from_id=20,
        type="message",
        text="You have a new message",
        date=datetime.strptime("2020-11-03 20:21:30.972", DATETIME_PATTERN),
    )  # type: ignore

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
                notification_8,
                notification_9,
                notification_10,
                notification_11,
                notification_12,
                notification_13,
                notification_14,
                notification_15,
                notification_16,
                notification_17,
                notification_18,
                notification_19,
                notification_20,
                notification_21,
                notification_22,
                notification_23,
                notification_24,
                notification_25,
                notification_26,
                notification_27,
                notification_28,
                notification_29,
                notification_30,
                notification_31,
                notification_32,
                notification_33,
                notification_34,
                notification_35,
                notification_36,
                notification_37,
                notification_38,
                notification_39,
                notification_40,
                notification_41,
                notification_42,
                notification_43,
                notification_44,
                notification_45,
                notification_46,
                notification_47,
                notification_48,
                notification_49,
                notification_50,
                notification_51,
                notification_52,
                notification_53,
                notification_54,
                notification_55,
                notification_56,
                notification_57,
                notification_58,
                notification_59,
                notification_60,
                notification_61,
                notification_62,
                notification_63,
                notification_64,
                notification_65,
                notification_66,
                notification_67,
                notification_68,
                notification_69,
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
        db.session.execute(text("ALTER SEQUENCE notifications_id_seq RESTART WITH 96;"))
        db.session.commit()
    finally:
        db.session.close()


# TODO: Add subscriptions


def create_data(db: SQLAlchemy):
    create_filters(db)
    create_users(db)
    create_posts(db)
    create_threads(db)
    create_messages(db)
    create_reports(db)
    create_notifications(db)
    # create_subscriptions(db)

    db.session.close()
