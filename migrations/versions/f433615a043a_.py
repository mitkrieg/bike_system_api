"""empty message

Revision ID: f433615a043a
Revises: 
Create Date: 2022-01-22 20:36:38.172835

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f433615a043a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('riders',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('address', sa.String(), nullable=False),
    sa.Column('membership', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('stations',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('capacity', sa.Integer(), nullable=False),
    sa.Column('latitude', sa.Float(), nullable=False),
    sa.Column('longitude', sa.Float(), nullable=False),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('bikes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('model', sa.String(), nullable=False),
    sa.Column('manufactured_at', sa.DateTime(), nullable=False),
    sa.Column('electric', sa.Boolean(), nullable=False),
    sa.Column('needs_maintenance', sa.Boolean(), nullable=True),
    sa.Column('current_station_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['current_station_id'], ['stations.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('trips',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('origination_station_id', sa.Integer(), nullable=True),
    sa.Column('destination_station_id', sa.Integer(), nullable=True),
    sa.Column('bike_id', sa.Integer(), nullable=True),
    sa.Column('rider_id', sa.Integer(), nullable=True),
    sa.Column('start_time', sa.DateTime(), nullable=False),
    sa.Column('end_time', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['bike_id'], ['bikes.id'], ),
    sa.ForeignKeyConstraint(['destination_station_id'], ['stations.id'], ),
    sa.ForeignKeyConstraint(['origination_station_id'], ['stations.id'], ),
    sa.ForeignKeyConstraint(['rider_id'], ['riders.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('trips')
    op.drop_table('bikes')
    op.drop_table('stations')
    op.drop_table('riders')
    # ### end Alembic commands ###
