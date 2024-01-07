import sys
import os
import platform
import glob
import pandas as pd

from PyQt6.QtCore import QSize, Qt, pyqtSignal
from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QVBoxLayout, \
    QLabel, QPushButton, QComboBox, QGroupBox, QSpacerItem, QSizePolicy

import plot

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


class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.setMinimumSize(QSize(200,100))
        self.setWindowTitle('BackTester')
        
        layout = QVBoxLayout()
        
        self.choose:ChooseBarFile = ChooseBarFile()
        # Connect the custom signal from the child to a slot in the parent
        self.choose.fileChangedEvent.connect(self.handleFileChanged)

        self.button = QPushButton("Show Current File Name")
        self.button.clicked.connect(self.showFileName)
        
        layout.addWidget(self.choose)
        layout.addWidget(self.button)
        
        widget = QWidget()
        widget.setLayout(layout)
            
        self.setCentralWidget(widget)
        
    def showFileName(self):
        print("Current File Name =", self.choose.comboBox.currentText())

    def handleFileChanged(self):
        x = self.choose.comboBox.currentText()
        print('Current = ', x)
        
app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()