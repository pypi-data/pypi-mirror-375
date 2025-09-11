from __future__ import annotations
import pandas as pd
from sklearn import datasets as skds
from pathlib import Path

def load(source: str, **kwargs) -> pd.DataFrame:
    """Load a dataset quickly.
    
    Parameters
    ----------
    source : str
        One of: "iris", "wine", "breast_cancer", "csv", "parquet"
    kwargs : dict
        For files, provide path=...
    """
    source = (source or "").lower()
    if source in {"iris", "wine", "breast_cancer"}:
        loader = {
            "iris": skds.load_iris,
            "wine": skds.load_wine,
            "breast_cancer": skds.load_breast_cancer,
        }[source]
        bunch = loader(as_frame=True)
        df = bunch.frame.copy()
        # Normalize target name
        if "target" not in df.columns and bunch.target is not None:
            df["target"] = bunch.target
        return df
    elif source in {"csv", "parquet"}:
        path = kwargs.get("path")
        if not path:
            raise ValueError("For file sources, pass path='<file>'")
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"No such file: {path}")
        if source == "csv":
            return pd.read_csv(path)
        else:
            return pd.read_parquet(path)
    else:
        raise ValueError("Unknown source. Use 'iris', 'wine', 'breast_cancer', 'csv', or 'parquet'.")
