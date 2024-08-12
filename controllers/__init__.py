from quart import Blueprint

from .filters import filters_endpoints
from .messages import messages_endpoints
from .notifications import notifications_endpoints
from .posts import posts_endpoints
from .reports import reports_endpoints
from .root import root_endpoints

routers: list[Blueprint] = [
    filters_endpoints,
    messages_endpoints,
    notifications_endpoints,
    posts_endpoints,
    reports_endpoints,
    root_endpoints,
]
