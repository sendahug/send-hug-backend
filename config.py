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
import os
from pathlib import Path
from typing import TypedDict

from firebase_admin import _apps, get_app, initialize_app  # type: ignore
from firebase_admin.credentials import Certificate  # type: ignore
from sqlalchemy import URL

from models.db import SendADatabase

HOME = Path(os.environ.get("HOME", ""))
SAH_HOME = Path(os.environ.get("SAH_HOME", HOME / "git" / "send-hug-backend"))
SECRETS_PATH = SAH_HOME / ".secrets"
FIREBASE_CREDENTIALS_FILE = Path(
    os.environ.get(
        "FIREBASE_CREDENTIALS_FILE",
        SECRETS_PATH / "platform_firebase_credentials" / "latest.json",
    )
)

# TODO: depcrate the below once we update docs with how to use
# db_development_creds/latest.json for development
DATABASE_USERNAME = os.environ.get("DATABASE_USERNAME", "")
DATABASE_PASSWORD = os.environ.get("DATABASE_PASSWORD", "")


def get_db_credentials_path() -> Path:
    return Path(
        os.environ.get(
            "DB_CREDENTIALS_PATH", SECRETS_PATH / "db_development_creds" / "latest.json"
        )
    )


class DatabaseCredentialsFile(TypedDict):
    username: str
    password: str
    host: str
    port: int | None
    db_name: str


class SAHConfig:
    """
    Configuration class for the Send A Hug backend.
    """

    def __init__(
        self,
        credentials_path: Path,
        override_db_name: str | None = None,
    ):
        credentials = self._get_credentials_json(credentials_path=credentials_path)
        self.database_url = self.get_db_url(
            credentials=credentials, override_db_name=override_db_name
        )
        self.db = SendADatabase(database_url=self.database_url)

        # if self.firebase_app is None:
        if not _apps:
            self.firebase_app = initialize_app(
                credential=Certificate(FIREBASE_CREDENTIALS_FILE)
            )
        else:
            self.firebase_app = get_app()

    def get_db_url(
        self, credentials: DatabaseCredentialsFile, override_db_name: str | None = None
    ):
        """
        Creates the db URL so that SQLAlchemy can establish the connection.

        param credentials: The credentials to use to login to the database
        param override_db_name: The name of the database to use instead of the name
                                in the database credentials.
        """
        return URL.create(
            drivername="postgresql+asyncpg",
            username=credentials["username"],
            password=credentials["password"],
            host=credentials["host"],
            port=credentials.get("port"),
            database=override_db_name or credentials["db_name"],
        )

    def _get_credentials_json(self, credentials_path: Path) -> DatabaseCredentialsFile:
        """
        Fetches the database credentials to construct the db URL.

        param credentials_path: The path to file with the database credentials.
        """
        try:
            with open(credentials_path) as creds_file:
                creds: DatabaseCredentialsFile = json.load(creds_file)

            # For non-local development, we use CloudSQL
            if not creds.get("port"):
                creds["host"] = f"/cloudsql/{creds['host']}"

            return creds

        # If the default file doesn't exist, it means we're in local mode
        # so set the details to localhost
        # TODO: should switch this to some dev creds json file so it follows the same
        # pattern as staging / prod
        except FileNotFoundError:
            return {
                "username": DATABASE_USERNAME,
                "password": DATABASE_PASSWORD,
                "host": "localhost",
                "port": 5432,
                "db_name": "sendahug",
            }


# TODO: should be able to do this with a mock but can't currently get it to work
if os.environ.get("PYTEST_VERSION"):
    sah_config = SAHConfig(
        credentials_path=Path("test.json"), override_db_name="test_sah"
    )
else:
    sah_config = SAHConfig(credentials_path=get_db_credentials_path())
