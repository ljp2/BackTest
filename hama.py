import platform
import pandas as pd
from pandas import DataFrame as DF
from utils import ExponentialSmoothing as ES
from ha import HA

class HAMA:
    def __init__(self) -> None:
        self.ha = HA()
        self.ohlcbars = DF()
        self.smooth_ohlcbars = DF()
        self.hamabars = DF()
        
        self.periodOpen  = 10
        self.periodHigh  = 10
        self.periodLow  =  10
        self.periodClose = 10
        
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
