"""Execution Context (P0/P1) — named dataframes + explicit inputs.

Moi step doc inputs tuong minh theo depends_on:
- depends_on rong  -> source dataframe (raw.*)
- 1 dep            -> dataframe cua step do
- nhieu dep        -> dict {step_id: dataframe} (chi op 'merge' / 'sql' nhan dict;
                      op pandas don le nhan dict se bao loi ro rang thay vi
                      lang le lay dep cuoi nhu ban cu)
"""

from typing import Dict, Union

import pandas as pd


class ExecutionContext:
    def __init__(self, source_df: pd.DataFrame):
        self.frames: Dict[str, pd.DataFrame] = {"source": source_df.copy()}

    def put(self, step_id: str, df: pd.DataFrame) -> None:
        self.frames[step_id] = df

    def resolve(self, step) -> Union[pd.DataFrame, Dict[str, pd.DataFrame]]:
        deps = list(step.depends_on or [])
        if not deps:
            return self.frames["source"]
        missing = [d for d in deps if d not in self.frames]
        if missing:
            raise ValueError(f"Step {step.id} depends_on chua co output: {missing}")
        if len(deps) == 1:
            return self.frames[deps[0]]
        return {d: self.frames[d] for d in deps}
