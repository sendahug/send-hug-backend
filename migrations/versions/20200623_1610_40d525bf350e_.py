"""empty message

Revision ID: 40d525bf350e
Revises: 1249cc3ed069
Create Date: 2020-06-23 16:10:53.777812

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "40d525bf350e"
down_revision = "1249cc3ed069"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("messages", sa.Column("user_1_deleted", sa.Boolean(), nullable=True))
    op.execute("UPDATE messages SET user_1_deleted = false;")
    op.alter_column("messages", "user_1_deleted", nullable=False)
    op.add_column("messages", sa.Column("user_2_deleted", sa.Boolean(), nullable=True))
    op.execute("UPDATE messages SET user_2_deleted = false;")
    op.alter_column("messages", "user_2_deleted", nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("messages", "user_2_deleted")
    op.drop_column("messages", "user_1_deleted")
    # ### end Alembic commands ###
