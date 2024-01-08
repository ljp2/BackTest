import platform
import sys
import glob
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.widgets import Button

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QSizePolicy,\
    QSpacerItem, QWidget, QPushButton, QComboBox, QGroupBox, QLabel
from PyQt6 import QtCore, QtWidgets
from PyQt6.QtCore import QSize, Qt, pyqtSignal

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
        print("Selected", filename)
        

class ToggleButton(Button):
    def __init__(self, ax, label):
        super().__init__()
        self.state = False

        self.state = False
        self.update_button_text()

    def toggle(self, event):
        self.state = not self.state
        if self.state:
            self.button.label.set_text("ON")
            self.button.color = 'green'
        else:
            self.button.label.set_text("OFF")
            self.button.color = 'red'

    def update_button_text(self):
        if self.state:
            self.button.label.set_text("ON")
            self.button.color = 'green'
        else:
            self.button.label.set_text("OFF")
            self.button.color = 'red'
        self.ax.figure.canvas.draw_idle()
        
class DraggableLines:
    def __init__(self, ax, getHorizLineCreateFlag, use_label=False):
        self.ax = ax
        self.getHorizLineCreateFlag = getHorizLineCreateFlag
        self.use_label = use_label
        self.lines = []
        self.is_dragging = False
        self.current_line = None
        self.press_y = None
        self.connect()
        
        self.ax.set_picker = True

    def connect(self):
        self.ax.figure.canvas.mpl_connect('button_press_event', self.on_press)
        self.ax.figure.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.ax.figure.canvas.mpl_connect('button_release_event', self.on_release)

    def on_press(self, event):
        if event.inaxes == self.ax:
            # x, y = event.xdata, event.ydata
            # self.ax.axhline(y=y, color='r', linestyle='--')
            # self.ax.figure.canvas.draw()
            clicked_line = self.get_line_at_event(event)
            if clicked_line:
                if event.button == 3:
                    # print("SHULD REMOE", clicked_line)
                    clicked_line.remove()
                    self.lines.remove(clicked_line)
                    self.ax.figure.canvas.draw_idle()
                    # for x in self.lines:
                    #     print(x)
                    # print()
                self.is_dragging = True
                self.current_line = clicked_line
                self.press_y = event.ydata
            elif self.getHorizLineCreateFlag():
                # new_line, = self.ax.plot([0, 1], [event.ydata, event.ydata], color='r', lw=2)
                x, y = event.xdata, event.ydata
                new_line = self.ax.axhline(y=y, color='r', linestyle='--', lw=1)
                self.lines.append(new_line)
                self.current_line = new_line
                self.is_dragging = True
                self.press_y = event.ydata
                
                if self.use_label:
                    label_text = f'{y:.2f}'
                    self.ax.text(x, y, label_text, ha='right', va='bottom', bbox=dict(facecolor='white', edgecolor='white'))
                            
                self.ax.figure.canvas.draw_idle()
                # for x in self.lines:
                #     print(x)
                # print()

    def on_motion(self, event):
        if self.is_dragging and event.inaxes == self.ax:
            delta_y = event.ydata - self.press_y
            new_ydata = [y + delta_y for y in self.current_line.get_ydata()]
            self.current_line.set_ydata(new_ydata)
            self.press_y = event.ydata
            self.ax.figure.canvas.draw_idle()

    def on_release(self, event):
        self.is_dragging = False

    def get_line_at_event(self, event):
        for line in self.lines:
            if line.contains(event)[0]:
                return line
        return None
            
class ExponentialSmoothing:
    def __init__(self, alpha=NotImplemented, length=NotImplemented):
        if alpha is NotImplemented:
            self.alpha = 2.0 / (length + 1)
        else:
            self.alpha = alpha
        # print(self.alpha)
        self.smoothed_data = []
        self.new_smoothed_value = None

    def update(self, new_raw_value):
        if not self.smoothed_data:
            # If no data is present, use the first raw value as the initial smoothed value
            self.new_smoothed_value = new_raw_value
        else:
            last_smoothed_value = self.smoothed_data[-1]
            self.new_smoothed_value = self.alpha * new_raw_value + (1 - self.alpha) * last_smoothed_value

        self.smoothed_data.append(self.new_smoothed_value)
        return self.new_smoothed_value

    def get_smoothed_data(self):
        return self.smoothed_data
    
class CrossHairCursor():
    def __init__(self, ax) -> None:
        self.ax = ax
        self.hline = self.ax.axhline(0, color='gray', linestyle='--', linewidth=1, visible=False)
        self.vline = self.ax.axvline(0, color='gray', linestyle='--', linewidth=1, visible=False)
        self.crosshair_visible = True
        self.ax.figure.canvas.mpl_connect('motion_notify_event', self.update_crosshair)
 
    def update_crosshair(self, event):
        if event.inaxes == self.ax:
            x, y = event.xdata, event.ydata
            self.hline.set_ydata([y])
            self.vline.set_xdata([x])
            self.hline.set_visible(self.crosshair_visible)
            self.vline.set_visible(self.crosshair_visible)
            self.ax.figure.canvas.draw_idle()
    
    def toggle_crosshair(self):
        self.crosshair_visible = not self.crosshair_visible
        self.hline.set_visible(self.crosshair_visible)
        self.vline.set_visible(self.crosshair_visible)
        self.ax.figure.canvas.draw_idle()