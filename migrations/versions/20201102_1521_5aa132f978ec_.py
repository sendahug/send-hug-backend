"""empty message

Revision ID: 5aa132f978ec
Revises: 97ebcd9c039d
Create Date: 2020-11-02 15:21:17.251397

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "5aa132f978ec"
down_revision = "97ebcd9c039d"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "filters",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("filter", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("filters")
    # ### end Alembic commands ###
