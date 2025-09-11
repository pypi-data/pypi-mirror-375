from __future__ import annotations
import pandas as _pd
import numpy as _np

def is_discrete_series(s, max_unique: int = 20) -> bool:
    try:
        nunique = s.nunique(dropna=True)
        return nunique <= max_unique
    except Exception:
        return False

def detect_types(df: _pd.DataFrame):
    num = df.select_dtypes(include=["number"]).columns.tolist()
    cat = df.select_dtypes(include=["object", "category", "bool"]).columns.tolist()
    dt = df.select_dtypes(include=["datetime64[ns]", "datetime64[ns, UTC]"]).columns.tolist()
    return num, cat, dt

def ensure_dataframe(obj) -> _pd.DataFrame:
    if isinstance(obj, _pd.DataFrame):
        return obj.copy()
    raise TypeError("Expected a pandas DataFrame.")
