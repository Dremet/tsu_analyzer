import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from matplotlib import font_manager as fm
from scipy.interpolate import splprep, splev

if len(sys.argv) < 4:
    print(
        "Usage: pdm run python track_coords/print_track_map.py <path_to_csv_file> <name_of_track> <author>"
    )
    sys.exit(1)

file_path = sys.argv[1]
name_of_track = sys.argv[2]
author = sys.argv[3]

# Read the track data
track_data_df = pd.read_csv(file_path)

# Load the local Impact font
font_path = Path("track_coords/Impact.ttf")
impact_font = fm.FontProperties(fname=font_path)

# Fill missing "middle" values with 0.5
track_data_df["middle"] = track_data_df["middle"].fillna(0.5)

# Adjust the midpoint based on the "middle" factor
x_middle_adjusted = track_data_df["x1"] + track_data_df["middle"] * (
    track_data_df["x2"] - track_data_df["x1"]
)
z_middle_adjusted = track_data_df["z1"] + track_data_df["middle"] * (
    track_data_df["z2"] - track_data_df["z1"]
)

# Close the curve by adding the first point at the end
x_closed = np.append(x_middle_adjusted, x_middle_adjusted.iloc[0])
z_closed = np.append(z_middle_adjusted, z_middle_adjusted.iloc[0])

# Interpolate a smooth curve
tck, u = splprep([x_closed, z_closed], s=0)
unew = np.linspace(0, 1, 1000)
x_smooth, z_smooth = splev(unew, tck)

# Define the color-to-car mapping
color_to_car = {"#FF7F50": "Buick", "#7FFFD4": "Porsche", "#8A2BE2": "Toyota"}

# Read sector colors from the additional file
sector_colors_df = pd.read_csv("track_coords/sector_coloring/laguna_seca.csv")
num_sectors = len(sector_colors_df)

# Determine the indices for each sector
sector_indices = np.linspace(0, len(x_smooth), num_sectors + 1, dtype=int)

# Create the plot
fig = plt.figure(figsize=(10, 10), facecolor="dimgray")
ax = fig.add_subplot(111)
ax.set_facecolor("dimgray")

# Plot each sector with the corresponding color
for i in range(num_sectors):
    start_idx = sector_indices[i]
    end_idx = sector_indices[i + 1]
    color = sector_colors_df.iloc[i]["color"]
    ax.plot(
        x_smooth[start_idx:end_idx],
        z_smooth[start_idx:end_idx],
        color=color,
        linewidth=4,
    )

# Calculate the angle of the track at the start point for the perpendicular marker
start_x, start_z = x_smooth[0], z_smooth[0]
next_x, next_z = x_smooth[1], z_smooth[1]
dx, dz = next_x - start_x, next_z - start_z

# Perpendicular direction for the marker
perp_dx, perp_dz = -dz, dx
marker_length = 10
marker_x = [
    start_x - perp_dx * marker_length / np.hypot(perp_dx, perp_dz),
    start_x + perp_dx * marker_length / np.hypot(perp_dx, perp_dz),
]
marker_z = [
    start_z - perp_dz * marker_length / np.hypot(perp_dx, perp_dz),
    start_z + perp_dz * marker_length / np.hypot(perp_dx, perp_dz),
]

# Draw the perpendicular start/finish marker
ax.plot(marker_x, marker_z, color="white", linewidth=8)

# Add track name text with shadow
text_x, text_y = -440, 480
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

# Add author text in dark red with black outline
ax.text(
    text_x + 1,
    text_y - 40,
    f"by {author}".upper(),
    color="black",
    fontsize=17,
    ha="left",
    fontproperties=impact_font,
)
ax.text(
    text_x,
    text_y - 39,
    f"by {author}".upper(),
    color="#8B0000",
    fontsize=17,
    ha="left",
    fontproperties=impact_font,
)

# Create legend for car colors
legend_handles = [
    plt.Line2D([0], [0], color=color, lw=4, label=car)
    for color, car in color_to_car.items()
]
legend = ax.legend(
    handles=legend_handles,
    loc="upper right",
    bbox_to_anchor=(1.15, 1),
    title="Quickest Car",
)
plt.setp(
    legend.get_texts(), fontproperties=impact_font, fontsize=18
)  # Set font size for legend items
plt.setp(
    legend.get_title(), fontproperties=impact_font, fontsize=22
)  # Set font for legend title

# Remove axes and set equal aspect ratio
ax.axis("equal")
ax.axis("off")

# Adjust bbox_inches to "tight" for saving the plot with the legend
name_of_track = name_of_track.replace(" ", "_")
plt.savefig(
    f"track_coords/sector_images/{name_of_track}_{author}.png",
    dpi=300,
    bbox_inches="tight",
    pad_inches=0,
)
