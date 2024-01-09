import platform
import sys
import glob
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.widgets import Button

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QSizePolicy,
    QFormLayout,
    QSpacerItem,
    QWidget,
    QPushButton,
    QComboBox,
    QGroupBox,
    QLabel,
    QLineEdit,
)
from PyQt6 import QtCore, QtWidgets
from PyQt6.QtCore import QSize, Qt, pyqtSignal
from PyQt6.QtGui import QFont


class LabelValue(QWidget):
    def __init__(
        self, form:QFormLayout, text="NONE", width=100, readonly=True, fontsize=18
    ):
        super().__init__()
        self.lbl = QLabel(f"{text} :  ")
        # self.lbl.setFixedWidth(width)
        self.lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.lbl.setFont(QFont("Arial", fontsize))

        self.val = QLineEdit()
        self.val.setReadOnly(readonly)
        self.val.setFixedWidth(width)
        self.val.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.lbl.setFont(QFont("Arial", fontsize))

        form.addRow(self.lbl, self.val)
        
    def setValue(self, val):
        if float(val) < 0:
            self.val.setStyleSheet("color: red;")
        else:
            self.val.setStyleSheet("color: black;")
        self.val.setText(str(val))

class StatusWidget(QWidget):
    def __init__(self):
        super().__init__()

        form_layout = QFormLayout()
        self.day_pl = LabelValue(form_layout, text="Day P/L")
        self.position = LabelValue(form_layout, text="Position")
        self.current_pl = LabelValue(form_layout, text="Current P/L")
        self.setLayout(form_layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    sw = StatusWidget()
    
    sw.day_pl.setValue(3.45)
    sw.position.setValue(-100)
    sw.show()

    app.exec()
