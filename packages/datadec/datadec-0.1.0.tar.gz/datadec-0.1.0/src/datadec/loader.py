from pathlib import Path
from typing import Dict, Optional

import pandas as pd

from datadec.paths import DataDecidePaths


class DataFrameLoader:
    def __init__(self, paths: Optional[DataDecidePaths] = None):
        self._cache: Dict[str, pd.DataFrame] = {}
        self.paths: DataDecidePaths = paths if paths else DataDecidePaths()

    @property
    def cached_dataframes(self) -> list[str]:
        return list(self._cache.keys())

    def possible_dataframes(self) -> list[str]:
        return list(self.paths.available_dataframes)

    def written_dataframes(self) -> list[str]:
        written_dataframes = []
        for df_name in self.possible_dataframes():
            maybe_path = self.paths.get_existing_path(df_name)
            if maybe_path is not None:
                written_dataframes.append(df_name)
        return written_dataframes

    def set_name(self, name: str, df: pd.DataFrame) -> None:
        self._cache[name] = df

    def load_path(self, path: Path, name: Optional[str] = None) -> pd.DataFrame:
        key = name if name is not None else str(path)
        if key not in self._cache:
            self._cache[key] = pd.read_parquet(path)
        return self._cache[key]

    def load_name(self, name: str) -> pd.DataFrame:
        if not self.paths.check_name_in_paths(name):
            if not self.is_cached(name):
                raise ValueError(f"Unknown dataframe '{name}'")
            return self._cache[name]
        path = self.paths.get_path(name)
        return self.load_path(path, name)

    def is_cached(self, cache_key: str) -> bool:
        return cache_key in self._cache

    def clear_cache(self, cache_key: Optional[str] = None) -> None:
        if cache_key is None:
            self._cache.clear()
        else:
            self._cache.pop(cache_key, None)

    def get_cache_size(self) -> int:
        return len(self._cache)
