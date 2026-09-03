"""SQL ops skeleton — ELT on DuckDB (Plan 02)."""


def run_sql(conn, query: str, prev: str = ""):
    q = query.replace("{{prev}}", prev)
    return conn.execute(q).fetchdf()
