import sys
import os
import platform
import glob
import pandas as pd
from multiprocessing import Process
from datetime import datetime

from PyQt6.QtCore import QSize, Qt, pyqtSignal, QDate
from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QVBoxLayout, \
    QLabel, QPushButton, QComboBox, QGroupBox, QSpacerItem, QSizePolicy, QDateEdit
from PyQt6.QtGui import QFont

from backtestwindow import BackTestWindow
import utils

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
        self.title_label = QLabel("Chose Data File for Backtesting")
        
        self.comboBox = QComboBox()
        self.files = ["None Selected"] + self.getBarFiles()
        self.comboBox.addItems(self.files)
        self.comboBox.currentTextChanged.connect( self.text_changed )
        
        group_box = QGroupBox()
        group_layout = QVBoxLayout(group_box)
        group_layout.addWidget(self.title_label, alignment=Qt.AlignmentFlag.AlignTop)
        group_layout.addWidget(self.comboBox, alignment=Qt.AlignmentFlag.AlignTop)
        
        layout.addWidget(group_box)
        layout.setAlignment(group_box, Qt.AlignmentFlag.AlignCenter)
        
        self.chosen_label = QLabel()
        self.chosen_label.setFont(QFont("Arial", 12))
        layout.addWidget(self.chosen_label)
        layout.setAlignment(self.title_label, Qt.AlignmentFlag.AlignCenter)
        self.setLayout(layout)
        
    #     date_edit = QDateEdit(self)
    #     date_edit.setCalendarPopup(True)  # Enable calendar popup
    #     date_edit.setDate(QDate.currentDate())  # Set the initial date

    #     # Connect a slot to handle the date change
    #     date_edit.dateChanged.connect(self.handle_date_change)

    #     layout.addWidget(date_edit)
    
    
    # def set_special_dates(self, calendar_widget):
    #     # Set styles for specific dates based on a logical condition
    #     special_dates = [QDate(2024, 1, 15), QDate(2024, 1, 20)]

    #     for date in special_dates:
    #         special_style = calendar_widget.dateTextFormat(date)
    #         special_style.setForeground(QColor(Qt.GlobalColor.red))  # Set color to red
    #         special_style.setFontWeight(75)  # Bold
    #         calendar_widget.setDateTextFormat(date, special_style)

    # def handle_date_change(self, new_date):
    #     print('Selected date:', new_date.toString("yyyy-MM-dd"))


    def getBarFiles(self):
        files = glob.glob(f"{self.files_directory}/*.csv")
        files = [file.replace("\\", "/") for file in files]
        files = [s.split('/')[-1].split('.')[0] for s in files]  
        return files
        
    def text_changed(self, base_file_name:str):
        date_object = datetime.strptime(base_file_name, "%Y%m%d")
        yearint = int(base_file_name[:4])
        month = int(base_file_name[4:6])
        day = int(base_file_name[6:8])
        year = date_object.year
        month_name = date_object.strftime("%B")  # Full month name
        day_name = date_object.strftime("%A")    # Full day name
        text = f"{base_file_name} : {day_name}, {month_name} {day}, {year}"
        print("text =", text)
        self.chosen_label.setText(text)
        self.parent.newFileChosen(base_file_name)


def BacktestProcess(base_file_name:str):
    date_object = datetime.strptime(base_file_name, "%Y%m%d")
    year = date_object.year
    month_name = date_object.strftime("%B")
    day_name = date_object.strftime("%A")
    day_number =  date_object.strftime("%d")
    window_title = f"Backtesting {day_name}, {month_name} {day_number}, {year}"
    
    app = QApplication(sys.argv)
    main_window = BackTestWindow(base_file_name)
    main_window.setWindowTitle(window_title)
    main_window.show()
    sys.exit(app.exec())

def CreateBacktest(base_file_name:str):
    bt = Process(target=BacktestProcess, args=(base_file_name,))
    bt.start()
    
    
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BackTesting")
        self.resize(300, 200)
        w = QWidget()
        layout = QVBoxLayout()
        self.choose = ChooseBarFile(self)
        layout.addWidget(self.choose)
        w = QWidget()
        w.setLayout(layout)
        self.setCentralWidget(w)
        
    def newFileChosen(self, base_file_name:str):
        print(base_file_name)
        CreateBacktest(base_file_name)

if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
        
            