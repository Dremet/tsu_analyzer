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

# The first argument is always the script name, so the second argument (index 1) is the file path
file_path = sys.argv[1]
name_of_track = sys.argv[2]
author = sys.argv[3]

track_data_df = pd.read_csv(file_path)

# Load the local Impact font
font_path = Path(
    "track_coords/Impact.ttf"
)  # Replace with the actual path to your Impact font file
impact_font = fm.FontProperties(fname=font_path)
impact_font.get_name()

# Fülle fehlende Werte in der "middle"-Spalte mit dem Standardwert 0.5
track_data_df["middle"] = track_data_df["middle"].fillna(0.5)

# Berechne die angepasste Mitte basierend auf der "middle" Spalte
x_middle_adjusted = track_data_df["x1"] + track_data_df["middle"] * (
    track_data_df["x2"] - track_data_df["x1"]
)
z_middle_adjusted = track_data_df["z1"] + track_data_df["middle"] * (
    track_data_df["z2"] - track_data_df["z1"]
)

# Schließe die Kurve, indem der erste Punkt am Ende hinzugefügt wird
x_closed = np.append(x_middle_adjusted, x_middle_adjusted.iloc[0])
z_closed = np.append(z_middle_adjusted, z_middle_adjusted.iloc[0])

# Interpolation mit Splines auf den geschlossenen Datensatz
tck, u = splprep([x_closed, z_closed], s=0)  # s=0 für genaue Anpassung
unew = np.linspace(0, 1, 1000)  # hohe Dichte für glatte Kurve
x_smooth, z_smooth = splev(unew, tck)

# Erstellen der Grafik
fig = plt.figure(
    figsize=(10, 10), facecolor="dimgray"
)  # Hintergrundfarbe auf dunkelgrau setzen
ax = fig.add_subplot(111)
ax.set_facecolor("dimgray")

# Zeichne die Strecke doppelt so breit in Weiß
ax.plot(x_smooth, z_smooth, color="white", linewidth=4)

# Calculate the angle of the track at the start point
start_x, start_z = x_smooth[0], z_smooth[0]
next_x, next_z = x_smooth[1], z_smooth[1]
dx, dz = next_x - start_x, next_z - start_z

# Find the perpendicular direction for the marker
perp_dx, perp_dz = -dz, dx  # Rotate 90 degrees
marker_length = 10  # Length of the marker
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

# Text oben links mit Schatten und Umrandung
text_x, text_y = -440, 480  # Höhere Position für mehr Abstand zur Strecke
# Schatten und Umrandung für name_of_track
ax.text(
    text_x + 1,
    text_y - 1,
    name_of_track.upper(),
    color="black",
    fontsize=20,
    ha="left",
    font=font_path,
)
ax.text(
    text_x,
    text_y,
    name_of_track.upper(),
    color="white",
    fontsize=20,
    ha="left",
    font=font_path,
)

# Anpassung für "by {author}" in #8B0000 mit schwarzer Umrandung
ax.text(
    text_x + 1,
    text_y - 35,
    f"by {author}".upper(),
    color="black",
    fontsize=17,
    ha="left",
    font=font_path,
)  # Schwarzer Rand
ax.text(
    text_x,
    text_y - 34,
    f"by {author}".upper(),
    color="#8B0000",
    fontsize=17,
    ha="left",
    font=font_path,
)  # Dunkelrot

# Füge den Text unten rechts hinzu, kursiv und im selben Stil wie "Laguna Seca Raceway v1.02"
# ax.text(
#     420,
#     -420,
#     "visit tsura.org and join our discord",
#     color="white",
#     fontsize=12,
#     ha="right",
#     style="italic",
#     weight="bold",
#     bbox=dict(facecolor="dimgray", edgecolor="black", pad=2),
# )  # Hintergrund für bessere Lesbarkeit

# Entferne Achsen und setze gleiche Skalierung
ax.axis("equal")
ax.axis("off")

name_of_track = name_of_track.replace(" ", "_")

# Speichern des finalen Bildes mit den gewünschten Anpassungen
plt.savefig(
    f"track_coords/images/{name_of_track}_{author}.png",
    dpi=300,
    bbox_inches="tight",
    pad_inches=0,
)
# plt.show()
