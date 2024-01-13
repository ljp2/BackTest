import sys
import os
import platform
import glob
import pandas as pd
from multiprocessing import Process
from datetime import datetime

from PyQt6.QtCore import QSize, Qt, pyqtSignal, QDate
from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QVBoxLayout, \
    QLabel, QPushButton, QComboBox, QGroupBox, QSpacerItem, QSizePolicy, QDateEdit, \
    QDialog, QCalendarWidget, QDialogButtonBox
from PyQt6.QtGui import QFont

from backtestwindow import BackTestWindow
import utils

class MyDialog(QDialog):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        layout = QVBoxLayout()
        
        label = QLabel("")
        layout.addWidget(label)
        
        self.calendar = QCalendarWidget(self)
        layout.addWidget(self.calendar)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)
        
    def accept(self) -> None:
        selected_date = self.calendar.selectedDate()
        print(selected_date, type(selected_date))
        self.parent.selectedDate(selected_date)
        return super().accept()
    
    def reject(self) -> None:
        self.parent.noDateSelected()
        return super().reject()
    

def BacktestProcess(df:pd.DataFrame):

    # date_object = datetime.strptime(base_file_name, "%Y%m%d")
    # year = date_object.year
    # month_name = date_object.strftime("%B")
    # day_name = date_object.strftime("%A")
    # day_number =  date_object.strftime("%d")
    # window_title = f"Backtesting {day_name}, {month_name} {day_number}, {year}"
    
    app = QApplication(sys.argv)
    main_window = BackTestWindow(df)
    # main_window.setWindowTitle(window_title)
    main_window.show()
    sys.exit(app.exec())

def CreateBacktest(df:pd.DataFrame):
    bt = Process(target=BacktestProcess, args=(df,))
    bt.start()
    
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt6 Example")

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        self.backtestFileLabel = QLabel("Current Backtest File :  None")
        self.backtestFileLabel.setFont(QFont("Arial", 18))
        self.button = QPushButton("Select Date for Backtest Filel", self)
        self.button.clicked.connect(self.show_dialog)
        layout.addWidget(self.backtestFileLabel)
        layout.addWidget(self.button)
        central_widget.setLayout(layout)

    def show_dialog(self):
        dialog = MyDialog(self)
        dialog.exec()
        
    def selectedDate(self, selected_date:QDate):
        mdy = selected_date.toString("MMM dd, yyyy")
        self.backtestFileLabel.setText(f"Current Backtest File :  {mdy}")
        df = utils.getDF(selected_date)
        if df is None:
            print("NO DATA FOR DATE", selected_date)
        else:
            CreateBacktest(df)

    def noDateSelected(self):
        print("Cancelled no date selected")
    

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()