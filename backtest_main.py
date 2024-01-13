import sys
import os
import platform
import glob
import pandas as pd
from multiprocessing import Process
from datetime import datetime

from PyQt6.QtCore import QSize, Qt, pyqtSignal, QDate
from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QVBoxLayout, \
    QLabel, QPushButton, QDialog, QCalendarWidget, QDialogButtonBox, QMessageBox
from PyQt6.QtGui import QFont

from backtestwindow import BackTestWindow
import utils

class ChooseBacktestFile(QDialog):
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
        valid_date = self.parent.selectedDate(selected_date)
        if valid_date:
            return super().accept()
        else:
            mdy = selected_date.toString("MMM dd, yyyy")
            msg = f"No Data Available for {mdy}"
            QMessageBox.information(None, "", msg)
    
    def reject(self) -> None:
        self.parent.noDateSelected()
        return super().reject()
    

def BacktestProcess(df:pd.DataFrame, selected_date:QDate):
    window_title = selected_date.toString("MMM dd, yyyy")
    app = QApplication(sys.argv)
    main_window = BackTestWindow(df)
    main_window.setWindowTitle(window_title)
    main_window.show()
    sys.exit(app.exec())

def CreateBacktest(df:pd.DataFrame, selected_date:QDate):
    bt = Process(target=BacktestProcess, args=(df,selected_date))
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
        dialog = ChooseBacktestFile(self)
        dialog.exec()
        
    def selectedDate(self, selected_date:QDate) -> bool:
        mdy = selected_date.toString("MMM dd, yyyy")
        self.backtestFileLabel.setText(f"Current Backtest File :  {mdy}")
        df = utils.getDF(selected_date)
        if df is None:
            return False
        else:
            CreateBacktest(df, selected_date)
            return True
            

    def noDateSelected(self):
        pass
        # print("Cancelled no date selected")
    

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()