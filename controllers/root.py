import json
from typing import Any, Sequence

from quart import Blueprint, Response, jsonify, request
from sqlalchemy import desc, false, select

from config import sah_config

from .common import validator
from models import Post, User

root_endpoints = Blueprint("root", __name__)


# Endpoint: GET /
# Description: Gets recent and suggested posts.
# Parameters: None.
# Authorization: None.
@root_endpoints.route("/")
async def index() -> Response:
    posts: dict[str, list[dict[str, Any]]] = {
        "recent": [],
        "suggested": [],
    }

    for target in posts.keys():
        posts_query = select(Post).filter(Post.open_report == false())

        # Gets the ten most recent posts
        if target == "recent":
            posts_query = posts_query.order_by(desc(Post.date))
        # Gets the ten posts with the least hugs
        else:
            posts_query = posts_query.order_by(Post.given_hugs, Post.date)

        posts_scalars = await sah_config.db.session.scalars(posts_query.limit(10))
        post_instances: Sequence[Post] = posts_scalars.all()

        # formats each post in the list
        posts[target] = [post.format() for post in post_instances]

    return jsonify(
        {
            "success": True,
            "recent": posts["recent"],
            "suggested": posts["suggested"],
        }
    )


# Endpoint: POST /
# Description: Run a search.
# Parameters: None.
# Authorization: None.
@root_endpoints.route("/", methods=["POST"])
async def search() -> Response:
    search_query = json.loads(await request.data)["search"]
    current_page = request.args.get("page", 1, type=int)

    # Check if the search query is empty; if it is, abort
    validator.check_length(search_query, "Search query")
    # Check if the search query isn't a string; if it isn't, abort
    validator.check_type(search_query, "Search query")

    # Get the users with the search query in their display name
    users_scalars = await sah_config.db.session.scalars(
        select(User).filter(User.display_name.ilike(f"%{search_query}%"))
    )
    users: Sequence[User] = users_scalars.all()

    posts = await sah_config.db.paginate(
        select(Post)
        .order_by(desc(Post.date))
        .filter(Post.text.ilike(f"%{search_query}%"))
        .filter(Post.open_report == false()),
        current_page=current_page,
    )

    # Formats the users' data
    formatted_users = [user.format() for user in users]

    return jsonify(
        {
            "success": True,
            "users": formatted_users,
            "posts": posts.resource,
            "user_results": len(users),
            "post_results": posts.total_items,
            "current_page": int(current_page),
            "total_pages": posts.total_pages,
        }
    )
