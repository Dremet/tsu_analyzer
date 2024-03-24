"""Initial migration

Revision ID: 8d8740f34a5d
Revises: 
Create Date: 2024-03-23 20:17:26.185870

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8d8740f34a5d'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('cars',
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('guid', sa.String(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('modified_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_cars')),
    schema='tsu'
    )
    op.create_table('drivers',
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('steam_id', sa.BigInteger(), nullable=False),
    sa.Column('clan', sa.String(), nullable=False),
    sa.Column('flag', sa.String(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('modified_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_drivers')),
    schema='tsu'
    )
    op.create_table('tracks',
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('guid', sa.String(), nullable=False),
    sa.Column('maker_id', sa.BigInteger(), nullable=False),
    sa.Column('level_type', sa.String(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('modified_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_tracks')),
    schema='tsu'
    )
    op.create_table('events',
    sa.Column('track_id', sa.Integer(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('modified_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['track_id'], ['tsu.tracks.id'], name=op.f('fk_events_track_id_tracks')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_events')),
    schema='tsu'
    )
    op.create_table('event_car_association',
    sa.Column('event_id', sa.Integer(), nullable=False),
    sa.Column('car_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['car_id'], ['tsu.cars.id'], name=op.f('fk_event_car_association_car_id_cars')),
    sa.ForeignKeyConstraint(['event_id'], ['tsu.events.id'], name=op.f('fk_event_car_association_event_id_events')),
    sa.PrimaryKeyConstraint('event_id', 'car_id', name=op.f('pk_event_car_association')),
    schema='tsu'
    )
    op.create_table('event_results',
    sa.Column('event_id', sa.Integer(), nullable=False),
    sa.Column('driver_id', sa.Integer(), nullable=False),
    sa.Column('car_id', sa.Integer(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('modified_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['car_id'], ['tsu.cars.id'], name=op.f('fk_event_results_car_id_cars')),
    sa.ForeignKeyConstraint(['driver_id'], ['tsu.drivers.id'], name=op.f('fk_event_results_driver_id_drivers')),
    sa.ForeignKeyConstraint(['event_id'], ['tsu.events.id'], name=op.f('fk_event_results_event_id_events')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_event_results')),
    schema='tsu'
    )
    op.create_table('lap_results',
    sa.Column('event_result_id', sa.Integer(), nullable=False),
    sa.Column('lap_time', sa.Float(), nullable=False),
    sa.Column('cflags', sa.Integer(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('modified_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['event_result_id'], ['tsu.event_results.id'], name=op.f('fk_lap_results_event_result_id_event_results')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_lap_results')),
    schema='tsu'
    )
    op.create_table('checkpoint_results',
    sa.Column('lap_result_id', sa.Integer(), nullable=False),
    sa.Column('time', sa.Float(), nullable=False),
    sa.Column('is_sector', sa.Boolean(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('modified_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['lap_result_id'], ['tsu.lap_results.id'], name=op.f('fk_checkpoint_results_lap_result_id_lap_results')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_checkpoint_results')),
    schema='tsu'
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('checkpoint_results', schema='tsu')
    op.drop_table('lap_results', schema='tsu')
    op.drop_table('event_results', schema='tsu')
    op.drop_table('event_car_association', schema='tsu')
    op.drop_table('events', schema='tsu')
    op.drop_table('tracks', schema='tsu')
    op.drop_table('drivers', schema='tsu')
    op.drop_table('cars', schema='tsu')
    # ### end Alembic commands ###