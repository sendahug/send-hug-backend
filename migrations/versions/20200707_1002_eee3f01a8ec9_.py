"""empty message

Revision ID: eee3f01a8ec9
Revises: 26e414955820
Create Date: 2020-07-07 10:02:48.901991

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "eee3f01a8ec9"
down_revision = "26e414955820"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "users", sa.Column("last_notifications_read", sa.DateTime(), nullable=True)
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("users", "last_notifications_read")
    # ### end Alembic commands ###
