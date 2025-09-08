import os
import sys
import PySide6.QtWidgets as Qw
import PySide6.QtCore as Qc

def main():
    from .resistance_calc import ResistanceCalc
    
    Qw.QApplication.setAttribute(Qc.Qt.AA_EnableHighDpiScaling, True)
    Qw.QApplication.setAttribute(Qc.Qt.AA_UseHighDpiPixmaps, True)

    app = Qw.QApplication(sys.argv)

    window = ResistanceCalc()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()