"""added elo heat table

Revision ID: 69b153928676
Revises: 96d31290ed78
Create Date: 2024-11-30 16:14:04.376118

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '69b153928676'
down_revision: Union[str, None] = '96d31290ed78'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('elo_heat',
    sa.Column('driver_id', sa.Integer(), nullable=False),
    sa.Column('value', sa.Float(), nullable=False),
    sa.Column('delta', sa.Float(), nullable=False),
    sa.Column('number_races', sa.Integer(), nullable=False),
    sa.Column('last_track_name', sa.String(), nullable=False),
    sa.Column('last_car_name', sa.String(), nullable=False),
    sa.Column('last_timestamp', sa.DateTime(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('modified_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['driver_id'], ['tsu.drivers.id'], name=op.f('fk_elo_heat_driver_id_drivers')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_elo_heat')),
    schema='tsu'
    )
    op.drop_constraint('fk_checkpoint_results_lap_result_id_lap_results', 'checkpoint_results', type_='foreignkey')
    op.create_foreign_key(op.f('fk_checkpoint_results_lap_result_id_lap_results'), 'checkpoint_results', 'lap_results', ['lap_result_id'], ['id'], source_schema='tsu', referent_schema='tsu')
    op.drop_constraint('fk_elo_driver_id_drivers', 'elo', type_='foreignkey')
    op.create_foreign_key(op.f('fk_elo_driver_id_drivers'), 'elo', 'drivers', ['driver_id'], ['id'], source_schema='tsu', referent_schema='tsu')
    op.drop_constraint('fk_event_car_association_car_id_cars', 'event_car_association', type_='foreignkey')
    op.drop_constraint('fk_event_car_association_event_id_events', 'event_car_association', type_='foreignkey')
    op.create_foreign_key(op.f('fk_event_car_association_event_id_events'), 'event_car_association', 'events', ['event_id'], ['id'], source_schema='tsu', referent_schema='tsu')
    op.create_foreign_key(op.f('fk_event_car_association_car_id_cars'), 'event_car_association', 'cars', ['car_id'], ['id'], source_schema='tsu', referent_schema='tsu')
    op.drop_constraint('fk_event_results_driver_id_drivers', 'event_results', type_='foreignkey')
    op.drop_constraint('fk_event_results_car_id_cars', 'event_results', type_='foreignkey')
    op.drop_constraint('fk_event_results_event_id_events', 'event_results', type_='foreignkey')
    op.create_foreign_key(op.f('fk_event_results_car_id_cars'), 'event_results', 'cars', ['car_id'], ['id'], source_schema='tsu', referent_schema='tsu')
    op.create_foreign_key(op.f('fk_event_results_event_id_events'), 'event_results', 'events', ['event_id'], ['id'], source_schema='tsu', referent_schema='tsu')
    op.create_foreign_key(op.f('fk_event_results_driver_id_drivers'), 'event_results', 'drivers', ['driver_id'], ['id'], source_schema='tsu', referent_schema='tsu')
    op.drop_constraint('fk_events_track_id_tracks', 'events', type_='foreignkey')
    op.create_foreign_key(op.f('fk_events_track_id_tracks'), 'events', 'tracks', ['track_id'], ['id'], source_schema='tsu', referent_schema='tsu')
    op.drop_constraint('fk_lap_results_event_result_id_event_results', 'lap_results', type_='foreignkey')
    op.create_foreign_key(op.f('fk_lap_results_event_result_id_event_results'), 'lap_results', 'event_results', ['event_result_id'], ['id'], source_schema='tsu', referent_schema='tsu')
    op.drop_constraint('fk_sector_results_lap_result_id_lap_results', 'sector_results', type_='foreignkey')
    op.create_foreign_key(op.f('fk_sector_results_lap_result_id_lap_results'), 'sector_results', 'lap_results', ['lap_result_id'], ['id'], source_schema='tsu', referent_schema='tsu')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(op.f('fk_sector_results_lap_result_id_lap_results'), 'sector_results', schema='tsu', type_='foreignkey')
    op.create_foreign_key('fk_sector_results_lap_result_id_lap_results', 'sector_results', 'lap_results', ['lap_result_id'], ['id'])
    op.drop_constraint(op.f('fk_lap_results_event_result_id_event_results'), 'lap_results', schema='tsu', type_='foreignkey')
    op.create_foreign_key('fk_lap_results_event_result_id_event_results', 'lap_results', 'event_results', ['event_result_id'], ['id'])
    op.drop_constraint(op.f('fk_events_track_id_tracks'), 'events', schema='tsu', type_='foreignkey')
    op.create_foreign_key('fk_events_track_id_tracks', 'events', 'tracks', ['track_id'], ['id'])
    op.drop_constraint(op.f('fk_event_results_driver_id_drivers'), 'event_results', schema='tsu', type_='foreignkey')
    op.drop_constraint(op.f('fk_event_results_event_id_events'), 'event_results', schema='tsu', type_='foreignkey')
    op.drop_constraint(op.f('fk_event_results_car_id_cars'), 'event_results', schema='tsu', type_='foreignkey')
    op.create_foreign_key('fk_event_results_event_id_events', 'event_results', 'events', ['event_id'], ['id'])
    op.create_foreign_key('fk_event_results_car_id_cars', 'event_results', 'cars', ['car_id'], ['id'])
    op.create_foreign_key('fk_event_results_driver_id_drivers', 'event_results', 'drivers', ['driver_id'], ['id'])
    op.drop_constraint(op.f('fk_event_car_association_car_id_cars'), 'event_car_association', schema='tsu', type_='foreignkey')
    op.drop_constraint(op.f('fk_event_car_association_event_id_events'), 'event_car_association', schema='tsu', type_='foreignkey')
    op.create_foreign_key('fk_event_car_association_event_id_events', 'event_car_association', 'events', ['event_id'], ['id'])
    op.create_foreign_key('fk_event_car_association_car_id_cars', 'event_car_association', 'cars', ['car_id'], ['id'])
    op.drop_constraint(op.f('fk_elo_driver_id_drivers'), 'elo', schema='tsu', type_='foreignkey')
    op.create_foreign_key('fk_elo_driver_id_drivers', 'elo', 'drivers', ['driver_id'], ['id'])
    op.drop_constraint(op.f('fk_checkpoint_results_lap_result_id_lap_results'), 'checkpoint_results', schema='tsu', type_='foreignkey')
    op.create_foreign_key('fk_checkpoint_results_lap_result_id_lap_results', 'checkpoint_results', 'lap_results', ['lap_result_id'], ['id'])
    op.drop_table('elo_heat', schema='tsu')
    # ### end Alembic commands ###