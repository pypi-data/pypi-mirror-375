from pathlib import Path
from typing import Optional


class DataDecidePaths:
    def __init__(self, data_dir: str = "./data"):
        self.data_dir = Path(data_dir) / "datadecide"
        self.dataset_dir = self.data_dir / "datasets"
        self.dataset_dir.mkdir(parents=True, exist_ok=True)

        self.dataframes = {
            "ppl_raw": "ppl_eval",
            "dwn_raw": "downstream_eval",
            "dwn_metrics_expanded": "dwn_metrics_expanded",
            "ppl_dwn_merged": "ppl_dwn_merged",
            "ppl_parsed": "ppl_eval_parsed",
            "dwn_parsed": "downstream_eval_parsed",
            "full_eval_raw": "full_eval_raw",
            "full_eval": "full_eval",
            "mean_eval": "mean_eval",
            "std_eval": "std_eval",
        }

        package_root = Path(__file__).parent
        self.ds_details_csv_path = package_root / "data" / "dataset_features.csv"

    @property
    def available_dataframes(self) -> list[str]:
        return list(self.dataframes.keys())

    def check_name_in_paths(self, name: str) -> bool:
        return name in self.dataframes

    def get_path(self, name: str) -> Path:
        if name not in self.dataframes:
            available = ", ".join(sorted(self.dataframes.keys()))
            raise ValueError(f"Unknown dataframe '{name}'. Available: {available}")
        return self.data_dir / f"{self.dataframes[name]}.parquet"

    def get_existing_path(self, name: str) -> Optional[Path]:
        path = self.get_path(name)
        if not path.exists():
            return None
        return path

    def parquet_path(self, name: str) -> Path:
        return self.data_dir / f"{name}.parquet"

    def dataset_path(self, max_params_str: str) -> Path:
        return self.dataset_dir / f"dataset_{max_params_str}.pkl"
