import json

from quart import Blueprint, Response, abort, jsonify, request
from sqlalchemy import select

from auth import UserData, requires_auth
from config import sah_config

from .common import validator
from models import Filter

filters_endpoints = Blueprint("filters", __name__)


# Endpoint: GET /filters
# Description: Get a paginated list of filtered words.
# Parameters: None.
# Authorization: read:admin-board.
@filters_endpoints.route("/filters")
@requires_auth(sah_config, ["read:admin-board"])
async def get_filters(token_payload: UserData) -> Response:
    page = request.args.get("page", 1, type=int)
    words_per_page = 10
    filtered_words = await sah_config.db.paginate(
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
@filters_endpoints.route("/filters", methods=["POST"])
@requires_auth(sah_config, ["read:admin-board"])
async def add_filter(token_payload: UserData) -> Response:
    new_filter = json.loads(await request.data)["word"]

    # Check if the filter is empty; if it is, abort
    validator.check_length(new_filter, "Phrase to filter")

    # If the word already exists in the filters list, abort
    existing_filter: Filter | None = await sah_config.db.session.scalar(
        select(Filter).filter(Filter.filter == new_filter.lower())
    )

    if existing_filter:
        abort(409)

    # Try to add the word to the filters list
    filter = Filter(filter=new_filter.lower())

    added = await sah_config.db.add_object(filter)

    return jsonify({"success": True, "added": added})


# Endpoint: DELETE /filters/<filter_id>
# Description: Delete a word from the filtered words list.
# Parameters: filter_id - the index of the word to delete.
# Authorization: read:admin-board.
@filters_endpoints.route("/filters/<filter_id>", methods=["DELETE"])
@requires_auth(sah_config, ["read:admin-board"])
async def delete_filter(token_payload: UserData, filter_id: int) -> Response:
    validator.check_type(filter_id, "Filter ID")

    # If there's no word in that index
    to_delete: Filter = await sah_config.db.one_or_404(
        item_id=int(filter_id),
        item_type=Filter,
    )

    # Otherwise, try to delete it
    removed = to_delete.format()
    await sah_config.db.delete_object(to_delete)

    return jsonify({"success": True, "deleted": removed})
