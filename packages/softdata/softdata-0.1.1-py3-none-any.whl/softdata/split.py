from __future__ import annotations
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from ._core import is_discrete_series, ensure_dataframe

def split(
    df: pd.DataFrame,
    target: str,
    strategy: str = "auto",     # 'auto' | 'random' | 'stratified'
    test_size: float = 0.2,
    val_size: float = 0.1,
    random_state: int = 42,
):
    """Split into train/val/test with optional stratification.
    
    Returns
    -------
    (X_train, X_val, X_test, y_dict)
    y_dict has keys 'train', 'val', 'test'
    """
    df = ensure_dataframe(df)
    if target not in df.columns:
        raise ValueError(f"target '{target}' not in DataFrame")
    
    y = df[target].copy()
    X = df.drop(columns=[target]).copy()
    
    # Decide strategy
    if strategy == "auto":
        stratify = y if is_discrete_series(y, max_unique=20) else None
    elif strategy == "random":
        stratify = None
    elif strategy == "stratified":
        stratify = y
    else:
        raise ValueError("strategy must be 'auto', 'random', or 'stratified'")
    
    # First split: train+val vs test
    X_temp, X_test, y_temp, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=stratify
    )
    
    # Second split: train vs val (preserve original ratio)
    val_ratio = val_size / (1.0 - test_size)
    strat2 = y_temp if stratify is not None else None
    
    X_train, X_val, y_train, y_val = train_test_split(
        X_temp, y_temp, test_size=val_ratio, random_state=random_state, stratify=strat2
    )
    
    y_dict = {"train": y_train, "val": y_val, "test": y_test}
    return X_train.reset_index(drop=True), X_val.reset_index(drop=True), X_test.reset_index(drop=True), {k: v.reset_index(drop=True) for k, v in y_dict.items()}
