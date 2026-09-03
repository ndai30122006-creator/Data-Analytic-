"""Pandas ops skeleton (Plan 02)."""

OPS = {
    "fill_missing": lambda df, **p: df.fillna(p.get("value", 0)),
    "drop_duplicates": lambda df, **p: df.drop_duplicates(),
}
