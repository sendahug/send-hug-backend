"""empty message

Revision ID: fbd822a8ecd6
Revises: e05f567d5754
Create Date: 2020-05-26 20:06:30.485049

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "fbd822a8ecd6"
down_revision = "e05f567d5754"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("users", sa.Column("display_name", sa.String(), nullable=False))
    op.drop_column("users", "username")
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "users",
        sa.Column("username", sa.VARCHAR(), autoincrement=False, nullable=False),
    )
    op.drop_column("users", "display_name")
    # ### end Alembic commands ###
