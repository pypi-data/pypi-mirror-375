from __future__ import annotations
import pandas as pd
import numpy as np
from ._core import detect_types, ensure_dataframe

def clean(
    df: pd.DataFrame,
    impute: str = "median",         # "median" | "mean"
    encode: str = "auto",           # "auto" | "none"
    drop_leaky: list[str] | None = None,
    datetime_auto: bool = True,
) -> pd.DataFrame:
    """Quick cleaning with sane defaults.
    
    - Impute numeric with median/mean
    - Impute categorical with most frequent
    - One-hot encode categoricals if encode='auto' (drop_first)
    - Attempt to parse likely datetime columns if datetime_auto=True
    """
    df = ensure_dataframe(df)
    df = df.copy()
    
    # Drop leaky columns if requested
    if drop_leaky:
        for c in drop_leaky:
            if c in df.columns:
                df = df.drop(columns=[c])
    
    # Try datetime inference for object columns that look like dates
    if datetime_auto:
        for col in df.select_dtypes(include=['object']).columns:
            try:
                parsed = pd.to_datetime(df[col], errors="raise", utc=False, infer_datetime_format=True)
                # consider it datetime if at least 80% successfully parsed
                success_ratio = parsed.notna().mean()
                if success_ratio > 0.8:
                    df[col] = parsed
            except Exception:
                pass
    
    num_cols, cat_cols, dt_cols = detect_types(df)
    
    # Impute numeric
    for c in num_cols:
        if impute == "median":
            fill_value = df[c].median()
        elif impute == "mean":
            fill_value = df[c].mean()
        else:
            raise ValueError("impute must be 'median' or 'mean'")
        df[c] = df[c].fillna(fill_value)
    
    # Impute categorical
    for c in cat_cols:
        mode = df[c].mode(dropna=True)
        fill_value = mode.iloc[0] if not mode.empty else ""
        df[c] = df[c].fillna(fill_value)
    
    # Encoding
    if encode == "auto" and cat_cols:
        df = pd.get_dummies(df, columns=cat_cols, drop_first=True)
    elif encode == "none":
        pass
    else:
        if encode not in {"auto", "none"}:
            raise ValueError("encode must be 'auto' or 'none'")
    
    return df
