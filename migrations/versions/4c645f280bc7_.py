"""empty message

Revision ID: 4c645f280bc7
Revises: 09338f19f84f
Create Date: 2021-06-08 08:32:04.522533

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4c645f280bc7'
down_revision = '09338f19f84f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('task', sa.Column('completed_at', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('task', 'completed_at')
    # ### end Alembic commands ###