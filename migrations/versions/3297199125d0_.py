"""empty message

Revision ID: 3297199125d0
Revises: d399e57f790a
Create Date: 2018-02-09 22:20:02.726073

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3297199125d0'
down_revision = 'd399e57f790a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('affix_type', sa.Column('top', sa.String(length=3), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('affix_type', 'top')
    # ### end Alembic commands ###
