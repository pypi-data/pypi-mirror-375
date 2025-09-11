import asyncio
from typing import List, Any, Dict

import dask
import dask.dataframe as dd

def _to_int_safe(x) -> int:
    """
    Convert scalar-like to int safely.
    Handles numpy scalars, pandas Series/DataFrame outputs.
    """
    if hasattr(x, "item"):        # numpy scalar, pandas scalar
        return int(x.item())
    if hasattr(x, "iloc"):        # Series-like
        return int(x.iloc[0])
    return int(x)

def dask_is_probably_empty(ddf: dd.DataFrame) -> bool:
    return getattr(ddf, "npartitions", 0) == 0 or len(ddf._meta.columns) == 0


def dask_is_empty_truthful(ddf: dd.DataFrame) -> bool:
    n = ddf.map_partitions(len).sum().compute()
    return int(n) == 0


def dask_is_empty(ddf: dd.DataFrame, *, sample: int = 4) -> bool:
    if dask_is_probably_empty(ddf):
        return True

    k = min(max(sample, 1), ddf.npartitions)
    probes = dask.compute(*[
        ddf.get_partition(i).map_partitions(len) for i in range(k)
    ])

    if any(_to_int_safe(n) > 0 for n in probes):
        return False
    if k == ddf.npartitions and all(_to_int_safe(n) == 0 for n in probes):
        return True

    return dask_is_empty_truthful(ddf)

class UniqueValuesExtractor:
    @staticmethod
    def _compute_to_list_sync(series) -> List[Any]:
        """Run in a worker thread when Dask-backed."""
        if hasattr(series, "compute"):
            return series.compute().tolist()
        return series.tolist()

    async def compute_to_list(self, series) -> List[Any]:
        # Offload potential Dask .compute() to a thread to avoid blocking the event loop
        return await asyncio.to_thread(self._compute_to_list_sync, series)

    async def extract_unique_values(self, df, *columns: str) -> Dict[str, List[Any]]:
        async def one(col: str):
            ser = df[col].dropna().unique()
            return col, await self.compute_to_list(ser)

        pairs = await asyncio.gather(*(one(c) for c in columns))
        return dict(pairs)