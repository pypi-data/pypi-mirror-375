"""DataDecide library for downloading and processing ML experiment datasets."""

import warnings

# Suppress urllib3 LibreSSL warning on macOS
warnings.filterwarnings("ignore", message="urllib3 v2 only supports OpenSSL")

from datadec.data import DataDecide  # noqa: E402

__all__ = ["DataDecide"]
