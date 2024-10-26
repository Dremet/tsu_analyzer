from typing import Optional, List
from datetime import datetime
from sqlalchemy import ForeignKey, MetaData, UniqueConstraint, Table, Column
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import BigInteger


from typing import List
from datetime import datetime
from sqlalchemy import ForeignKey, MetaData, Table, Column, BigInteger, Float, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


### BASE MODEL ###
class Base(DeclarativeBase):
    metadata = MetaData(
        schema="tsu",
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_`%(constraint_name)s`",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        },
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, nullable=False
    )
    modified_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, nullable=False
    )


event_car_association = Table(
    "event_car_association",
    Base.metadata,
    Column("event_id", ForeignKey("events.id"), primary_key=True),
    Column("car_id", ForeignKey("cars.id"), primary_key=True),
)


class Driver(Base):
    __tablename__ = "drivers"

    name: Mapped[str] = mapped_column()
    steam_id: Mapped[int] = mapped_column(BigInteger)
    clan: Mapped[str] = mapped_column()
    flag: Mapped[str] = mapped_column()


class Elo(Base):
    __tablename__ = "elo"

    driver_id: Mapped[int] = mapped_column(ForeignKey("tsu.drivers.id"))
    driver: Mapped["Driver"] = relationship("Driver")

    value: Mapped[float] = mapped_column(Float(asdecimal=False))
    number_races: Mapped[int] = mapped_column()
    

class Car(Base):
    __tablename__ = "cars"

    name: Mapped[str] = mapped_column()
    guid: Mapped[str] = mapped_column()

    events: Mapped[List["Event"]] = relationship(
        "Event", secondary=event_car_association, back_populates="cars"
    )


class Track(Base):
    __tablename__ = "tracks"

    name: Mapped[str] = mapped_column()
    guid: Mapped[str] = mapped_column()
    maker_id: Mapped[int] = mapped_column(BigInteger)
    level_type: Mapped[str] = mapped_column()

    events: Mapped[List["Event"]] = relationship("Event", back_populates="track")


class Event(Base):
    __tablename__ = "events"

    track_id: Mapped[int] = mapped_column(ForeignKey("tsu.tracks.id"))
    track: Mapped["Track"] = relationship("Track", back_populates="events")
    cars: Mapped[List["Car"]] = relationship(
        "Car", secondary=event_car_association, back_populates="events"
    )


class EventResult(Base):
    __tablename__ = "event_results"

    event_id: Mapped[int] = mapped_column(ForeignKey("tsu.events.id"))
    driver_id: Mapped[int] = mapped_column(ForeignKey("tsu.drivers.id"))
    car_id: Mapped[int] = mapped_column(ForeignKey("tsu.cars.id"))

    event: Mapped["Event"] = relationship("Event")
    driver: Mapped["Driver"] = relationship("Driver")
    car: Mapped["Car"] = relationship("Car")

    lap_results: Mapped[List["LapResult"]] = relationship(
        "LapResult", back_populates="event_result"
    )

    driven_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)


class LapResult(Base):
    __tablename__ = "lap_results"

    event_result_id: Mapped[int] = mapped_column(ForeignKey("tsu.event_results.id"))
    lap_time: Mapped[float] = mapped_column(Float(asdecimal=False))
    cflags: Mapped[int] = mapped_column()

    event_result: Mapped["EventResult"] = relationship(
        "EventResult", back_populates="lap_results"
    )
    checkpoint_results: Mapped[List["CheckpointResult"]] = relationship(
        "CheckpointResult", back_populates="lap_result"
    )
    sector_results: Mapped[List["SectorResult"]] = relationship(
        "SectorResult", back_populates="lap_result"
    )


class SectorResult(Base):
    __tablename__ = "sector_results"

    lap_result_id: Mapped[int] = mapped_column(ForeignKey("tsu.lap_results.id"))
    time: Mapped[float] = mapped_column(Float(asdecimal=False))
    number: Mapped[int] = mapped_column()

    lap_result: Mapped["LapResult"] = relationship(
        "LapResult", back_populates="sector_results"
    )


class CheckpointResult(Base):
    __tablename__ = "checkpoint_results"

    lap_result_id: Mapped[int] = mapped_column(ForeignKey("tsu.lap_results.id"))
    time: Mapped[float] = mapped_column(Float(asdecimal=False))
    is_sector: Mapped[bool] = mapped_column(Boolean)
    number: Mapped[int] = mapped_column()

    lap_result: Mapped["LapResult"] = relationship(
        "LapResult", back_populates="checkpoint_results"
    )


if __name__ == "__main__":
    import os
    from sqlalchemy import create_engine
    from dotenv import load_dotenv

    load_dotenv()

    engine = create_engine(os.environ.get("TSU_HOTLAPPING_POSTGRES_URL"), echo=True)
    Base.metadata.create_all(engine)
