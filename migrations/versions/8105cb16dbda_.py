""" add affix.af_text

Revision ID: 8105cb16dbda
Revises: fe4a8ce8fa5a
Create Date: 2018-02-23 20:41:25.717404

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8105cb16dbda'
down_revision = 'fe4a8ce8fa5a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('affix', sa.Column('af_text', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('affix', 'af_text')
    # ### end Alembic commands ###
