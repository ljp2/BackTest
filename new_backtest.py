import sys
import glob
import platform
import pandas as pd

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QSizePolicy,\
    QSpacerItem, QWidget, QPushButton, QComboBox, QGroupBox, QLabel
from PyQt6 import QtCore, QtWidgets
from PyQt6.QtCore import QSize, Qt, pyqtSignal

import matplotlib
matplotlib.use('QtAgg')
import matplotlib.dates as mdates
from matplotlib.axes import Axes
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from ha import HA
from hama import HAMA

class ChooseBarFile(QWidget):
    fileChangedEvent = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.bars = None
        
        if platform.system() == "Darwin":
            self.files_directory = "/Users/ljp2/Data"
        else:
            self.files_directory = "C:/Data/"
        
        layout = QVBoxLayout()
        
        self.title_label = QLabel('Backtest Day')
        group_box = QGroupBox()
        group_layout = QVBoxLayout(group_box)
        group_layout.addWidget(self.title_label, alignment=Qt.AlignmentFlag.AlignTop)
        
        self.comboBox = QComboBox()
        self.files = ["None Selected"] + self.getBarFiles()
        self.comboBox.addItems(self.files)
        self.comboBox.currentIndexChanged.connect( self.index_changed )
        self.comboBox.currentTextChanged.connect( self.text_changed )
        
        group_layout.addWidget(self.comboBox, alignment=Qt.AlignmentFlag.AlignTop)
        
        layout.addWidget(group_box)
        spacer = QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addItem(spacer)
        self.setLayout(layout)

    def getBarFiles(self):
        files = glob.glob(f"{self.files_directory}/*.csv")
        files = [file.replace("\\", "/") for file in files]
        files = [s.split('/')[-1].split('.')[0] for s in files]  
        return files
        
    def index_changed(self, i): # i is an int
        print(i)

    def text_changed(self, filename:str):
        self.fileChangedEvent.emit()
        # filepath = f"{self.files_directory}/{filename}.csv"
        # self.bars = pd.read_csv(filepath, index_col=0, parse_dates=True)
        # print(self.bars.head())
        # print(self.bars.tail())
        
        # self.plot_process = plot.PlotProcess(self.bars)


class MyMainWindow(QMainWindow):
    def __init__(self, df):
        super().__init__()
        self.df = df
        
        self.bars = pd.DataFrame()
        self.habars = HA()
        self.hamabars = HAMA()
        
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
        
        self.layout = QVBoxLayout()

        self.figure = Figure(figsize=(800,600))
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
        
        layout_buttons = self.Buttons()
        
        layout_h = QHBoxLayout()
        layout_h.addLayout(self.layout)
        layout_h.addLayout(layout_buttons)
            
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.central_widget.setLayout(layout_h)
        
        self.setMinimumSize(800, 600)
        
    def Buttons(self) -> QVBoxLayout:
        layout_buttons = QVBoxLayout()
        
        self.choose = ChooseBarFile()
        layout_buttons.addWidget(self.choose)
        
        self.next_button = QPushButton("Next Bar")
        self.next_button.clicked.connect(self.handleNextBar)
        layout_buttons.addWidget(self.next_button)
        
        self.redraw_button = QPushButton("Redraw")
        self.redraw_button.clicked.connect(self.handleShowHama)
        layout_buttons.addWidget(self.redraw_button)
        
        self.buy_button = QPushButton("BUY")
        self.buy_button.clicked.connect(self.handleShowHama)
        layout_buttons.addWidget(self.buy_button)
        
        self.sell_button = QPushButton("SELL")
        self.sell_button.clicked.connect(self.handleShowHama)
        layout_buttons.addWidget(self.sell_button)
        
        spacer_item = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout_buttons.addItem(spacer_item)
        return layout_buttons

    def handleRedraw(self):
        print("REDRAW CLICKED")
        
    def handleShowHama(self):
        print("SHOW HAMA CLICKED")
        
    def handleBuy(self):
        print("BUY CLICKED")
        
    def handleSell(self):
        print("SELL CLICKED")
        
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
        hamabar = self.hamabars.addBar(bar)
        self.current_i += 1
        # print(bar)
        self.plotBar(bar, self.ax1)
        self.plotBar(habar, self.ax2)
        self.plotBar(hamabar, self.ax1)
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
