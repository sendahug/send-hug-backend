import asyncio
from logging.config import fileConfig
from logging import getLogger

# from sqlalchemy import pool
from sqlalchemy.engine import Connection

# from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

from models.models import BaseModel
from app import config as app_config

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
alembic_config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if alembic_config.config_file_name is not None:
    fileConfig(alembic_config.config_file_name)

logger = getLogger("alembic.env")

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
alembic_config.set_main_option(
    "sqlalchemy.url",
    app_config.database_url.render_as_string(hide_password=False).replace("%", "%%"),
)
target_metadata = BaseModel.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = alembic_config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # this callback is used to prevent an auto-migration from being generated
    # when there are no changes to the schema
    # reference: http://alembic.zzzcomputing.com/en/latest/cookbook.html
    # TODO: Figure out why this doesn't work
    # def process_revision_directives(
    #     context: MigrationContext,
    #     revision: str | Iterable[str | None] | Iterable[str],
    #     directives: list[MigrationScript],
    # ):
    #     assert alembic_config.cmd_opts is not None
    #     if getattr(alembic_config.cmd_opts, 'autogenerate', False):
    #         script = directives[0]
    #         assert script.upgrade_ops is not None
    #         if script.upgrade_ops.is_empty():
    #             directives[:] = []

    connectable = app_config.db.engine
    # TODO: figure out why below doesn't work
    # connectable = async_engine_from_config(
    #     alembic_config.get_section(alembic_config.config_ini_section, {}),
    #     prefix="sqlalchemy.",
    #     poolclass=pool.NullPool,
    #     # process_revision_directives=process_revision_directives
    # )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
