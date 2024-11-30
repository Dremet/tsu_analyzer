import os
import sys
import json
import shutil
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, select, desc, and_
from sqlalchemy.orm import Session
from dotenv import load_dotenv

sys.path.append(".")
from src.tsu_analyzer.db.models import *

K_FACTOR = 20

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
            driver_id = driver.id
        except Exception as e:
            print("Error:", e)
            session.rollback()

    return driver, driver_id


def get_or_create_elo(engine, driver_id):

    with Session(engine) as session:
        try:
            elo = session.scalars(
                select(EloHeat).where(EloHeat.driver_id == driver_id).order_by(desc(EloHeat.last_timestamp)
                )
            ).first()

            if elo:
                value = elo.value
                number_races = elo.number_races
            else:
                value = 1000.0
                number_races = 0
        except Exception as e:
            print("Error:", e)
            session.rollback()
    
    return value, number_races



def get_drivers_dict(data):
    players = data.get('players', [])

    drivers_by_id = {}

    # Über die Liste der Spieler (players) iterieren, um die Zuordnung zu erstellen
    for i, row in enumerate(players):
        player = row["player"]
        player_id = player.get('id')  # Verwende den Key "ID" für die Fahrer-ID
        player_name = player.get('name')  # Verwende den Key "name" für den Fahrernamen
        
        driver, driver_id = get_or_create_driver(engine, player)
        
        elo_value, elo_number_races = get_or_create_elo(engine, driver_id)
        
        drivers_by_id[player_id] = {
            "index":i,
            "name":player_name,
            "driver_db_object":driver,
            "elo_value_before":elo_value,
            "elo_number_races_before":elo_number_races,
            "elo_value_new":elo_value,
            "elo_number_races_new":elo_number_races,
            "last_car":row.get("vehicle").get("name")
        }

    return drivers_by_id
        
    
   
def get_event_results(data, drivers_by_id):

    track_name = data["level"]["name"]
    race_timestamp = data["utcStartTime"]

    race_results = data.get('raceStats', []).get("raceRanking").get("entries")
    
    drivers_steam_id_by_index = {}
    for steam_id, driver_dict in drivers_by_id.items():
        drivers_steam_id_by_index[driver_dict["index"]] = steam_id

    # Erstelle ein neues Dictionary für die Events, um die Positionen der Fahrer zu sammeln
    event_data = {}

    for pos, entry in enumerate(race_results, start=1):
        steam_id = drivers_steam_id_by_index[entry["playerIndex"]]
        event_data[steam_id] = pos

    return event_data,track_name,race_timestamp



def calc_expected_score(driver_elo, opponent_elo, D=400):
    # https://towardsdatascience.com/developing-a-generalized-elo-rating-system-for-multiplayer-games-b9b495e87802
    # D=400 is a general default value
    # it means that someone with 1500 ELO wins against someone with 1000 ELO with a likelihood of 95% which seems reasonable
    return 1./(1+np.power(10., (opponent_elo-driver_elo)/D))


def calc_elo_changes(drivers_by_id, event_data):
    for driver_id, driver_result in event_data.items():
        if driver_result == 0:
            continue
        
        print(drivers_by_id[driver_id]["name"], " with elo ", drivers_by_id[driver_id]["elo_value_before"])

        expected_score_nominator = 0.
        opponents = 0

        for opponent_id, opponent_result in event_data.items():
            if driver_id == opponent_id or opponent_result == 0:
                continue

            single_expected_score = calc_expected_score(drivers_by_id[driver_id]["elo_value_before"], drivers_by_id[opponent_id]["elo_value_before"], D=400)

            expected_score_nominator += single_expected_score
            opponents += 1
        
        overall_players = opponents + 1
            
        expected_score = expected_score_nominator / (overall_players * opponents / 2.)

        scoring = (overall_players-driver_result) / (overall_players * opponents / 2.)

        elo_change = K_FACTOR * opponents * (scoring - expected_score)
        print(f"Overall elo change: {elo_change} (had {opponents} opponents)")

        # add elo change to previous elo, can never go below 100
        new_elo = max(drivers_by_id[driver_id]["elo_value_before"] + elo_change, 100)
        print(f"New ELO: {new_elo}")

        drivers_by_id[driver_id]["elo_value_new"] = new_elo
        drivers_by_id[driver_id]["elo_number_races_new"] = drivers_by_id[driver_id]["elo_number_races_before"] + 1
    
    
    return drivers_by_id


def apply_elo_changes(drivers_by_id,track_name,race_timestamp):
    with Session(engine) as session:
        try:
            for driver_dict in drivers_by_id.values():
                elo_change = driver_dict["elo_value_new"]-driver_dict["elo_value_before"]
                
                new_elo_entry = EloHeat(
                    driver_id=driver_dict["driver_db_object"].id,
                    value=driver_dict["elo_value_new"],
                    delta=elo_change,
                    number_races=driver_dict["elo_number_races_new"],
                    last_track_name=track_name,
                    last_car_name=driver_dict["last_car"],
                    last_timestamp=race_timestamp
                )
                session.add(new_elo_entry)
            
            session.commit()
        except Exception as e:
            print("Error:", e)
            session.rollback()


if __name__ == "__main__":
    # load env vars from .env file
    load_dotenv()

    # create postgres engine
    engine = create_engine(os.environ.get("TSU_HOTLAPPING_POSTGRES_URL"), echo=True)

    base_dir = os.path.expanduser("~/stat_files")
    processed_dir = os.path.join(base_dir, "processed")
    
    # Create the processed directory if it doesn't exist
    os.makedirs(processed_dir, exist_ok=True)
    
    # Iterate over all files ending with "_event.json"
    for file_name in os.listdir(base_dir):
        if file_name.endswith("_event.json"):
            file_path = os.path.join(base_dir, file_name)
            print(file_path)
            # read file
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            # get drivers dict
            drivers_by_id = get_drivers_dict(data)

            # get events dataframe
            event_data,track_name,race_timestamp = get_event_results(data, drivers_by_id)

            # calc elo changes for all events and all drivers
            drivers_by_id = calc_elo_changes(drivers_by_id, event_data)

            # apply elo changes for all drivers
            apply_elo_changes(drivers_by_id,track_name,race_timestamp)

            # Move the file to the "processed" subdirectory
            #shutil.move(file_path, os.path.join(processed_dir, file_name))
            print(f"Moved {file_name} to {processed_dir}")