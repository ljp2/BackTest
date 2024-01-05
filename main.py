import sys
import glob
from PyQt6.QtCore import QSize, Qt

from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, \
    QPushButton, QComboBox

def getBarFiles():
    files = [s.split('/')[-1].split('.')[0] for s in  glob.glob("/Users/ljp2/Data/*.csv")]
    return files

class BarFiles(QComboBox):
    def __init__(self) -> None:
        super().__init__()
        files = [""] + getBarFiles()
        self.addItems(files)
        
        self.currentIndexChanged.connect( self.index_changed )
        self.currentTextChanged.connect( self.text_changed )
        
    def index_changed(self, i): # i is an int
        print(i)

    def text_changed(self, s): # s is a str
        print(s)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.button_is_checked = False
        
        self.setMinimumSize(QSize(400,300))
        self.setWindowTitle('BackTester')
        
        self.files = BarFiles()
        
        self.setCentralWidget(self.files)
        
        
    def the_button_was_clicked(self):
        self.button.setText("You already clicked me.")
        self.button.setEnabled(False)
        self.setWindowTitle("A new window title")
        

app = QApplication([])

window = MainWindow()
window.show()

app.exec()
