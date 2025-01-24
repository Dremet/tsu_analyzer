import sys

sys.path.append(".")
from src.tsu_analyzer.helpers import *

if len(sys.argv) < 5:
    print(
        "Usage: pdm run python src/tsu_analyzer/animate_race.py <path_to_track_csv_file> <name_of_track> <author> <path_to_result_file>"
    )
    sys.exit(1)

# The first argument is always the script name, so the second argument (index 1) is the file path
track_file_path = sys.argv[1]
name_of_track = sys.argv[2]
author = sys.argv[3]
result_file_path = sys.argv[4]

## using track csv file
df_track = get_track_data(track_file_path)
df_track.to_csv("track.csv", index=False)

## using result json file
result_dict = get_result_data(result_file_path)
df_drivers = get_drivers_df(result_dict)
df_drivers.to_csv("driver.csv", index=False)
df_results = get_results_df(result_dict)
df_results.to_csv("results.csv", index=False)

## merging
df_results_w_drivers = pd.merge(
    df_results, df_drivers, how="inner", left_on="player_index", right_on="index"
)
df = pd.merge(
    df_results_w_drivers,
    df_track[[col for col in df_track.columns if col != "sector"]],
    how="inner",
    left_on="cp",
    right_on="cp",
)

animate_race(df, df_track, "animations/race_animation.mp4", name_of_track, author)
