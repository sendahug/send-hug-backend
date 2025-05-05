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

import json

import pytest
from pytest_mock import MockerFixture
from pywebpush import WebPushException  # type: ignore
from quart.typing import TestClientProtocol

from config.config import sah_config
from controllers.common import (
    get_current_filters,
    get_thread_id_for_users,
    send_email_notification,
    send_push_notification,
)

from models import NotificationSub
from models.db import SendADatabase
from utils.push_notifications import RawPushData


@pytest.mark.asyncio
async def test_send_email_notification(
    app_client: TestClientProtocol, test_db: SendADatabase, mocker: MockerFixture
) -> None:
    send_email_func = mocker.patch("controllers.common.send_email")

    async with app_client.app.app_context():
        await send_email_notification(
            user_id=1, data=RawPushData(type="message", text="This is a test")
        )

    assert send_email_func.call_args.kwargs == {
        "to": "user1@user1.com",
        "subject": "New message",
        "content": "This is a test\n\nhttp://localhost:3000/messages/inbox",
    }


# send_email_notification auto populates from address, subject and content
# so only real error that can happen is an invalid or missing to email address
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "user_id, data, expected_log_message",
    [
        (
            4,
            RawPushData(type="message", text="This is a test"),
            "Invalid email address: invalid_email",
        ),
        (
            5,
            RawPushData(type="message", text="This is a test"),
            "Missing email address",
        ),
    ],
)
async def test_send_email_notification_errors(
    app_client: TestClientProtocol,
    test_db: SendADatabase,
    user_id: int,
    data: RawPushData,
    expected_log_message: str,
    mocker: MockerFixture,
    caplog: pytest.LogCaptureFixture,
) -> None:
    mocker.patch("utils.email.SG_CLIENT")

    async with app_client.app.app_context():
        caplog.clear()
        await send_email_notification(user_id=user_id, data=data)

    assert expected_log_message in caplog.messages


@pytest.mark.asyncio
async def test_send_push_notification(
    app_client: TestClientProtocol,
    test_db: SendADatabase,
    mocker: MockerFixture,
    monkeypatch: pytest.MonkeyPatch,
):
    user_id = 4
    push_data = RawPushData(type="hug", text="User sent you a hug")
    mock_vapid_key = "KEY"
    mock_push_data = {"data": "data"}
    mock_vapid_claims = {"my": "claim"}
    monkeypatch.setenv("PRIVATE_VAPID_KEY", mock_vapid_key)
    generate_push_data_mock = mocker.patch(
        "controllers.common.generate_push_data", return_value=mock_push_data
    )
    generate_vapid_claims_mock = mocker.patch(
        "controllers.common.generate_vapid_claims", return_value=mock_vapid_claims
    )
    webpush_spy = mocker.patch("controllers.common.webpush")

    push_subscription = await test_db.one_or_404(item_id=3, item_type=NotificationSub)

    await send_push_notification(user_id=user_id, data=push_data)

    webpush_spy.assert_called_once_with(
        subscription_info=json.loads(str(push_subscription.subscription_data)),
        data=json.dumps(mock_push_data),
        vapid_private_key=mock_vapid_key,
        vapid_claims=mock_vapid_claims,
    )
    generate_push_data_mock.assert_called_with(push_data)
    generate_vapid_claims_mock.assert_called_once()


@pytest.mark.asyncio
async def test_send_push_notification_error(
    app_client: TestClientProtocol,
    test_db: SendADatabase,
    mocker: MockerFixture,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
):
    user_id = 4
    push_data = RawPushData(type="hug", text="User sent you a hug")
    mock_vapid_key = "KEY"
    mock_push_data = {"data": "data"}
    mock_vapid_claims = {"my": "claim"}
    mock_error = WebPushException("push_error!")
    monkeypatch.setenv("PRIVATE_VAPID_KEY", mock_vapid_key)
    mocker.patch("controllers.common.generate_push_data", return_value=mock_push_data)
    mocker.patch(
        "controllers.common.generate_vapid_claims", return_value=mock_vapid_claims
    )
    mocker.patch("controllers.common.webpush", side_effect=mock_error)

    async with app_client.app.app_context():
        caplog.clear()
        await send_push_notification(user_id=user_id, data=push_data)

    assert "push_error!" in caplog.messages[0]


@pytest.mark.asyncio
async def test_get_current_filters(test_db: SendADatabase):
    filters_result = await get_current_filters()

    assert filters_result == ["filtered_word_1", "filtered_word_2"]


@pytest.mark.asyncio
async def test_get_thread_id_for_users_no_thread(
    test_db: SendADatabase, mocker: MockerFixture
):
    add_object_spy = mocker.spy(sah_config.db, "add_object")
    thread_id = await get_thread_id_for_users(
        user1_id=5, user2_id=17, current_user_id=5
    )

    assert thread_id >= 9
    add_object_spy.assert_called_once()


@pytest.mark.asyncio
async def test_get_thread_id_for_users_thread_exists(
    test_db: SendADatabase, mocker: MockerFixture
):
    add_object_spy = mocker.spy(sah_config.db, "add_object")
    thread_id = await get_thread_id_for_users(
        user1_id=17, user2_id=4, current_user_id=4
    )

    assert thread_id == 7
    add_object_spy.assert_not_called()
