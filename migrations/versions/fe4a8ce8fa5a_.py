""" add item.note

Revision ID: fe4a8ce8fa5a
Revises: 5e6d3f8f1776
Create Date: 2018-02-17 18:06:27.114488

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fe4a8ce8fa5a'
down_revision = '5e6d3f8f1776'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('item', sa.Column('note', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('item', 'note')
    # ### end Alembic commands ###
