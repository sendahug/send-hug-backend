"""empty message

Revision ID: 55c97dad811f
Revises: 2cd3e0bd28db
Create Date: 2020-06-21 19:18:16.279625

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "55c97dad811f"
down_revision = "2cd3e0bd28db"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("users", sa.Column("open_report", sa.Boolean(), nullable=True))
    op.execute("UPDATE users SET open_report = false;")
    op.alter_column("users", "open_report", nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("users", "open_report")
    # ### end Alembic commands ###
