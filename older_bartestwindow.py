import sys
import platform
import glob
import pandas as pd

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QSizePolicy,\
    QSpacerItem, QWidget, QPushButton, QComboBox, QGroupBox, QLabel
from PyQt6 import QtCore, QtWidgets
from PyQt6.QtCore import QSize, Qt, QObject, pyqtSignal

import matplotlib
matplotlib.use('QtAgg')
import matplotlib.dates as mdates
from matplotlib.axes import Axes
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.widgets import MultiCursor, Cursor
from matplotlib.lines import Line2D

from ha import HA
from hama import HAMA
from utils import DraggableLines, CrossHairCursor
from scorewidget import ScoreWidget
from utils import getLatestDataFile

class ChooseBarFile(QWidget):
    fileChangedEvent = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
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
        # spacer = QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        # spacer = QSpacerItem(1, 1, QSizePolicy.Policy.Minimum)
        # layout.addItem(spacer)
        self.setLayout(layout)

    def getBarFiles(self):
        files = glob.glob(f"{self.files_directory}/*.csv")
        files = [file.replace("\\", "/") for file in files]
        files = [s.split('/')[-1].split('.')[0] for s in files]  
        return files
        
    def index_changed(self, i): 
        pass

    def text_changed(self, filename:str):
        print("Selected in Choose", filename)
        self.parent.dataFileSelected(filename)

class BarPlotsFigure(QWidget):
    def __init__(self, setup_df:pd.DataFrame):
        super().__init__()
        self.df = setup_df
        self.bars = pd.DataFrame()
        self.habars = HA()
        self.hamabars = HAMA()
        
        self.fig_layout = QVBoxLayout()
        self.figure = Figure(figsize=(800,600))
        self.figure.suptitle("")
        self.figure.set_facecolor('#e6e6e6')
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.fig_layout.addWidget(self.canvas, stretch=1)
        
        
        self.fig_layout.addWidget(NavigationToolbar(self.canvas, self))
        
        self.createBarPlots()
        self.setLayout(self.fig_layout)
        
    def createBarPlots(self):
        self.current_i = 0
        self.i_last = len(self.df) - 1
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
    
        (self.ax1, self.ax2, self.ax3) = self.figure.subplots(3, 1, sharex=True, sharey=True)
        self.figure.subplots_adjust(left=0.05, right=0.95, bottom=0.05, top=0.95, hspace=0.2)
        
        self.ax1.set_title("Candles")
        self.ax1.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        self.ax1.yaxis.tick_right()
        self.ax1.set_xlim(self.x_left, self.x_right)
        self.ax1.set_ylim(self.y_low, self.y_high)
        self.ax1.grid(True, linestyle='--', color='gray', alpha=0.7)
        self.draggable_lines_1 = DraggableLines(self.ax1, self.getHorizLineCreateFlag)
        self.crosshair_1 = CrossHairCursor(self.ax1)
        
        self.ax2.set_title("HA")
        self.ax2.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        self.ax2.yaxis.tick_right()
        self.ax2.set_xlim(self.x_left, self.x_right)
        self.ax2.set_ylim(self.y_low, self.y_high)
        self.ax2.grid(True, linestyle='--', color='gray', alpha=0.7)
        # self.draggable_lines_2 = DraggableLines(self.ax2, self.getHorizLineCreateFlag)
        
        self.ax3.set_title("HAMA")
        self.ax3.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        self.ax3.yaxis.tick_right()
        self.ax3.set_xlim(self.x_left, self.x_right)
        self.ax3.set_ylim(self.y_low, self.y_high)
        self.ax3.grid(True, linestyle='--', color='gray', alpha=0.7)
    
    def nextBars(self, n:int):
        for i in range(n):
            bar = self.df.iloc[[self.current_i]]
            habar = self.habars.addBar(bar)
            hamabar = self.hamabars.addBar(bar)
            self.current_i += 1
            self.plotBar(bar, self.ax1)
            self.plotBar(habar, self.ax2)
            self.plotBar(hamabar, self.ax3)
            self.canvas.draw()
        
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
       
class BackTestWindow(QWidget):
    def __init__(self, setup_df:pd.DataFrame):
        super().__init__()
        
        self.df = setup_df
        self.bars = pd.DataFrame()
        self.habars = HA()
        self.hamabars = HAMA()
        
        # self.createBarPlots()
        self.bar_plots = BarPlotsFigure(self.df)
        
        self.buttons_layout = self.Buttons()
        self.status_widget = ScoreWidget()
        
        button_score_layout = QVBoxLayout()
        button_score_layout.addLayout(self.buttons_layout)
        button_score_layout.addWidget(self.status_widget)
        
        layout = QHBoxLayout()
    
        # layout.addLayout(self.fig_layout)
        layout.addWidget(self.bar_plots)
        
        cmd_layout = QVBoxLayout()  
        buttons_layout = self.Buttons()
        cmd_layout.addLayout(button_score_layout)
        layout.addLayout(cmd_layout)
            
        self.setLayout(layout)
        
    
    def onButtonClick(self):
        print("Button clicked.")
        
    def Buttons(self) -> QVBoxLayout:
        layout_buttons = QVBoxLayout()
        
        self.choose = ChooseBarFile()
        layout_buttons.addWidget(self.choose)
        
        self.next_button = QPushButton("Next Bar")
        self.next_button.clicked.connect(self.handleNextBar)
        layout_buttons.addWidget(self.next_button)
        
        self.buttons = {}
        for n in [5,10,20,30]:
            btn_label = f"Next {n} Bars"
            self.buttons[n] = QPushButton(btn_label)
            layout_buttons.addWidget(self.buttons[n])
            match n:
                case 5:
                    self.buttons[5].clicked.connect(lambda : self.bar_plots.nextBars(5))
                case 10:
                    self.buttons[10].clicked.connect(lambda : self.bar_plots.nextBars(10))
                case 20 :
                    self.buttons[20].clicked.connect(lambda : self.bar_plots.nextBars(20))
                case 30 :
                    self.buttons[30].clicked.connect(lambda : self.bar_plots.nextBars(30))
                case default:
                    return None
            
        self.toggle_cross_button = QPushButton("Toggle Crosshair")
        self.toggle_cross_button.clicked.connect(self.handleToggleCrosshair)
        layout_buttons.addWidget(self.toggle_cross_button)
        
        self.redraw_button = QPushButton("Redraw")
        self.redraw_button.clicked.connect(self.handleRedraw)
        layout_buttons.addWidget(self.redraw_button)
        
        self.buy_button = QPushButton("BUY")
        self.buy_button.clicked.connect(self.handleBuy)
        layout_buttons.addWidget(self.buy_button)
        
        self.sell_button = QPushButton("SELL")
        self.sell_button.clicked.connect(self.handleSell)
        layout_buttons.addWidget(self.sell_button)
        
        self.hline_button = QPushButton("Horiz Line")
        self.horiz_line_create = False
        self.hline_button.clicked.connect(self.handleCreateHLine)
        layout_buttons.addWidget(self.hline_button)
        
        spacer_item = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout_buttons.addItem(spacer_item)
        return layout_buttons
            
    def handleRedraw(self):
        print("REDRAW CLICKED")
        
    def handleBuy(self):
        print("BUY CLICKED")
        
    def handleSell(self):
        print("SELL CLICKED")
        
    def handleCreateHLine(self):
        self.horiz_line_create = not self.horiz_line_create
        if self.horiz_line_create:
            self.hline_button.setStyleSheet("background-color: red;")
        else:
            self.hline_button.setStyleSheet("")
        
    def getHorizLineCreateFlag(self):
        return self.horiz_line_create
        
    def handleToggleCrosshair(self):
        print("TOGGLE CROSSHAIR")
        self.bar_plots.crosshair_1.toggle_crosshair()
             
    def handleNextBar(self, e):
        self.bar_plots.nextBars(1)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_C:
            self.bar_plots.crosshair_1.toggle_crosshair()
            
            
if __name__ == '__main__':
    latest_data_file = getLatestDataFile()
    zf = pd.read_csv(latest_data_file, index_col=0, parse_dates=True)
    
    app = QApplication(sys.argv)
    # main_window = BarPlotsFigure(df)
    main_window = BackTestWindow(zf)
    main_window.show()
    sys.exit(app.exec())