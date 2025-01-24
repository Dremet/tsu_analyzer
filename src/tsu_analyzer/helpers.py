import os
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import matplotlib as mpl
from matplotlib import font_manager as fm, cm, colors
from matplotlib.animation import FuncAnimation
from scipy.interpolate import splprep, splev

# Set the path to the ffmpeg executable explicitly
mpl.rcParams["animation.ffmpeg_path"] = "/usr/bin/ffmpeg"


### MATH ###
def _calculate_distance(row1, row2):
    return np.sqrt(
        (row1["x"] - row2["x"]) ** 2
        + (row1["y"] - row2["y"]) ** 2
        + (row1["z"] - row2["z"]) ** 2
    )


### READ DATA ###
def get_track_data(path: Path):
    df = pd.read_csv(path)

    # Move the first row to the last as the last checkpoint should be the start-finish-line
    df = pd.concat([df.iloc[1:], df.iloc[:1]], ignore_index=True)

    # calculate pixel distance to previous cp (if first, then distance to first)
    df["distance_to_last"] = [
        (
            _calculate_distance(df.iloc[i], df.iloc[i - 1])
            if i > 0
            else _calculate_distance(df.iloc[i], df.iloc[-1])
        )
        for i in range(len(df))
    ]

    # assign cp number to each row
    df["cp"] = range(1, len(df) + 1)

    # Initialize sector columns
    df["sector"] = None
    df["sector_ends"] = False

    # Set initial sector number
    sector = 1

    # Iterate by index to modify df directly
    for i in range(len(df)):
        df.at[i, "sector"] = sector

        if df.at[i, "Type"] == "Sector":
            sector += 1
            df.at[i, "sector_ends"] = True

    # Set sector_ends to True for the last row
    df.at[len(df) - 1, "sector_ends"] = True

    return df[["cp", "sector", "sector_ends", "x", "y", "z", "distance_to_last"]]


def get_result_data(path: Path):
    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)
    return data


### TRANSFORM DATA ###
def get_drivers_df(result_dict: dict):
    players = result_dict.get("players", [])

    drivers = []

    for i, row in enumerate(players):
        driver = {}

        player = row["player"]
        vehicle = row["vehicle"]

        driver["index"] = i
        driver["name"] = player["name"]
        driver["id"] = player["id"]
        driver["clan"] = player["clan"]
        driver["flag"] = player["flag"]
        driver["ai"] = player["ai"]
        driver["vehicle"] = vehicle["name"]
        driver["vehicle_guid"] = vehicle["guid"]
        driver["start_position"] = row["startPosition"]

        drivers.append(driver)

    return pd.DataFrame(drivers)


def get_drivers_data_by_name(result_dict: dict):
    players = result_dict.get("players", [])

    drivers_by_name = {}

    for i, row in enumerate(players):
        player = row["player"]
        vehicle = row["vehicle"]

        drivers_by_name[player["name"]] = {}

        drivers_by_name[player["name"]]["index"] = i
        drivers_by_name[player["name"]]["id"] = player["id"]
        drivers_by_name[player["name"]]["clan"] = player["clan"]
        drivers_by_name[player["name"]]["flag"] = player["flag"]
        drivers_by_name[player["name"]]["ai"] = player["ai"]
        drivers_by_name[player["name"]]["vehicle"] = vehicle["name"]
        drivers_by_name[player["name"]]["vehicle_guid"] = vehicle["guid"]
        drivers_by_name[player["name"]]["start_position"] = row["startPosition"]

    return drivers_by_name


def get_drivers_data_by_index(result_dict: dict):
    drivers_by_name = get_drivers_data_by_name(result_dict)

    drivers_by_index = {}

    for name, driver_dict in drivers_by_name.items():
        drivers_by_index[driver_dict["index"]] = {}
        drivers_by_index[driver_dict["index"]]["name"] = name

        for key, val in driver_dict.items():
            if key == "index":
                continue
            drivers_by_index[driver_dict["index"]][key] = val

    return drivers_by_index


def get_results_df(result_dict: dict):
    race_stats = result_dict.get("raceStats", [])

    indices_of_sector_checkpoints = race_stats["checkpoints"]["sectorToCheckpoint"][1:]

    result_time_data = []

    for player_index, player_stat in enumerate(race_stats["playerStats"], start=0):
        player_data = []

        start_time = player_stat["startTime"]
        last_cp_time = None

        for lap, lap_data in enumerate(player_stat["checkpointTimes"], start=1):
            # set sector to 1 at the beginning of the lap
            sector = 1

            for cp, cp_time in enumerate(lap_data["times"], start=0):
                if cp in indices_of_sector_checkpoints:
                    sector += 1

                player_data.append(
                    {
                        "lap": lap,
                        "sector": sector,
                        "cp": cp,
                        "player_index": player_index,
                        "time": (
                            (cp_time - start_time) / 10000.0
                            if last_cp_time is None
                            else (cp_time - last_cp_time) / 10000.0
                        ),
                    }
                )

                last_cp_time = cp_time

        result_time_data.append(player_data)

    # Flatten list of lists and convert to DataFrame
    flat_data = [item for sublist in result_time_data for item in sublist]
    df = pd.DataFrame(flat_data)

    ### Correct cp = 0 entries
    # the first entry from each lap should be assigned to the prior lap cause it is the time the car needed to go from the last cp to the start line
    # for lap 1 the time is always 0, so we can drop that
    df = df.loc[((df["lap"] != 1) | (df["cp"] != 0))].reset_index(drop=True)

    # # identify indices where cp equals 0
    cp_zero_indices = df[df["cp"] == 0].index

    for idx in cp_zero_indices:
        # assign to previous lap
        df.at[idx, "lap"] -= 1

        # assign to last sector
        df.at[idx, "sector"] = df.at[idx - 1, "sector"]

        # use last cp number and add 1 as it is really the last cp
        df.at[idx, "cp"] = df.at[idx - 1, "cp"] + 1

    df.sort_values(by=["lap", "cp", "player_index"], ascending=True, inplace=True)

    return df


def plot_driver_comparison(
    df,
    df_track,
    driver1,
    driver2,
    speed_output_path,
    time_output_path,
    name_of_track,
    author,
):
    # Load the local Impact font
    font_path = Path("track_coords/04B_09__.ttf")
    impact_font = fm.FontProperties(fname=font_path)

    # Adjust midpoint for track data
    x_middle_adjusted = df_track["x"]
    z_middle_adjusted = df_track["z"]
    x_closed = np.append(x_middle_adjusted, x_middle_adjusted.iloc[0])
    z_closed = np.append(z_middle_adjusted, z_middle_adjusted.iloc[0])

    # Smooth track curve
    tck, u = splprep([x_closed, z_closed], s=0)
    unew = np.linspace(0, 1, 1000)
    x_smooth, z_smooth = splev(unew, tck)

    # Filter data for each driver to compute metrics
    df_speed = df.groupby(["cp", "name"])["speed_kmh"].median().unstack()
    df_time = df.groupby(["cp", "name"])["time"].min().unstack()

    # Ensure both drivers exist in the DataFrame
    if driver1 not in df_speed.columns or driver2 not in df_speed.columns:
        raise ValueError("One or both drivers not found in the DataFrame")

    # Compute differences for color scaling
    speed_diff = df_speed[driver1] - df_speed[driver2]
    time_diff = df_time[driver2] - df_time[driver1]  # Lower time means faster

    # Set colormap
    cmap = cm.get_cmap("RdYlBu")

    # Normalize data for color scaling with symmetric range
    max_abs_speed_diff = max(abs(speed_diff.min()), abs(speed_diff.max()))
    max_abs_time_diff = max(abs(time_diff.min()), abs(time_diff.max()))
    norm_speed = colors.Normalize(vmin=-max_abs_speed_diff, vmax=max_abs_speed_diff)
    norm_time = colors.Normalize(vmin=-max_abs_time_diff, vmax=max_abs_time_diff)

    def plot_colored_track(ax, x_smooth, z_smooth, data_diff, norm, title, unit):
        # Plot each checkpoint colored by the difference
        for i in range(len(x_smooth) - 1):
            cp_index = int(
                i * len(data_diff) / len(x_smooth)
            )  # Scale to data_diff length
            if cp_index in data_diff.index:
                color_val = norm(data_diff.iloc[cp_index])
                color = cmap(color_val)
            else:
                color = cmap(0.5)  # Neutral color
            ax.plot(
                x_smooth[i : i + 2],
                z_smooth[i : i + 2],
                color=color,
                linewidth=8,  # Increased track line width
            )

        # Add start/finish line as a simple black line with reduced width
        start_x, start_z = x_smooth[0], z_smooth[0]
        next_x, next_z = x_smooth[1], z_smooth[1]
        dx, dz = next_x - start_x, next_z - start_z
        perp_dx, perp_dz = -dz, dx  # Rotate 90 degrees to find perpendicular direction
        marker_length = 15
        marker_x = [
            start_x - perp_dx * marker_length / np.hypot(perp_dx, perp_dz),
            start_x + perp_dx * marker_length / np.hypot(perp_dx, perp_dz),
        ]
        marker_z = [
            start_z - perp_dz * marker_length / np.hypot(perp_dx, perp_dz),
            start_z + perp_dz * marker_length / np.hypot(perp_dx, perp_dz),
        ]
        ax.plot(marker_x, marker_z, color="black", linewidth=6)  # Reduced line width

        # Set title with shadow effect similar to track name
        title_x, title_y = 0.5, 1.05
        # Shadow
        ax.text(
            title_x,
            title_y - 0.003,
            title,
            fontsize=28,
            color="black",
            fontproperties=impact_font,
            ha="center",
            va="top",
            transform=ax.transAxes,
        )
        # Main title
        ax.text(
            title_x,
            title_y,
            title,
            fontsize=28,
            color="white",
            fontproperties=impact_font,
            ha="center",
            va="top",
            transform=ax.transAxes,
        )
        ax.axis("equal")
        ax.axis("off")

        # Add color bar to represent comparison between drivers
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=ax, orientation="vertical", pad=0.02, aspect=25)

        max_driver_name_length = max(len(driver1), len(driver2))
        cbar.ax.set_ylabel(
            f"{driver1.ljust(max_driver_name_length)} (faster)        {driver2.rjust(max_driver_name_length)} (faster)",
            fontsize=16,
            color="white",
            fontproperties=impact_font,
            labelpad=20,
        )

        cbar.ax.tick_params(labelsize=12, colors="white")

        # Add track name and author text at the bottom with more distance
        text_x, text_y = (
            ax.get_xlim()[0],
            ax.get_ylim()[0] - 40,
        )  # Adjust to place text further at the bottom of the plot
        ax.text(
            text_x + 1,
            text_y - 1,
            name_of_track.upper(),
            color="black",
            fontsize=24,
            ha="left",
            fontproperties=impact_font,
        )
        ax.text(
            text_x,
            text_y,
            name_of_track.upper(),
            color="white",
            fontsize=24,
            ha="left",
            fontproperties=impact_font,
        )
        ax.text(
            text_x + 1,
            text_y - 60,
            f"by {author}".upper(),
            color="black",
            fontsize=17,
            ha="left",
            fontproperties=impact_font,
        )
        ax.text(
            text_x,
            text_y - 59,
            f"by {author}".upper(),
            color="#8B0000",
            fontsize=17,
            ha="left",
            fontproperties=impact_font,
        )

    # Plot for speed comparison
    fig, ax = plt.subplots(figsize=(10, 10), facecolor="dimgray")
    ax.set_facecolor("dimgray")
    plot_colored_track(
        ax,
        x_smooth,
        z_smooth,
        speed_diff,
        norm_speed,
        "Median Speed Comparison",
        "km/h",
    )
    plt.savefig(
        speed_output_path, dpi=300, bbox_inches="tight", pad_inches=0.5
    )  # Added padding to prevent text cropping

    # Plot for time comparison
    fig, ax = plt.subplots(figsize=(10, 10), facecolor="dimgray")
    ax.set_facecolor("dimgray")
    plot_colored_track(
        ax,
        x_smooth,
        z_smooth,
        time_diff,
        norm_time,
        "Minimum Time Comparison",
        "seconds",
    )
    plt.savefig(
        time_output_path, dpi=300, bbox_inches="tight", pad_inches=0.5
    )  # Added padding to prevent text cropping


def animate_race(df, df_track, output_path, name_of_track, author):
    # Load the local Impact font
    font_path = Path("track_coords/04B_09__.ttf")
    impact_font = fm.FontProperties(fname=font_path)

    # Extract track coordinates for each checkpoint
    track_points = df_track[["cp", "x", "y", "z"]].set_index("cp")

    # Filter to only include the first lap
    df_first_lap = df[df["lap"] == 1]

    # Assign a unique color to each driver
    driver_names = df_first_lap["name"].unique()[:2]
    print(driver_names)
    num_drivers = len(driver_names)
    colors = plt.cm.get_cmap(
        "tab20", num_drivers
    )  # Use tab20 colormap for up to 20 distinct colors

    # Prepare the figure
    fig, ax = plt.subplots(figsize=(10, 10), facecolor="dimgray")
    ax.set_facecolor("dimgray")
    ax.axis("equal")
    ax.axis("off")

    # Set the title and track name
    ax.text(
        0.5,
        1.05,
        f"{name_of_track.upper()} - Race Animation",
        fontsize=24,
        color="white",
        fontproperties=impact_font,
        ha="center",
        va="top",
        transform=ax.transAxes,
    )
    ax.text(
        0.5,
        1.02,
        f"by {author}",
        fontsize=16,
        color="#8B0000",
        fontproperties=impact_font,
        ha="center",
        va="top",
        transform=ax.transAxes,
    )

    # Smooth the track using splprep and splev
    x_middle_adjusted = track_points["x"]
    z_middle_adjusted = track_points["z"]
    x_closed = np.append(x_middle_adjusted, x_middle_adjusted.iloc[0])
    z_closed = np.append(z_middle_adjusted, z_middle_adjusted.iloc[0])

    # Interpolate the track for smoothness
    tck, u = splprep([x_closed, z_closed], s=0)
    unew = np.linspace(0, 1, 1000)  # Increase the number of points for a smooth curve
    x_smooth, z_smooth = splev(unew, tck)

    # Draw the track
    ax.plot(x_smooth, z_smooth, color="white", linewidth=2)

    # Prepare driver point placeholders and a dictionary to store their positions
    driver_points = {
        driver: ax.plot([], [], "o", color=colors(i), markersize=12)[0]
        for i, driver in enumerate(driver_names)
    }

    # Berechne die kumulative Zeit für jeden Fahrer basierend auf der Zeit zwischen den Checkpoints
    cumulative_times = {}
    for driver in driver_names:
        driver_data = df_first_lap[df_first_lap["name"] == driver]
        cumulative_time = 0
        cumulative_times[driver] = [0]
        for time in driver_data["time"]:
            cumulative_time += time
            cumulative_times[driver].append(cumulative_time)

    # Zeit-Skalierung: 10x schneller als die tatsächliche Zeit
    speed_factor = 10.0

    # Set the animation time range to match the longest cumulative time divided by the speed factor
    total_time = max(max(times) for times in cumulative_times.values())
    frames = int(total_time / speed_factor * 30)  # 30 frames per second

    print(cumulative_times)

    def update(frame):
        # Berechne die aktuelle Zeit im Rennen (skaliert durch den Geschwindigkeitsfaktor)
        current_time = frame * speed_factor / 30

        for driver in driver_names:
            driver_data = df_first_lap[df_first_lap["name"] == driver].reset_index()
            times = cumulative_times[driver]

            # Finde den aktuellen Abschnitt basierend auf der kumulativen Zeit
            current_cp_idx = np.searchsorted(times, current_time, side="right") - 1

            # Grenzwertprüfung, um sicherzustellen, dass der Index innerhalb der Grenzen liegt
            if current_cp_idx < 0:
                continue

            # Wenn `current_cp_idx` der letzte Checkpoint ist, setze den Fahrer einfach auf den letzten Punkt
            if current_cp_idx >= len(driver_data) - 1:
                last_cp = driver_data.iloc[-1]["cp"]
                pos = track_points.loc[last_cp][["x", "z"]]
                driver_points[driver].set_data([pos["x"]], [pos["z"]])
                continue

            # Berechne, wie weit entlang des aktuellen Abschnitts der Fahrer ist (0-1)
            segment_start_time = times[current_cp_idx]
            segment_end_time = times[current_cp_idx + 1]
            fraction = (current_time - segment_start_time) / (
                segment_end_time - segment_start_time
            )

            # Interpoliere die Position des Fahrers basierend auf dem aktuellen Abschnitt
            cp1 = driver_data.iloc[current_cp_idx]["cp"]
            cp2 = driver_data.iloc[current_cp_idx + 1]["cp"]
            pos1 = track_points.loc[cp1][["x", "z"]]
            pos2 = track_points.loc[cp2][["x", "z"]]

            # Lineare Interpolation für die Fahrerposition
            x = pos1["x"] + fraction * (pos2["x"] - pos1["x"])
            z = pos1["z"] + fraction * (pos2["z"] - pos1["z"])

            # Aktualisiere die Position des Fahrers
            driver_points[driver].set_data([x], [z])
            with open("logfile.txt", "a") as log_file:
                log_file.write(
                    "current_time: "
                    + str(current_time)
                    + " | current_cp_idx: "
                    + str(current_cp_idx)
                    + " | segment_start_time: "
                    + str(segment_start_time)
                    + " | segment_end_time: "
                    + str(segment_end_time)
                    + " | fraction: "
                    + str(fraction)
                    + " | cp1: "
                    + str(cp1)
                    + " | cp2: "
                    + str(cp2)
                    + " | pos1: (x: "
                    + str(pos1["x"])
                    + ", z: "
                    + str(pos1["z"])
                    + ") | pos2: (x: "
                    + str(pos2["x"])
                    + ", z: "
                    + str(pos2["z"])
                    + ") | x: "
                    + str(x)
                    + " | z: "
                    + str(z)
                    + "\n"
                )

        return list(driver_points.values())

    # Create the animation
    try:
        anim = FuncAnimation(fig, update, frames=frames, blit=True, interval=1000 / 30)

        # Check if output directory is writable
        output_dir = os.path.dirname(output_path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Add legend to the plot
        legend_handles = [
            plt.Line2D([0], [0], color=colors(i), lw=4, label=driver)
            for i, driver in enumerate(driver_names)
        ]
        ax.legend(
            handles=legend_handles,
            loc="upper right",
            bbox_to_anchor=(1.15, 1),
            title="Drivers",
            prop=impact_font,
        )

        # Save the animation
        anim.save(output_path, writer="ffmpeg", dpi=300)
        print(f"Animation successfully saved to {output_path}")

    except FileNotFoundError:
        print(
            "FFmpeg not found. Please make sure FFmpeg is installed and available in your PATH."
        )
    except RuntimeError as e:
        print(f"An error occurred while saving the animation: {e}")
