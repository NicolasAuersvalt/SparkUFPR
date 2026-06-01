import sqlite3

conn = sqlite3.connect("crowd_sensing.db")

cursor = conn.cursor()

cursor.execute(
    "SELECT COUNT(*) FROM events"
)

print(cursor.fetchone())