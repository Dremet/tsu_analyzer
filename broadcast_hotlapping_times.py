import os
import psycopg2
from psycopg2.extras import DictCursor
from dotenv import load_dotenv

# Lade Umgebungsvariablen aus der .env-Datei
load_dotenv()

# Hole die PostgreSQL-Verbindungs-URL aus der Umgebungsvariable
postgres_url = os.getenv("TSU_HOTLAPPING_POSTGRES_URL")

if not postgres_url:
    raise ValueError(
        "Die Umgebungsvariable TSU_HOTLAPPING_POSTGRES_URL ist nicht gesetzt!"
    )


def format_seconds_to_time(seconds):
    minutes = int(seconds // 60)
    remaining_seconds = seconds % 60
    return f"{minutes}:{remaining_seconds:06.3f}"


# Funktion zur Verbindung und Abfrage der Datenbank
def query_database():
    results = []

    try:
        # Verbindung zur Datenbank herstellen
        with psycopg2.connect(postgres_url) as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                # SQL-Abfrage ausführen
                sql_query = """
                    SELECT 
                        driver,
                        best_lap_seconds,
                        car
                    FROM (
                        SELECT 
                            lr.id AS lap_result_id,
                            lr.lap_time AS best_lap_seconds,
                            d.name AS driver,
                            d.steam_id AS steam_id,
                            c.name AS car,
                            lr.created_at AS time_of_best_lap,
                            ROW_NUMBER() OVER (PARTITION BY d.steam_id ORDER BY lr.lap_time ASC) AS rn
                        FROM tsu.lap_results lr
                        JOIN tsu.event_results er ON lr.event_result_id = er.id
                        JOIN tsu.events e ON er.event_id = e.id
                        JOIN tsu.drivers d ON er.driver_id = d.id
                        JOIN tsu.cars c ON er.car_id = c.id
                        WHERE e.id = (select max(id) from tsu.events)
                    ) subquery
                    WHERE rn = 1
                    order by best_lap_seconds asc, time_of_best_lap asc
                    limit 10
                    """
                cursor.execute(sql_query)

                # Ergebnisse Zeile für Zeile drucken
                for row in cursor:
                    results.append(dict(row))
    except psycopg2.Error as e:
        print(f"Ein Fehler ist aufgetreten: {e}")

    with open(
        "/home/steam/tsu_server/config/Scripts/event_end_generated.src", "w"
    ) as f:
        for i, result in enumerate(results, start=1):
            if i == 1:
                f.write("/broadcast ### Current Top 10 ###\n")

            driver = result["driver"] + ":"
            f.write(
                f"/broadcast {i}. {driver.ljust(20)} {format_seconds_to_time(result['best_lap_seconds'])} ({result['car']})\n"
            )


if __name__ == "__main__":
    query_database()
