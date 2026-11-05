import pandas as pd, numpy as np, pyarrow.parquet as pq
def load(cols=None):
    t=pq.read_table("req.parquet", columns=cols, read_dictionary=[c for c in ["type","dept","status","origin"] if cols is None or c in cols])
    return t.to_pandas()
