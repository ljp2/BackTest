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

        

if __name__ == "__main__":
    import arrivals
    barfilename = "20231130"
    filedirectory = "~/Data" if platform.system() == "Darwin" else "c:/Data"
    filepath = f"{filedirectory}/{barfilename}.csv"
    df = pd.read_csv(filepath, index_col=0, parse_dates=True)
    arrivals = arrivals.Arrivals(df)
    hama = HAMA()

    while arrivals.waitforarrival() is not None:
        newbar = arrivals.arrival
        o,h,l,c,_ = newbar.iloc[0].values
        newhamabar = hama.addBar(newbar)
        nO,nH,nL,nC = newhamabar.iloc[0].values
        print(o,h,l,c)
        print(nO,nH,nL,nC)

        
   
