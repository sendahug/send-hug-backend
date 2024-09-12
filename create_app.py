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

import os

from quart import Quart, Response, jsonify
from quart_cors import cors

from auth import AuthError
from config import sah_config
from controllers import routers

from utils.validator import ValidationError


def create_app() -> Quart:
    # create and configure the app
    app = Quart("SendAHug")
    sah_config.db.init_app(app=app)
    sah_config.db.set_default_per_page(per_page=5)
    # Utilities
    cors(app)

    @app.after_request
    def after_request(response: Response):
        # CORS Setup
        response.headers.add(
            "Access-Control-Allow-Origin", str(os.environ.get("FRONTEND"))
        )
        response.headers.add(
            "Access-Control-Allow-Methods",
            "GET, POST, PATCH, DELETE, OPTIONS",
        )
        response.headers.add(
            "Access-Control-Allow-Headers",
            "Authorization, Content-Type",
        )
        # Security Headers, based on
        # https://owasp.org/www-project-secure-headers/index.html#div-bestpractices
        response.headers.add(
            "Strict-Transport-Security", "max-age=31536000; includeSubDomains"
        )
        response.headers.add("X-Frame-Options", "deny")
        response.headers.add("X-Content-Type-Options", "nosniff")
        response.headers.add(
            "Content-Security-Policy",
            (
                "default-src 'self'; form-action 'self'; object-src 'none'; "
                "frame-ancestors 'none'; upgrade-insecure-requests; "
                "block-all-mixed-content"
            ),
        )
        response.headers.add("X-Permitted-Cross-Domain-Policies", "none")
        response.headers.add("Referrer-Policy", "no-referrer")
        response.headers.add("Cross-Origin-Resource-Policy", "same-origin")
        response.headers.add("Cross-Origin-Embedder-Policy", "require-corp")
        response.headers.add("Cross-Origin-Opener-Policy", "same-origin")
        response.headers.add("Cache-Control", "no-store, max-age=0")
        response.headers.add("Pragma", "no-cache")  # HTTP 1.0

        return response

    for router in routers:
        app.register_blueprint(router)

    # Error Handlers
    # -----------------------------------------------------------------
    # Bad request error handler
    @app.errorhandler(400)
    def bad_request(error):
        return (
            jsonify(
                {
                    "success": False,
                    "code": 400,
                    "message": "Bad request. Fix your request and try again.",
                }
            ),
            400,
        )

    # Not found error handler
    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify(
                {
                    "success": False,
                    "code": 404,
                    "message": "The resource you were looking for wasn't found.",
                }
            ),
            404,
        )

    # Method not allowed handler
    @app.errorhandler(405)
    def method_not_allowed(error):
        return (
            jsonify(
                {
                    "success": False,
                    "code": 405,
                    "message": "This HTTP method is not allowed at this endpoint.",
                }
            ),
            405,
        )

    # Conflict error handler
    @app.errorhandler(409)
    def conflict(error):
        return (
            jsonify(
                {
                    "success": False,
                    "code": 409,
                    "message": "Conflict. The resource you were trying to create "
                    "already exists.",
                }
            ),
            409,
        )

    # Unprocessable error handler
    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify(
                {
                    "success": False,
                    "code": 422,
                    "message": f"Unprocessable request. {error.description}",
                }
            ),
            422,
        )

    # Internal server error handler
    @app.errorhandler(500)
    def internal_server_error(error):
        return (
            jsonify(
                {
                    "success": False,
                    "code": 500,
                    "message": "An internal server error occurred. "
                    f"{error.description}",
                }
            ),
            500,
        )

    # Authentication error handler
    @app.errorhandler(AuthError)
    def auth_error(error):
        return (
            jsonify(
                {"success": False, "code": error.status_code, "message": error.error}
            ),
            error.status_code,
        )

    # Validation error handler
    @app.errorhandler(ValidationError)
    def validation_error(error):
        return (
            jsonify(
                {"success": False, "code": error.status_code, "message": error.error}
            ),
            error.status_code,
        )

    return app
