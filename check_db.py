import sqlite3

conn = sqlite3.connect('geoai_recovered.db')
cur = conn.cursor()

cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cur.fetchall()
print("Tables:", tables)

for t in tables:
    table_name = t[0]
    try:
        cur.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cur.fetchone()[0]
        print(f"{table_name}: {count} rows")
    except Exception as e:
        print(f"{table_name}: error - {e}")

conn.close()
