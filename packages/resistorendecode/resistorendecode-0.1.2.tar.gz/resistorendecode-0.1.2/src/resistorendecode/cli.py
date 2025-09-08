from pathlib import Path
import os
import sys
import PySide6.QtWidgets as Qw
import PySide6.QtCore as Qc

print('Running' if __name__ == '__main__' else 'Importing', Path(__file__).resolve())

from .resistance_calc import ResistanceCalc

def main():
    
    Qw.QApplication.setAttribute(Qc.Qt.AA_EnableHighDpiScaling, True)
    Qw.QApplication.setAttribute(Qc.Qt.AA_UseHighDpiPixmaps, True)

    app = Qw.QApplication(sys.argv)

    window = ResistanceCalc()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()