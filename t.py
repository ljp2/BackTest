from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt

class MyMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        # Create a child widget with a QPushButton
        child_widget = QWidget()
        button = QPushButton("Click me!")
        button.clicked.connect(self.onButtonClick)
        layout.addWidget(button)  # Add the button to the layout
        child_widget.setLayout(layout)

        # Set the child widget as the central widget
        self.setCentralWidget(child_widget)

    def keyPressEvent(self, event):
        print("KRY PRESSED")
        modifiers = event.modifiers()

        # Example: Handling the key event in the main window
        if modifiers == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_Q:
            print("Ctrl + Q pressed. Quitting application.")
            self.close()

    def onButtonClick(self):
        print("Button clicked.")

if __name__ == '__main__':
    app = QApplication([])
    main_window = MyMainWindow()
    main_window.show()
    app.exec()
