#!/bin/sh

# Pfad zur eventstats.json Datei
EVENT_STATS_FILE="./eventstats.json"
SESSION_STATS_FILE="./sessionstats.json"

# Verzeichnis, in das die Datei verschoben werden soll
DEST_DIR=~/stat_files

# Stelle sicher, dass das Zielverzeichnis existiert
mkdir -p "$DEST_DIR"

# Versuche, den Streckennamen aus der JSON-Datei zu extrahieren
TRACK_NAME=$(jq -r '.level.name // empty' "$EVENT_STATS_FILE" 2>/dev/null | tr -d ' ')

# Erhalte den aktuellen Timestamp im gewünschten Format
CURRENT_TIMESTAMP=$(date "+%Y%m%d_%H%M%S")

# Basis für den neuen Dateinamen: Timestamp
NEW_FILE_NAME="${CURRENT_TIMESTAMP}"

# Füge den Streckennamen hinzu, falls vorhanden
if [ -n "$TRACK_NAME" ]; then
  NEW_FILE_NAME="${NEW_FILE_NAME}_${TRACK_NAME}"
fi

# Erweitere den Dateinamen um die Dateiendung
EVENT_FILE_NAME="${NEW_FILE_NAME}_event.json"
SESSION_FILE_NAME="${NEW_FILE_NAME}_session.json"

# Überprüfe, ob die Quelldatei existiert und nicht leer ist
if [ ! -s "$EVENT_STATS_FILE" ]; then
  echo "Warnung: Die Datei '$EVENT_STATS_FILE' ist leer oder existiert nicht. Es wird ein leeres Dokument verschoben."
fi

if [ ! -s "$SESSION_STATS_FILE" ]; then
  echo "Warnung: Die Datei '$SESSION_STATS_FILE' ist leer oder existiert nicht. Es wird ein leeres Dokument verschoben."
fi

# Verschiebe die eventstats.json Datei in das Zielverzeichnis mit dem neuen Dateinamen
mv "$EVENT_STATS_FILE" "$DEST_DIR/$EVENT_FILE_NAME"
echo "Event Stats Datei erfolgreich verschoben nach: $DEST_DIR/$EVENT_FILE_NAME"

mv "$SESSION_STATS_FILE" "$DEST_DIR/$SESSION_FILE_NAME"
echo "Session Stats Datei erfolgreich verschoben nach: $DEST_DIR/$SESSION_FILE_NAME"


# Now save to database (only for hotlapping)
# cd ~/tsu_analyzer
# /home/steam/.local/bin/pdm run python run.py "$DEST_DIR/$EVENT_FILE_NAME" &