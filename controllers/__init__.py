from quart import Blueprint

from .posts import posts_endpoints
from .root import root_endpoints

routers: list[Blueprint] = [root_endpoints, posts_endpoints]
