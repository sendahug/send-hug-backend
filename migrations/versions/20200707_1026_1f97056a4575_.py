"""empty message

Revision ID: 1f97056a4575
Revises: eee3f01a8ec9
Create Date: 2020-07-07 10:26:20.001913

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "1f97056a4575"
down_revision = "eee3f01a8ec9"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "hugs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("for_id", sa.Integer(), nullable=False),
        sa.Column("from_id", sa.Integer(), nullable=False),
        sa.Column("date", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["for_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["from_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("hugs")
    # ### end Alembic commands ###
