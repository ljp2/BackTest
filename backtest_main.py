import sys
import os
import platform
import glob
import pandas as pd

from PyQt6.QtCore import QSize, Qt, pyqtSignal
from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QVBoxLayout, \
    QLabel, QPushButton, QComboBox, QGroupBox, QSpacerItem, QSizePolicy

from backtestwindow import BackTestWindow
from utils import getLatestDataFile, getLowHighLimits, getRoundedLowHighLimits


    

class MainWindow(QMainWindow):
    def __init__(self, df):
        super().__init__()
        
        layout = QVBoxLayout()
        
        bt = BackTestWindow(df)
        layout.addWidget(bt)
        
        scoreboard = QLabel("THE SCOREBOARD GOES HERe")
        layout.addWidget(scoreboard)
        
        w = QWidget()
        w.setLayout(layout)
        
        self.setCentralWidget(w)
        
        

if __name__ == '__main__':
    latest_data_file = getLatestDataFile()
    # filedirectory = "~/Data" if platform.system() == "Darwin" else "c:/Data"
    # filepath = f"{filedirectory}/{barfilename}.csv"
    df = pd.read_csv(latest_data_file, index_col=0, parse_dates=True)
    
    app = QApplication(sys.argv)
    main_window = MainWindow(df)
    main_window.show()
    sys.exit(app.exec())