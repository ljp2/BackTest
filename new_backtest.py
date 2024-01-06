import sys
import platform
import pandas as pd

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
from PyQt6 import QtCore, QtWidgets

import matplotlib
matplotlib.use('QtAgg')
import matplotlib.dates as mdates
from matplotlib.axes import Axes
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from ha import HA

class MyMainWindow(QMainWindow):
    def __init__(self, df):
        super().__init__()
        self.df = df
        self.bars = pd.DataFrame()
        self.habars = HA()
        self.current_i = 0
        self.i_last = len(df) - 1
        self.i_left = 0
        self.i_width = 389
        self.i_plot_shift_delta = 5
        self.i_right = self.i_left + self.i_width

        self.dfleft = self.df.index[0]
        self.dfright = self.df.index[self.i_last]
        self.dfhigh = self.df.High.max()
        self.dflow = self.df.Low.min()

        self.x_left = self.df.index[self.i_left]
        self.x_right = self.df.index[self.i_right]
        self.y_high = self.dfhigh
        self.y_low = self.dflow

        self.width = (self.df.index[1] - self.df.index[0]) * 0.6
        self.width2 = self.width * 0.1
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.figure = Figure()
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.layout.addWidget(self.canvas)
        self.layout.addWidget(NavigationToolbar(self.canvas, self))
        
        (self.ax1, self.ax2) = self.figure.subplots(2, 1, sharex=True, sharey=True)
        
        # Set titles
        self.figure.suptitle("BACKTESTING")
        self.ax1.set_title("Candles")
        self.ax2.set_title("HA")
        self.ax1.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        self.ax2.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        self.ax1.yaxis.tick_right()
        self.ax2.yaxis.tick_right()
        
        self.ax1.set_xlim(self.x_left, self.x_right)
        self.ax2.set_xlim(self.x_left, self.x_right)
        self.ax1.set_ylim(self.y_low, self.y_high)
        self.ax2.set_ylim(self.y_low, self.y_high)
        
        self.button = QPushButton("Push for Window")
        self.button.clicked.connect(self.handleNextBar)
        self.layout.addWidget(self.button)


    def plotBar(self, bardf: pd.DataFrame, ax:Axes):
        """Plots the bar directory on the candles (the upper) subplot

        Args:
            bardf (pd.DataFrame): a classic OHLCV bar
        """
        if (bardf.Close >= bardf.Open).any():
            ax.bar(
                bardf.index,
                bardf.Close - bardf.Open,
                self.width,
                bottom=bardf.Open,
                color="green",
            )
            ax.bar(
                bardf.index,
                bardf.High - bardf.Close,
                self.width2,
                bottom=bardf.Close,
                color="green",
            )
            ax.bar(
                bardf.index,
                bardf.Low - bardf.Open,
                self.width2,
                bottom=bardf.Open,
                color="green",
            )
        else:
            ax.bar(
                bardf.index,
                bardf.Close - bardf.Open,
                self.width,
                bottom=bardf.Open,
                color="red",
            )
            ax.bar(
                bardf.index,
                bardf.High - bardf.Open,
                self.width2,
                bottom=bardf.Open,
                color="red",
            )
            ax.bar(
                bardf.index,
                bardf.Low - bardf.Close,
                self.width2,
                bottom=bardf.Close,
                color="red",
            )
            
    def plotAllDF(self):
        self.ax1.plot(df.index, df.Close)
        self.ax2.plot(df.index, df.High)
        self.ax2.plot(df.index, df.Low)
        self.canvas.draw()
        
    def handleNextBar(self, e):
        bar = self.df.iloc[[self.current_i]]
        habar = self.habars.addBar(bar)
        self.current_i += 1
        # print(bar)
        self.plotBar(bar, self.ax1)
        self.plotBar(habar, self.ax2)
        self.canvas.draw()

if __name__ == '__main__':
    barfilename = "20231130"
    filedirectory = "~/Data" if platform.system() == "Darwin" else "c:/Data"
    filepath = f"{filedirectory}/{barfilename}.csv"
    df = pd.read_csv(filepath, index_col=0, parse_dates=True)
    
    
    app = QApplication(sys.argv)
    main_window = MyMainWindow(df)
    main_window.show()
    sys.exit(app.exec())
