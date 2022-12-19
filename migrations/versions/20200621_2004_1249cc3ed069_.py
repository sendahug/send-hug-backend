"""empty message

Revision ID: 1249cc3ed069
Revises: 55c97dad811f
Create Date: 2020-06-21 20:04:37.559092

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "1249cc3ed069"
down_revision = "55c97dad811f"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("users", sa.Column("release_date", sa.DateTime(), nullable=True))
    op.drop_column("users", "releaseDate")
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "users",
        sa.Column(
            "releaseDate", postgresql.TIMESTAMP(), autoincrement=False, nullable=True
        ),
    )
    op.drop_column("users", "release_date")
    # ### end Alembic commands ###
