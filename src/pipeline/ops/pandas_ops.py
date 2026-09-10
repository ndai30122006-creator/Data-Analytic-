"""Pandas ops — ETL mode (Plan 04)."""

import pandas as pd


def fill_missing(df: pd.DataFrame, column: str = None, method: str = "mean", value=None) -> pd.DataFrame:
    if column and column in df.columns:
        if method == "mean" and pd.api.types.is_numeric_dtype(df[column]):
            df[column] = df[column].fillna(df[column].mean())
        elif method == "median" and pd.api.types.is_numeric_dtype(df[column]):
            df[column] = df[column].fillna(df[column].median())
        elif method == "mode":
            df[column] = df[column].fillna(df[column].mode().iloc[0] if not df[column].mode().empty else value)
        else:
            df[column] = df[column].fillna(value)
    else:
        df = df.fillna(value if value is not None else 0)
    return df


def drop_duplicates(df: pd.DataFrame, subset=None) -> pd.DataFrame:
    return df.drop_duplicates(subset=subset)


def type_cast(df: pd.DataFrame, column: str, dtype: str) -> pd.DataFrame:
    if column in df.columns:
        try:
            df[column] = df[column].astype(dtype)
        except Exception:
            pass
    return df


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    return df


def derive_column(df: pd.DataFrame, name: str, expr: str) -> pd.DataFrame:
    # expr as python eval on df (simple) or SQL-like CASE
    try:
        # Try pandas eval
        df[name] = df.eval(expr)
    except Exception:
        # Fallback: create with NaN
        df[name] = None
    return df


def filter_rows(df: pd.DataFrame, query: str) -> pd.DataFrame:
    try:
        return df.query(query)
    except Exception:
        return df


def aggregate(df: pd.DataFrame, by: str, agg: str = "mean") -> pd.DataFrame:
    if by in df.columns:
        try:
            return df.groupby(by).agg(agg).reset_index()
        except Exception:
            return df
    return df


def merge(frames, how: str = "concat", on=None) -> pd.DataFrame:
    """Combine explicit multi-inputs (P1) — receives dict {step_id: df} from ExecutionContext.

    - how="concat" (default): stack frames vertically (ignore_index).
    - how="merge": sequential join on column(s) `on` (str or list).
    """
    import functools

    if isinstance(frames, pd.DataFrame):
        return frames
    if not isinstance(frames, dict) or not frames:
        raise ValueError("merge needs a non-empty dict {step_id: dataframe}")
    dfs = list(frames.values())
    if how == "merge":
        if not on:
            raise ValueError("merge how='merge' needs params 'on' (join column)")
        return functools.reduce(lambda l, r: pd.merge(l, r, on=on), dfs)
    return pd.concat(dfs, ignore_index=True)


OPS = {
    "fill_missing": fill_missing,
    "drop_duplicates": drop_duplicates,
    "type_cast": type_cast,
    "standardize_columns": standardize_columns,
    "derive_column": derive_column,
    "filter": filter_rows,
    "aggregate": aggregate,
    "merge": merge,
}
