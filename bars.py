import platform
import pandas as pd
from pandas import DataFrame as DF
import numpy as np
from datetime import datetime

from utils import ExponentialSmoothing as ES

class OHLC_bar:
    def __init__(self, T, O, H, L, C, V=None) -> None:
        data = {'T': [T], 'O': [O], 'H': [H], 'L': [L], 'C': [C], 'V': [V]}
        df = DF(data)
        df.set_index('T', inplace=True)

class OHLC:
    def __init__(self, x:any) -> None:
        self.ohlcbars = DF()

    def addBar(self, t, O, H, L, C, V=None):
        ohlcbar = OHLC_bar(t, O, H, L, C, V)
        self.ohlcbars.append(ohlcbar)
        return ohlcbar
                                  

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
    
    def calculate_first_heiken_ashi(self, ohlc_bar: DF) -> DF:
        """
        Calulates the first HA bar.

        Args:
            ohlc_bar (DF): _description_

        Returns:
            DF: _description_
        """
        ohlc_bar["HA_Close"] = (ohlc_bar["Open"] + ohlc_bar["High"] + ohlc_bar["Low"] + ohlc_bar["Close"]) / 4
        ohlc_bar["HA_Open"] = ohlc_bar["Open"]
        ohlc_bar["HA_High"] = ohlc_bar[["High", "HA_Open", "HA_Close"]].max(axis=1)
        ohlc_bar["HA_Low"] = ohlc_bar[["Low", "HA_Open", "HA_Close"]].min(axis=1)
        ha_bar = ohlc_bar[["HA_Open", "HA_High", "HA_Low", "HA_Close"]]
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
    

class HAMA:
    def __init__(self) -> None:
        self.ha = HA()
        self.ohlcbars = DF()
        self.smooth_ohlcbars = DF()
        self.hamabars = DF()
        
        self.periodOpen  = 3
        self.periodHigh  = 3
        self.periodLow  =  3
        self.periodClose = 3
        
        # self.exOpen = ES(self.periodOpen)
        self.exOpen = ES(length=3)
        self.exHigh = ES(length=self.periodHigh)
        self.exLow = ES(length=self.periodLow)
        self.exClose = ES(length=self.periodClose)
        
        
    def addBar(self, ohlcbar:DF):
        self.ohlcbars = pd.concat([self.ohlcbars, ohlcbar])
        O,H,L,C,_ = ohlcbar.iloc[0].values
        nO = self.exOpen.update(O)
        nH = self.exHigh.update(H)
        nL = self.exLow.update(L)
        nC = self.exClose.update(C)
        smooth_olhc_bar =  pd.DataFrame([[nO,nH,nL,nC]], index=ohlcbar.index,  columns=["Open", "High", "Low", "Close"] )
        new_hama_bar = self.ha.addBar(smooth_olhc_bar)
        return new_hama_bar

        

# if __name__ == "__main__":
#     import arrivals
#     barfilename = "20231130"
#     filedirectory = "~/Data" if platform.system() == "Darwin" else "c:/Data"
#     filepath = f"{filedirectory}/{barfilename}.csv"
#     df = pd.read_csv(filepath, index_col=0, parse_dates=True)
#     arrivals = arrivals.Arrivals(df)
#     hama = HAMA()

#     while arrivals.waitforarrival() is not None:
#         newbar = arrivals.arrival
#         o,h,l,c,_ = newbar.iloc[0].values
#         newhamabar = hama.addBar(newbar)
#         nO,nH,nL,nC = newhamabar.iloc[0].values
#         print(o,h,l,c)
#         print(nO,nH,nL,nC)
#         print()


        
   
