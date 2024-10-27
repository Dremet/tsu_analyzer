import os
import sys
import json
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
                select(Driver).where(Driver.steam_id == driver_dict["ID"])
            ).first()

            if not driver:
                driver = Driver(
                    name=driver_dict["name"],
                    steam_id=driver_dict["ID"],
                    clan=driver_dict["clan"],
                    flag=driver_dict["country"],
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
                select(Elo).where(Elo.driver_id == driver_id).order_by(desc(Elo.last_timestamp)
                )
            ).first()

            if elo:
                value = elo.value
                number_races = elo.number_races
                print("TRUE")
            else:
                value = 1000.0
                number_races = 0
                print("FALSE")
            
            print(driver_id)
            print(value, number_races)      
            
            
        except Exception as e:
            print("Error:", e)
            session.rollback()

    return value, number_races



def get_drivers_dict(data):
    players = data.get('players', [])

    drivers_by_id = {}

    # Über die Liste der Spieler (players) iterieren, um die Zuordnung zu erstellen
    for player in players:
        player_id = player.get('ID')  # Verwende den Key "ID" für die Fahrer-ID
        player_name = player.get('name')  # Verwende den Key "name" für den Fahrernamen
        
        driver, driver_id = get_or_create_driver(engine, player)
        elo_value, elo_number_races = get_or_create_elo(engine, driver_id)

        drivers_by_id[player_id] = {
            "name":player_name,
            "driver_db_object":driver,
            "elo_value_before":elo_value,
            "elo_number_races_before":elo_number_races,
            "elo_value_new":elo_value,
            "elo_number_races_new":elo_number_races,
            "last_car":""
        }
    print(drivers_by_id)
    
    return drivers_by_id
        
    
   
def get_events_df(data, drivers_by_id):

    events = data.get('events', [])
    players = data.get('players', [])

    # Erstelle ein neues Dictionary für die Events, um die Positionen der Fahrer zu sammeln
    event_results = {}
    event_names = []
    event_timestamps = []
    event_indices = []

    # Über alle Events iterieren, um die Fahrerpositionen zu sammeln
    for event in events:
        if event["eventType"] != "Normal race":
            continue
        
        event_index = event['eventIndex']
        event_names.append(event['eventName'])
        event_timestamps.append(event['datePlayed'])
        event_indices.append(event['eventIndex'])

        event_results[event_index] = {}

        # Initialisiere die Positionen der Fahrer für dieses Event als leer
        for driver_id in drivers_by_id.keys():
            event_results[event_index][driver_id] = None

        # Gehe über alle Spieler und sammle die Positionen für das Event
        for player in players:
            player_events = player.get('events', [])
            player_id = player.get('ID')
            for player_event in player_events:
                if player_event['eventIndex'] == event_index:
                    # Finde die Position des Fahrers für dieses Event
                    position = player_event.get('position', None)
                    if player_id in drivers_by_id:
                        event_results[event_index][player_id] = position

    
    return pd.DataFrame.from_dict(event_results, orient='index'), event_names, event_timestamps, event_indices



def calc_expected_score(driver_elo, opponent_elo, D=400):
    # https://towardsdatascience.com/developing-a-generalized-elo-rating-system-for-multiplayer-games-b9b495e87802
    # D=400 is a general default value
    # it means that someone with 1500 ELO wins against someone with 1000 ELO with a likelihood of 95% which seems reasonable
    return 1./(1+np.power(10., (opponent_elo-driver_elo)/D))


def calc_elo_changes(drivers_by_id, df_events, event_names, event_timestamps, event_indices):
    cars_by_player_and_event = {}

    for player in data.get('players', []):
        cars_by_player_and_event[player["name"]] = {}
        for event in player["events"]:             
             cars_by_player_and_event[player["name"]][event["eventIndex"]]= event["vehicle"]
    

    for i, (_, event_results) in enumerate(df_events.iterrows()):
        for driver_id, driver_result in event_results.items():
            if driver_result == 0:
                continue

            print(drivers_by_id[driver_id]["name"], " with elo ", drivers_by_id[driver_id]["elo_value_before"])

            expected_score_nominator = 0
            opponents = 0

            for opponent_id, opponent_result in event_results.items():
                if driver_id == opponent_id or opponent_result == 0:
                    continue

                single_expected_score = calc_expected_score(drivers_by_id[driver_id]["elo_value_before"], drivers_by_id[opponent_id]["elo_value_before"], D=400)

                expected_score_nominator += single_expected_score
                opponents += 1
            
            overall_players = opponents + 1
                
            expected_score = expected_score_nominator / (overall_players * opponents / 2)

            scoring = (overall_players-driver_result) / (overall_players * opponents / 2)

            elo_change = K_FACTOR * opponents * (scoring - expected_score)
            print(f"Overall elo change: {elo_change} (had {opponents} opponents)")

            # add elo change to previous elo, can never go below 100
            new_elo = max(drivers_by_id[driver_id]["elo_value_before"] + elo_change, 100)
            print(f"New ELO: {new_elo}")

            drivers_by_id[driver_id]["last_car"] = cars_by_player_and_event[drivers_by_id[driver_id]["name"]][event_indices[i]]
            drivers_by_id[driver_id]["elo_value_new"] = new_elo
            drivers_by_id[driver_id]["elo_number_races_new"] = drivers_by_id[driver_id]["elo_number_races_before"] + 1
                
            # apply elo changes for all drivers
            print(cars_by_player_and_event)

            print(drivers_by_id[driver_id]["name"])

            print(event_indices)

            print(i)

            print(cars_by_player_and_event[drivers_by_id[driver_id]["name"]][event_indices[i]])

        apply_elo_changes(drivers_by_id, track_name=event_names[i], race_timestamp=event_timestamps[i])

        # after calculations for all drivers for that specific events are done, we need to update the before values for the next event
        # to make sure the updated elo values are used for the next event
        for driver_id in drivers_by_id.keys():
            drivers_by_id[driver_id]["elo_value_before"] = drivers_by_id[driver_id]["elo_value_new"]
            drivers_by_id[driver_id]["elo_number_races_before"] = drivers_by_id[driver_id]["elo_number_races_new"]
        
    
    return drivers_by_id


def apply_elo_changes(drivers_by_id, track_name, race_timestamp):
    with Session(engine) as session:
        try:
            for driver_dict in drivers_by_id.values():
                elo_change = driver_dict["elo_value_new"]-driver_dict["elo_value_before"]
                
                if elo_change == 0:
                    continue
                
                new_elo_entry = Elo(
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

    # Check if a file path is provided as a command-line argument
    if len(sys.argv) < 2:
        print("Usage: pdm run python src/tsu_analyzer/elo/update_with_java_tool_export.py <path_to_dbjson_file>")
        sys.exit(1)

    # The first argument is always the script name, so the second argument (index 1) is the file path
    file_path = sys.argv[1]

    # read file
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # get drivers dict
    drivers_by_id = get_drivers_dict(data)
        
    # get events dataframe
    df_events,event_names,event_timestamps,event_indices = get_events_df(data, drivers_by_id)

    # calc elo changes for all events and all drivers
    drivers_by_id = calc_elo_changes(drivers_by_id, df_events,event_names,event_timestamps,event_indices)
