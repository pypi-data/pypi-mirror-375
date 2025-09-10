"""
Non-lookahead bias range bar construction from Binance aggTrades data.
"""

from .range_bars import iter_range_bars_from_aggtrades
from .data_fetcher import UMFuturesDataFetcher, fetch_um_futures_aggtrades
from .parquet_converter import ParquetConverter, aggtrades_to_parquet, range_bars_to_parquet

__version__ = "0.2.1"
__all__ = [
    "iter_range_bars_from_aggtrades", 
    "UMFuturesDataFetcher", 
    "fetch_um_futures_aggtrades",
    "ParquetConverter",
    "aggtrades_to_parquet",
    "range_bars_to_parquet"
]