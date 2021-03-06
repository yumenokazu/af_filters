""" add category.class_name

Revision ID: 9b34058bea95
Revises: ccf9590ce2e6
Create Date: 2018-01-31 02:18:08.233186

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9b34058bea95'
down_revision = '314e597d5a6e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('category', sa.Column('class_name', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('category', 'class_name')
    # ### end Alembic commands ###
