import sys
from PyQtcode import ToDoListApp
from PyQt5.QtWidgets import QApplication

def main():
    app = QApplication(sys.argv)
    window = ToDoListApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
