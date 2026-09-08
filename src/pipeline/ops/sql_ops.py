"""SQL ops — ELT mode on DuckDB (Plan 04)."""

import re

_BLOCKED = re.compile(
    r"\b(drop|delete|insert|update|alter|create|attach|detach|copy|pragma|vacuum|checkpoint|install|load)\b",
    re.IGNORECASE,
)


def run_sql(conn, query: str, prev: str = ""):
    if not query or not isinstance(query, str):
        raise ValueError("SQL query is required")
    q = query.replace("{{prev}}", prev).strip()
    if ";" in q:
        raise ValueError("Multiple SQL statements are not allowed")
    if not re.match(r"^(select|with)\b", q, re.IGNORECASE):
        raise ValueError("Only SELECT/WITH queries are allowed in sql op")
    if _BLOCKED.search(q):
        raise ValueError("DDL/DML statements are not allowed in sql op")
    return conn.execute(q).fetchdf()


OPS = {"sql": run_sql}
OPS_SQL = OPS
