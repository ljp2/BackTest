import pandas as pd
from pandas import DataFrame as DF

class HA:
    def __init__(self) -> None:
        self.habars = DF()

    def addBar(self, ohlc_bar:DF) -> DF:
        """
        Calulates, adds and returns first or next HA bar

        Args:
            ohlc_bar (DF): OHLC dataframe of len(1)

        Returns:
            DF of len(1) containing new HA bar
        """
        if len(self.habars) == 0:
            hadf = self.calculate_first_heiken_ashi(ohlc_bar)
        else:
            hadf = self.calculate_next_heiken_ashi(ohlc_bar)
        return hadf
    
    def calculate_first_heiken_ashi(self, xohlc_bar: DF) -> DF:
        """
        Calulates the first HA bar.

        Args:
            ohlc_bar (DF): _description_

        Returns:
            DF: _description_
        """
        ohlc_bar = xohlc_bar.iloc[[-1]]
        ohlc_bar["HA_Close"] = (ohlc_bar["Open"] + ohlc_bar["High"] + ohlc_bar["Low"] + ohlc_bar["Close"]) / 4
        ohlc_bar["HA_Open"] = ohlc_bar["Open"]
        ohlc_bar["HA_High"] = ohlc_bar[["High", "HA_Open", "HA_Close"]].max(axis=1)
        ohlc_bar["HA_Low"] = ohlc_bar[["Low", "HA_Open", "HA_Close"]].min(axis=1)
        ha_bar = ohlc_bar[["HA_Open", "HA_High", "HA_Low", "HA_Close"]].copy()
        ha_bar.columns = ["Open", "High", "Low", "Close"]
        self.habars = pd.concat([self.habars, ha_bar])
        return ha_bar
    
    def calculate_next_heiken_ashi(self, ohlc_bar: pd.DataFrame
    ):
        previous_ha_candle = self.habars.iloc[-1]
        previous_ha_open, previous_ha_close = previous_ha_candle[["Open", "Close"]]
        new_open, new_high, new_low, new_close = ohlc_bar[["Open", "High", "Low", "Close"]].iloc[0]
        avg_price = (new_open + new_high + new_low + new_close) / 4
        ha_open = (previous_ha_open + previous_ha_close) / 2
        ha_high = max(new_open, new_close, new_high, ha_open)
        ha_low = min(new_open, new_close, new_low, ha_open)
        ha_close = (avg_price + ha_open + ha_high + ha_low) / 4

        data_list = [ha_open, ha_high, ha_low, ha_close]
        ha_bar = pd.DataFrame(
            [data_list],
            index=ohlc_bar.index,
            columns=["Open", "High", "Low", "Close"],
        )
        self.habars = pd.concat([self.habars, ha_bar])
        return ha_bar