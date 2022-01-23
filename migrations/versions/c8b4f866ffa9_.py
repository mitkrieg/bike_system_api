"""empty message

Revision ID: c8b4f866ffa9
Revises: f433615a043a
Create Date: 2022-01-23 00:04:52.899158

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c8b4f866ffa9'
down_revision = 'f433615a043a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('trips', 'origination_station_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('trips', 'origination_station_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    # ### end Alembic commands ###