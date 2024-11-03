import sys
sys.path.append(".")
from src.tsu_analyzer.helpers import *

if len(sys.argv) < 5:
    print(
        "Usage: pdm run python src/tsu_analyzer/driver_comparison.py <path_to_track_csv_file> <name_of_track> <author> <path_to_result_file>"
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
df_results_w_drivers = pd.merge(df_results, df_drivers, how="inner", left_on="player_index", right_on="index")
df = pd.merge(df_results_w_drivers, df_track[[col for col in df_track.columns if col!='sector']], how="inner", left_on="cp", right_on="cp")

# calculation possible after merging
df["speed_kmh"] = df["distance_to_last"]/df["time"]*3.6
print(df)
print(df.columns)

plot_driver_comparison(df, df_track, "cyberpunk_42", "Dremet", "cyb_dre_speed.png", "cyb_dre_time.png", name_of_track, author)
plot_driver_comparison(df, df_track, "Nestori", "Frozeni", "nes_froz_speed.png", "nes_froz_time.png", name_of_track, author)