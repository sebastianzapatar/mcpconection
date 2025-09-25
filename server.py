import os
import psycopg2
from dotenv import load_dotenv


from mcp.server.fastmcp import FastMCP  

load_dotenv()
mcp = FastMCP("mcp-ventas")

def get_conn():
    return psycopg2.connect(
        host=os.getenv("PG_HOST", "localhost"),
        port=int(os.getenv("PG_PORT", "5432")),
        dbname=os.getenv("PG_DB", "ventasdb"),
        user=os.getenv("PG_USER", "postgres"),
        password=os.getenv("PG_PASSWORD", "123"),
    )

@mcp.tool()
def total_ventas_ultimo_mes() -> float:
    """
    Devuelve el total de ventas del mes anterior (monto acumulado).
    """
    sql = """
    SELECT COALESCE(SUM(monto),0) AS total
    FROM ventas
    WHERE fecha >= date_trunc('month', CURRENT_DATE) - INTERVAL '1 month'
      AND fecha <  date_trunc('month', CURRENT_DATE);
    """
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql)
        (total,) = cur.fetchone()
        return float(total)

@mcp.tool()
def ventas_por_dia_ultimos_n_dias(n:int=30) -> list[dict]:
    """
    Devuelve ventas por día para los últimos N días (default: 30).
    """
    sql = """
    SELECT fecha, SUM(monto) AS total_dia
    FROM ventas
    WHERE fecha >= CURRENT_DATE - INTERVAL %s
    GROUP BY fecha
    ORDER BY fecha;
    """
    interval = f'{n} days'
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, (interval,))
        rows = cur.fetchall()
        return [{"fecha": str(r[0]), "total_dia": float(r[1])} for r in rows]


if __name__ == "__main__":
    import datetime, os, sys, traceback
    try:
        # Log a archivo (opcional)
        with open("mcp_boot.log", "a", encoding="utf-8") as f:
            f.write(f"[{datetime.datetime.now()}] MCP starting. CWD={os.getcwd()}\n")

        # NUNCA imprimir a stdout: usar stderr
        print("MCP server inicializando… (esperando cliente MCP por stdio)", file=sys.stderr, flush=True)

        mcp.run(transport="stdio")
    except Exception:
        with open("mcp_error.log", "a", encoding="utf-8") as f:
            f.write(f"[{datetime.datetime.now()}]\n{traceback.format_exc()}\n")
        raise

