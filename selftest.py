# selftest.py (prueba directa sin MCP)
import os, psycopg2
from dotenv import load_dotenv
load_dotenv()

conn = psycopg2.connect(
    host=os.getenv("PG_HOST", "localhost"),
    port=int(os.getenv("PG_PORT", "5432")),
    dbname=os.getenv("PG_DB", "ventasdb"),
    user=os.getenv("PG_USER", "postgres"),
    password=os.getenv("PG_PASSWORD", "secret"),
)
cur = conn.cursor()
cur.execute("""
    SELECT COALESCE(SUM(monto),0) AS total
    FROM ventas
    WHERE fecha >= date_trunc('month', CURRENT_DATE) - INTERVAL '1 month'
      AND fecha <  date_trunc('month', CURRENT_DATE);
""")
print("Total mes anterior:", cur.fetchone()[0])
cur.close()
conn.close()
