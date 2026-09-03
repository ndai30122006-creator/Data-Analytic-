"""SQL ops — ELT mode on DuckDB (Plan 04)."""


def run_sql(conn, query: str, prev: str = ""):
    q = query.replace("{{prev}}", prev)
    return conn.execute(q).fetchdf()


OPS = {"sql": run_sql}
OPS_SQL = OPS
