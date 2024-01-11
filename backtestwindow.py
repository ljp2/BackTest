import sys
import platform
import glob
import pandas as pd
from multiprocessing import Process

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QSizePolicy,\
    QSpacerItem, QWidget, QPushButton, QComboBox, QGroupBox, QLabel, QMessageBox
from PyQt6 import QtCore, QtWidgets
from PyQt6.QtCore import QSize, Qt, QObject, pyqtSignal
from PyQt6.QtGui import QFont

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
from statuswidget import StatusWidget
from utils import getLatestDataFile
import utils

class BarPlotsFigure(QWidget):
    def __init__(self, parent, setup_df:pd.DataFrame):
        super().__init__()
        self.parent = parent
        self.df = setup_df
        self.position_line:Line2D = None
        
        self.fig_layout = QVBoxLayout()
        self.figure = Figure(figsize=(1000,750))
        self.figure.suptitle("")
        self.figure.set_facecolor('#e6e6e6')
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.fig_layout.addWidget(self.canvas, stretch=1)
        
        self.fig_layout.addWidget(NavigationToolbar(self.canvas, self))
        
        self.createBarPlots()
        self.setLayout(self.fig_layout)
        
    def createBarPlots(self):
        maxy = self.df['High'].max()
        miny = self.df['Low'].min()
        height = maxy - miny
        delta = 0.05 * height
        self.x_left = self.df.index[0]
        self.x_right = self.df.index[-1]
        self.y_high = maxy + delta
        self.y_low = miny - delta
        
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
        self.draggable_lines_1 = DraggableLines(self.ax1, self.parent.getHorizLineCreateFlag)
        self.crosshair_1 = CrossHairCursor(self.ax1)
        
        self.ax2.set_title("HA")
        self.ax2.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        self.ax2.yaxis.tick_right()
        self.ax2.set_xlim(self.x_left, self.x_right)
        self.ax2.set_ylim(self.y_low, self.y_high)
        self.ax2.grid(True, linestyle='--', color='gray', alpha=0.7)
        
        self.ax3.set_title("HAMA")
        self.ax3.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        self.ax3.yaxis.tick_right()
        self.ax3.set_xlim(self.x_left, self.x_right)
        self.ax3.set_ylim(self.y_low, self.y_high)
        self.ax3.grid(True, linestyle='--', color='gray', alpha=0.7)
    
        x = [self.x_right, self.x_right]
        x = [self.df.index[100], self.df.index[100]]
        y = [self.y_low, self.y_high]
        # self.vline1 = Line2D(x,y, color='red', linestyle='--', label='Cursor')
        # self.ax1.add_line(self.vline1)
        self.vline2 = Line2D(x,y, color='red', linestyle='--', linewidth=0.5)
        self.ax2.add_line(self.vline2)
        self.vline3 = Line2D(x,y, color='red', linestyle='--', linewidth=0.5)
        self.ax3.add_line(self.vline3)
    
        self.canvas.mpl_connect('motion_notify_event', self.update_line)

    def zoomAll(self):
        self.ax1.set_xlim(self.x_left, self.x_right)
        self.ax1.set_ylim(self.y_low, self.y_high)
        self.canvas.draw()
            
    def update_line(self, event):
        if event.inaxes == self.ax1:
            x_cursor = event.xdata
            # self.vline1.set_xdata([x_cursor, x_cursor])
            self.vline2.set_xdata([x_cursor, x_cursor])
            self.vline3.set_xdata([x_cursor, x_cursor])
            # self.bar_plots.canvas.draw_idle() 
            

    def updatePositionLine(self, position, value):
        if self.position_line is not None:
            self.position_line.remove()
            self.position_line = None
        if position > 0:
            self.position_line = self.ax1.axhline(y=value, color='green', linestyle='-', linewidth=1.0)
        elif position < 0:
            self.position_line = self.ax1.axhline(y=value, color='red', linestyle='-', linewidth=1.0)
        self.canvas.draw_idle()
            
            
            
            
        
        
    def plotBar(self, bardf: pd.DataFrame):
        self.plotBarAxes(bardf, self.ax1)
    
    def plotHA(self, bardf: pd.DataFrame):
        self.plotBarAxes(bardf, self.ax2)
    
    def plotHAMA(self, bardf: pd.DataFrame):
        self.plotBarAxes(bardf, self.ax3)
        
    def plotBarAxes(self, bardf: pd.DataFrame, ax:Axes):
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
       
class Buttons(QWidget):
    def  __init__(self, parent):
        super().__init__()
        self.parent = parent
        layout_buttons = QVBoxLayout()
    
        self.buttons = {}
        for n in [1, 5,10,20,30]:
            if n == 1:
                btn_label = "Get Next Bar"
            else:
                btn_label = f"Get Next {n} Bars"
            self.buttons[n] = QPushButton(btn_label)
            layout_buttons.addWidget(self.buttons[n])
            self.buttons[n].clicked.connect(self.onNextBars)
            
        self.toggle_cross_button = QPushButton("Toggle Crosshair")
        self.toggle_cross_button.clicked.connect(self.parent.handleToggleCrosshair)
        layout_buttons.addWidget(self.toggle_cross_button)
        
        layout_buttons.addWidget(QLabel())  #SPACE
        # self.redraw_button = QPushButton("Redraw")
        # self.redraw_button.clicked.connect(self.parent.handleRedraw)
        # layout_buttons.addWidget(self.redraw_button)
        
        layout_buttons.addWidget(QLabel())
        self.show_latest_hour_button = QPushButton('Show Latest 30 Min')
        self.show_latest_hour_button.clicked.connect(self.parent.handleZoomLatest30)
        layout_buttons.addWidget(self.show_latest_hour_button)
        
        self.show_latest_hour_button = QPushButton('Show Latest 60 Min')
        self.show_latest_hour_button.clicked.connect(self.parent.handleZoomLatest60)
        layout_buttons.addWidget(self.show_latest_hour_button)
        
        self.zoom_all_button = QPushButton('Show All Day')
        self.zoom_all_button.clicked.connect(self.parent.handleZoomAll)
        layout_buttons.addWidget(self.zoom_all_button)
        
        layout_buttons.addWidget(QLabel())  #SPACE
        
        self.buy_button = QPushButton("BUY")
        self.buy_button.clicked.connect(self.parent.handleBuy)
        layout_buttons.addWidget(self.buy_button)
        
        self.sell_button = QPushButton("SELL")
        self.sell_button.clicked.connect(self.parent.handleSell)
        layout_buttons.addWidget(self.sell_button)
        
        self.hline_button = QPushButton("Horiz Line")
        self.horiz_line_create = False
        self.hline_button.clicked.connect(self.parent.handleCreateHLine)
        layout_buttons.addWidget(self.hline_button)
        
        spacer_item = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout_buttons.addItem(spacer_item)
        
        self.setLayout(layout_buttons)

    def onNextBars(self):
        button_name = self.sender().text()
        s = button_name.split(" ")[2]
        n = 1 if s == "Bar" else int(s)
        self.parent.nextBars(n)
        
class BackTestWindow(QWidget):
    def __init__(self, base_file_name:str):
        super().__init__()
        self.value_per_point = 5
        self.current_price:float = None
        self.position:int = 0
        self.current_pl = 0.0
        self.day_pl = 0.0
        
        self.net_value_held_shares = 0.0
        
        self.df = utils.readBaseFile(basefilename=base_file_name)
        self.current_i = -1
        
        self.bars = pd.DataFrame()
        self.habars = HA()
        self.hamabars = HAMA()
        
        self.horiz_line_create = False
        self.bar_plots = BarPlotsFigure(self, self.df)
        
        self.buttons = Buttons(self)
        self.status = StatusWidget()
        self.status.updateDayPL(self.day_pl)
        self.status.updatePosition(self.position)
        self.status.updateCurrentPL(self.current_pl)
        self.cmd_layout = QVBoxLayout()
        
        bar = self.df.iloc[0]
        self.current_price = bar['Open']
        self.current_price_label = QLabel()
        self.current_price_label.setFont(QFont("Arial", 18))
        text = f"{bar.name.strftime('%H:%M')} Open  {bar['Open']}"
        if text[0] == '0' : text = text[1:]
        self.current_price_label.setText(text)
        
          
        self.cmd_layout.addWidget(self.current_price_label)
        self.cmd_layout.addWidget(self.buttons)
        self.cmd_layout.addWidget(self.status)
        
 
        self.layout = QHBoxLayout()
        self.layout.addWidget(self.bar_plots)
        self.layout.addLayout(self.cmd_layout)
        self.setLayout(self.layout)
        
    def handleRedraw(self):
        print("REDRAW CLICKED")
        
    def avgPurchasedPricePerShare(self):
        if self.position == 0:
            avg_price_per_share = None
        elif self.position < 0:
            avg_price_per_share = self.net_value_held_shares / (-self.position)
        else:
            avg_price_per_share = self.net_value_held_shares / self.position
        return avg_price_per_share
    
    def handleBuy(self):
        current_value_per_share = self.avgPurchasedPricePerShare()
        if self.position == 0:
            self.net_value_held_shares = self.current_price
            self.position = 1
        elif self.position < 0:
            transaction_pl = current_value_per_share - self.current_price
            self.day_pl += transaction_pl * self.value_per_point
            
            self.net_value_held_shares -= self.current_price
            self.position += 1
            self.status.updateDayPL(round(self.day_pl,2))
            
        else: # position > 0
            self.net_value_held_shares += self.current_price
            self.position += 1  
                
        new_current_value_per_share = self.avgPurchasedPricePerShare()
        self.status.updatePosition(self.position)
        self.bar_plots.updatePositionLine(self.position, new_current_value_per_share)
        self.updateCurrentPL()
           
    def handleSell(self):
        current_value_per_share = self.avgPurchasedPricePerShare()
        if self.position == 0:
            self.net_value_held_shares = self.current_price
            self.position = -1
        elif self.position < 0:
            self.net_value_held_shares += self.current_price
            self.position -= 1
        else: # position > 0
            self.net_value_held_shares -= self.current_price
            transaction_pl = self.current_price - current_value_per_share
            self.day_pl += transaction_pl * self.value_per_point
            self.position -= 1
            self.status.updateDayPL(round(self.day_pl,2))
            
        new_current_value_per_share = self.avgPurchasedPricePerShare()
        self.status.updatePosition(self.position)
        self.bar_plots.updatePositionLine(self.position, new_current_value_per_share)
        self.updateCurrentPL()
        
    def handleCreateHLine(self):
        self.horiz_line_create = not self.horiz_line_create
        if self.horiz_line_create:
            self.buttons.hline_button.setStyleSheet("background-color: lightblue;")
        else:
            self.buttons.hline_button.setStyleSheet("")
        
    def getHorizLineCreateFlag(self):
        return self.horiz_line_create
        
    def handleToggleCrosshair(self):
        self.bar_plots.crosshair_1.toggle_crosshair()
    
    def zoomLatestN(self, n):
        x2_i = self.current_i
        x1_i = x2_i - n
        first = max(0, x1_i)
        last = max(x2_i, first + n)
        x1 = self.df.index[first]
        x2 = self.df.index[last]
        self.bar_plots.ax1.set_xlim(x1, x2)
        self.bar_plots.canvas.draw()
        
    def handleZoomLatest30(self):
        self.zoomLatestN(30 + 10)
        
    def handleZoomLatest60(self):
        self.zoomLatestN(60 + 20)
        
    def handleZoomAll(self):
        self.bar_plots.zoomAll()
             
    def nextBars(self, n:int):
        if self.current_i >= len(self.df) - 1:
            self.show_no_more_bars_alert()
            return
        for i in range(n):
            self.current_i += 1
            if self.current_i >= len(self.df):
                self.show_no_more_bars_alert()
                break
            bar = self.df.iloc[[self.current_i]]
            habar = self.habars.addBar(bar)
            hamabar = self.hamabars.addBar(bar)
            self.bar_plots.plotBar(bar)
            self.bar_plots.plotHA(habar)
            self.bar_plots.plotHAMA(hamabar)
            
        current_date_time = bar.index[-1]
        current_close_price = bar.iloc[-1]['Close']
        text = f"{current_date_time.strftime('%I:%M')} Close  {current_close_price}"
        if text[0] == '0' : text = text[1:]
        self.current_price_label.setText(text)
        self.current_price = current_close_price
        self.bar_plots.canvas.draw()
        self.updateCurrentPL()
        return bar
    
    def show_no_more_bars_alert(self):
        # Create a QMessageBox
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Alert")
        msg_box.setText("NO MORE BARS")
        # Set the icon (optional)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setDefaultButton(QMessageBox.StandardButton.Ok)
        result = msg_box.exec()

    
                 
    
    def updateCurrentPL(self):
        if self.position == 0:
            current_pl = 0.0
        elif self.position < 0:
            current_value_per_share = self.net_value_held_shares / (-self.position)
            current_pl = current_value_per_share - self.current_price
        else:
            current_value_per_share = self.net_value_held_shares / self.position
            current_pl = (self.current_price -current_value_per_share) * self.value_per_point
        self.status.updateCurrentPL(round(current_pl,2))
        
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_C:
            self.bar_plots.crosshair_1.toggle_crosshair()  
    
        
if __name__ == '__main__':
    from backtest_main import BacktestProcess
    BacktestProcess('20231130')
        