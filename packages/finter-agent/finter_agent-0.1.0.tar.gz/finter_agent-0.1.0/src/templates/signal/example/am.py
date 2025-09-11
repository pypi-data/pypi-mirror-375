from datetime import datetime

import numpy as np
import pandas as pd
from finter import BaseSignal, SignalConfig, SignalParams


class Alpha(BaseSignal):
    """Your strategy description here"""

    def set_params(self):
        self.params = SignalParams(
            window_size={
                "default": 20,
                "range": [10, 20, 30, 60],
                "description": "Rolling window size",
            },
            threshold={
                "default": 0.05,
                "range": [0.01, 0.03, 0.05, 0.1],
                "description": "Signal threshold",
            },
        )

    def set_config(self):
        self.configs = SignalConfig(
            universe="kr_stock",
            first_date=20150101,
            data_list=["close", "volume"],
            data_lookback=self.params.window_size,
            signal_lookback=self.params.window_size,
        )

    def step(self, t: datetime) -> np.ndarray:
        """Generate signals at time t"""
        # Get data window
        data = self.stock_data.window(t, window=self.configs.data_lookback)

        # Example: Simple momentum strategy
        current_prices = data[-1, :, 0]  # Latest close prices
        past_prices = data[0, :, 0]  # Earliest close prices
        returns = current_prices / past_prices - 1

        # Generate signals
        signals = np.where(
            returns > self.params.threshold,
            1.0,
            np.where(returns < -self.params.threshold, -1.0, 0.0),
        )

        return -signals

    def post_process(self, position: pd.DataFrame) -> pd.DataFrame:
        """Optional post-processing"""
        return position.rolling(window=self.configs.signal_lookback).mean()
