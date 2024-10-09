"""empty message

Revision ID: 8e2b04523898
Revises: 8c92b636cfca
Create Date: 2020-06-21 18:32:24.971199

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "8e2b04523898"
down_revision = "8c92b636cfca"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("users", sa.Column("blocked", sa.Boolean(), nullable=True))
    op.execute("UPDATE users SET blocked = false;")
    op.alter_column("users", "blocked", nullable=False)
    op.add_column("users", sa.Column("releaseDate", sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("users", "releaseDate")
    op.drop_column("users", "blocked")
    # ### end Alembic commands ###
