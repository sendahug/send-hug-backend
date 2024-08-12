from datetime import datetime
from typing import Any

from quart import Blueprint, Response, abort, jsonify, request
from sqlalchemy import false, select

from auth import UserData, requires_auth
from config import sah_config

from .common import DATETIME_PATTERN, validator
from models import Post, Report, User

reports_endpoints = Blueprint("posts", __name__)


# Endpoint: GET /reports
# Description: Gets the currently open reports.
# Parameters: None.
# Authorization: read:admin-board.
@reports_endpoints.route("/reports")
@requires_auth(sah_config, ["read:admin-board"])
async def get_open_reports(token_payload: UserData) -> Response:
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
@reports_endpoints.route("/reports", methods=["POST"])
@requires_auth(sah_config, ["post:report"])
async def create_new_report(token_payload: UserData) -> Response:
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
@reports_endpoints.route("/reports/<report_id>", methods=["PATCH"])
@requires_auth(sah_config, ["read:admin-board"])
async def update_report_status(token_payload: UserData, report_id: int) -> Response:
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
