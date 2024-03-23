"""added sector time results

Revision ID: 8cba1627d403
Revises: 2f00e5e4fdf4
Create Date: 2024-03-23 23:27:02.176977

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8cba1627d403'
down_revision: Union[str, None] = '2f00e5e4fdf4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('sector_results',
    sa.Column('lap_result_id', sa.Integer(), nullable=False),
    sa.Column('time', sa.Float(), nullable=False),
    sa.Column('number', sa.Integer(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('modified_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['lap_result_id'], ['tsu.lap_results.id'], name=op.f('fk_sector_results_lap_result_id_lap_results')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_sector_results')),
    schema='tsu'
    )
    op.add_column('checkpoint_results', sa.Column('number', sa.Integer(), nullable=False))
    op.drop_constraint('fk_checkpoint_results_lap_result_id_lap_results', 'checkpoint_results', type_='foreignkey')
    op.create_foreign_key(op.f('fk_checkpoint_results_lap_result_id_lap_results'), 'checkpoint_results', 'lap_results', ['lap_result_id'], ['id'], source_schema='tsu', referent_schema='tsu')
    op.drop_constraint('fk_event_car_association_car_id_cars', 'event_car_association', type_='foreignkey')
    op.drop_constraint('fk_event_car_association_event_id_events', 'event_car_association', type_='foreignkey')
    op.create_foreign_key(op.f('fk_event_car_association_car_id_cars'), 'event_car_association', 'cars', ['car_id'], ['id'], source_schema='tsu', referent_schema='tsu')
    op.create_foreign_key(op.f('fk_event_car_association_event_id_events'), 'event_car_association', 'events', ['event_id'], ['id'], source_schema='tsu', referent_schema='tsu')
    op.drop_constraint('fk_event_results_car_id_cars', 'event_results', type_='foreignkey')
    op.drop_constraint('fk_event_results_event_id_events', 'event_results', type_='foreignkey')
    op.drop_constraint('fk_event_results_driver_id_drivers', 'event_results', type_='foreignkey')
    op.create_foreign_key(op.f('fk_event_results_event_id_events'), 'event_results', 'events', ['event_id'], ['id'], source_schema='tsu', referent_schema='tsu')
    op.create_foreign_key(op.f('fk_event_results_car_id_cars'), 'event_results', 'cars', ['car_id'], ['id'], source_schema='tsu', referent_schema='tsu')
    op.create_foreign_key(op.f('fk_event_results_driver_id_drivers'), 'event_results', 'drivers', ['driver_id'], ['id'], source_schema='tsu', referent_schema='tsu')
    op.drop_constraint('fk_events_track_id_tracks', 'events', type_='foreignkey')
    op.create_foreign_key(op.f('fk_events_track_id_tracks'), 'events', 'tracks', ['track_id'], ['id'], source_schema='tsu', referent_schema='tsu')
    op.drop_constraint('fk_lap_results_event_result_id_event_results', 'lap_results', type_='foreignkey')
    op.create_foreign_key(op.f('fk_lap_results_event_result_id_event_results'), 'lap_results', 'event_results', ['event_result_id'], ['id'], source_schema='tsu', referent_schema='tsu')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(op.f('fk_lap_results_event_result_id_event_results'), 'lap_results', schema='tsu', type_='foreignkey')
    op.create_foreign_key('fk_lap_results_event_result_id_event_results', 'lap_results', 'event_results', ['event_result_id'], ['id'])
    op.drop_constraint(op.f('fk_events_track_id_tracks'), 'events', schema='tsu', type_='foreignkey')
    op.create_foreign_key('fk_events_track_id_tracks', 'events', 'tracks', ['track_id'], ['id'])
    op.drop_constraint(op.f('fk_event_results_driver_id_drivers'), 'event_results', schema='tsu', type_='foreignkey')
    op.drop_constraint(op.f('fk_event_results_car_id_cars'), 'event_results', schema='tsu', type_='foreignkey')
    op.drop_constraint(op.f('fk_event_results_event_id_events'), 'event_results', schema='tsu', type_='foreignkey')
    op.create_foreign_key('fk_event_results_driver_id_drivers', 'event_results', 'drivers', ['driver_id'], ['id'])
    op.create_foreign_key('fk_event_results_event_id_events', 'event_results', 'events', ['event_id'], ['id'])
    op.create_foreign_key('fk_event_results_car_id_cars', 'event_results', 'cars', ['car_id'], ['id'])
    op.drop_constraint(op.f('fk_event_car_association_event_id_events'), 'event_car_association', schema='tsu', type_='foreignkey')
    op.drop_constraint(op.f('fk_event_car_association_car_id_cars'), 'event_car_association', schema='tsu', type_='foreignkey')
    op.create_foreign_key('fk_event_car_association_event_id_events', 'event_car_association', 'events', ['event_id'], ['id'])
    op.create_foreign_key('fk_event_car_association_car_id_cars', 'event_car_association', 'cars', ['car_id'], ['id'])
    op.drop_constraint(op.f('fk_checkpoint_results_lap_result_id_lap_results'), 'checkpoint_results', schema='tsu', type_='foreignkey')
    op.create_foreign_key('fk_checkpoint_results_lap_result_id_lap_results', 'checkpoint_results', 'lap_results', ['lap_result_id'], ['id'])
    op.drop_column('checkpoint_results', 'number')
    op.drop_table('sector_results', schema='tsu')
    # ### end Alembic commands ###
