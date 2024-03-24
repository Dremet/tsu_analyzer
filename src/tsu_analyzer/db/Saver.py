import os
import json
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine, select, desc, and_
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import sys

sys.path.append(".")
from src.tsu_analyzer.db.models import *


class Saver:
    def __init__(self, file_name) -> None:
        with open(file_name, "r", encoding="utf-8") as file:
            self.data = json.load(file)

    def get_engine(self):
        load_dotenv()

        return create_engine(os.environ.get("TSU_HOTLAPPING_POSTGRES_URL"), echo=True)

    @staticmethod
    def get_or_create_driver(engine, driver_dict):

        with Session(engine) as session:
            try:
                driver = session.scalars(
                    select(Driver).where(Driver.steam_id == driver_dict["id"])
                ).first()

                if not driver:
                    driver = Driver(
                        name=driver_dict["name"],
                        steam_id=driver_dict["id"],
                        clan=driver_dict["clan"],
                        flag=driver_dict["flag"],
                    )
                    session.add(driver)
                    session.commit()
            except Exception as e:
                print("Error:", e)
                session.rollback()

        return driver

    @staticmethod
    def get_or_create_car(engine, car_dict):

        with Session(engine) as session:
            try:
                car = session.scalars(
                    select(Car).where(Car.guid == car_dict["guid"])
                ).first()

                if not car:
                    car = Car(name=car_dict["name"], guid=car_dict["guid"])
                    session.add(car)
                    session.commit()
            except Exception as e:
                print("Error:", e)
                session.rollback()

        return car

    @staticmethod
    def get_or_create_track(engine, track_dict):

        with Session(engine) as session:
            try:
                track = session.scalars(
                    select(Track).where(Track.guid == track_dict["guid"])
                ).first()

                if not track:
                    track = Track(
                        name=track_dict["name"],
                        guid=track_dict["guid"],
                        maker_id=track_dict["makerId"],
                        level_type=track_dict["levelType"],
                    )
                    session.add(track)
                    session.commit()
            except Exception as e:
                print("Error:", e)
                session.rollback()

        return track

    @staticmethod
    def get_create_or_update_event(engine, event_dict):
        with Session(engine) as session:
            session.add(event_dict["track"])

            event = session.scalars(
                select(Event)
                .where(Event.track_id == event_dict["track"].id)
                .order_by(desc(Event.created_at))
            ).first()

            if not event:
                event = Event(track_id=event_dict["track"].id)
                session.add(event)
                session.commit()

            for car in event_dict["cars"]:
                merged_car = session.merge(car)
                if merged_car not in event.cars:
                    event.cars.append(merged_car)

            session.commit()

        return event

    @staticmethod
    def get_or_create_event_result(engine, event_result_dict):

        with Session(engine) as session:
            session.add(event_result_dict["event"])
            session.add(event_result_dict["driver"])
            session.add(event_result_dict["car"])

            try:
                event_result = session.scalars(
                    select(EventResult).where(
                        and_(
                            EventResult.event_id == event_result_dict["event"].id,
                            EventResult.driver_id == event_result_dict["driver"].id,
                            EventResult.car_id == event_result_dict["car"].id,
                            EventResult.driven_at == event_result_dict["driven_at"],
                        )
                    )
                ).first()

                if not event_result:
                    event_result = EventResult(
                        event_id=event_result_dict["event"].id,
                        driver_id=event_result_dict["driver"].id,
                        car_id=event_result_dict["car"].id,
                        driven_at=event_result_dict["driven_at"],
                    )
                    session.add(event_result)
                    session.commit()
            except Exception as e:
                print("Error:", e)
                session.rollback()

        return event_result

    @staticmethod
    def get_or_create_lap_result(engine, lap_result_dict):

        with Session(engine) as session:
            session.add(lap_result_dict["event_result"])

            try:
                lap_result = session.scalars(
                    select(LapResult).where(
                        and_(
                            LapResult.event_result_id
                            == lap_result_dict["event_result"].id,
                            LapResult.lap_time == lap_result_dict["lap_time"],
                            LapResult.cflags == lap_result_dict["cflags"],
                        )
                    )
                ).first()

                if not lap_result:
                    lap_result = LapResult(
                        event_result_id=lap_result_dict["event_result"].id,
                        lap_time=lap_result_dict["lap_time"],
                        cflags=lap_result_dict["cflags"],
                    )
                    session.add(lap_result)
                    session.commit()
            except Exception as e:
                print("Error:", e)
                session.rollback()

        return lap_result

    @staticmethod
    def delete_existing_cp_results(session, lap_result_id):
        try:
            session.query(CheckpointResult).filter(
                CheckpointResult.lap_result_id == lap_result_id
            ).delete()
            session.commit()
        except Exception as e:
            print(
                f"Error deleting existing Checkpoint Results for lap_result_id: {lap_result_id}",
                e,
            )
            session.rollback()

    @staticmethod
    def insert_new_cp_results(session, lap_result_id, cp_results):
        try:
            mappings = [
                {
                    "lap_result_id": lap_result_id,
                    "time": cp_result["time"],
                    "is_sector": cp_result["is_sector"],
                    "number": cp_result["number"],
                }
                for cp_result in cp_results
            ]
            session.bulk_insert_mappings(CheckpointResult, mappings)
            session.commit()
        except Exception as e:
            print("Error inserting new checkpoint times:", e)
            session.rollback()

    @staticmethod
    def delete_existing_sector_results(session, lap_result_id):
        try:
            session.query(SectorResult).filter(
                SectorResult.lap_result_id == lap_result_id
            ).delete()
            session.commit()
        except Exception as e:
            print(
                f"Error deleting existing Sector Results for lap_result_id: {lap_result_id}",
                e,
            )
            session.rollback()

    @staticmethod
    def insert_new_sector_results(session, lap_result_id, sector_results):
        try:
            mappings = [
                {
                    "lap_result_id": lap_result_id,
                    "time": sector_result["time"],
                    "number": sector_result["number"],
                }
                for sector_result in sector_results
            ]
            session.bulk_insert_mappings(SectorResult, mappings)
            session.commit()
        except Exception as e:
            print("Error inserting new sector times:", e)
            session.rollback()

    def run(self):
        engine = self.get_engine()

        # start time of hotlapping event
        self.start_time = self.data["utcStartTime"]

        ### DRIVERS & CARS ###
        self.drivers = []
        self.cars = []

        for player in self.data["players"]:
            driver_dict = player["player"]
            car_dict = player["vehicle"]

            driver = self.get_or_create_driver(engine, driver_dict)
            self.drivers.append(driver)

            car = self.get_or_create_car(engine, car_dict)
            self.cars.append(car)

        ### TRACK ###
        track = self.get_or_create_track(engine, self.data["level"])

        ### EVENT ###
        event_dict = dict()
        event_dict["track"] = track
        event_dict["cars"] = self.cars

        event = self.get_create_or_update_event(engine, event_dict)

        ### EVENT RESULT ###
        event_result_dict = dict()
        event_result_dict["event"] = event

        number_checkpoints = len(
            self.data["raceStats"]["checkpoints"]["checkpointToSector"]
        )
        indices_sectors = self.data["raceStats"]["checkpoints"]["sectorToCheckpoint"]

        player_stats = self.data["raceStats"]["playerStats"]

        for i, driver_player_stats in enumerate(player_stats):

            event_result_dict["driver"] = self.drivers[i]
            event_result_dict["car"] = self.cars[i]
            event_result_dict["driven_at"] = datetime.strptime(
                self.start_time, "%Y-%m-%dT%H:%M:%S%z"
            )

            event_result = self.get_or_create_event_result(engine, event_result_dict)

            ### LAP RESULT ###
            lap_result_dict = dict()
            lap_result_dict["event_result"] = event_result

            all_checkpoint_times = driver_player_stats["checkpointTimes"]

            for j, lap_checkpoint_times in enumerate(all_checkpoint_times):
                # last lap_checkpoint_times entry consists of one checkpoint time, namely finish line time
                if len(lap_checkpoint_times["times"]) == 1:
                    continue

                lap_result_dict["cflags"] = lap_checkpoint_times["cFlags"]
                cp_times_this_lap = lap_checkpoint_times["times"]
                first_cp_time_next_lap = all_checkpoint_times[j + 1]["times"][0]

                # double check if driver passed all checkpoints
                if len(cp_times_this_lap) == number_checkpoints:
                    lap_result_dict["lap_time"] = (
                        first_cp_time_next_lap - cp_times_this_lap[0]
                    ) / 10000.0

                    lap_result = self.get_or_create_lap_result(engine, lap_result_dict)

                    ### Checkpoint Result ###

                    with Session(engine) as session:
                        self.delete_existing_cp_results(session, lap_result.id)

                        cp_results = []

                        for k, cp_time in enumerate(cp_times_this_lap):
                            cp_result = {}

                            # calculate time difference between next sector time and this one
                            # this is relevant for the last checkpoint time before start and finish line
                            if k + 1 == len(cp_times_this_lap):
                                cp_result["time"] = (
                                    first_cp_time_next_lap - cp_time
                                ) / 10000.0
                            else:
                                # this is valid for all others
                                cp_result["time"] = (
                                    cp_times_this_lap[k + 1] - cp_time
                                ) / 10000.0

                            # the very first cp is flagged as a
                            cp_result["is_sector"] = (
                                k + 1 in indices_sectors or k + 1 == number_checkpoints
                            )
                            cp_result["number"] = k + 1

                            cp_results.append(cp_result)

                        self.insert_new_cp_results(session, lap_result.id, cp_results)

                        ### SECTOR RESULTS ###
                        self.delete_existing_sector_results(session, lap_result.id)

                        sector_times_this_lap = [
                            cp_times_this_lap[ind] for ind in indices_sectors
                        ]

                        sector_results = []

                        for l, sector_time in enumerate(sector_times_this_lap):
                            sector_result = dict()

                            if l + 1 == len(sector_times_this_lap):
                                sector_result["time"] = (
                                    first_cp_time_next_lap - sector_time
                                ) / 10000.0
                            else:
                                sector_result["time"] = (
                                    sector_times_this_lap[l + 1] - sector_time
                                ) / 10000.0

                            sector_result["number"] = l + 1

                            sector_results.append(sector_result)

                        self.insert_new_sector_results(
                            session, lap_result.id, sector_results
                        )


if __name__ == "__main__":
    saver = Saver("examples/20240323_234957_Interlagosv6.json")
    saver.run()
