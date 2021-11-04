## Updated version of app.py ## 

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from vectorUi import Ui_MainWindow
import sys
# from PyQt5 import QtWidgets
import pdb
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import numpy as np
import matplotlib.animation as animation
from PyQt5 import QtCore, QtGui, QtWidgets
from canvas import Canvas

# Connecting UI and Canvas. 
def connect(ui, canvas):
    # XMax slider, xMin slider. 
    ui.xMaxSlider.valueChanged.connect(canvas.toggleXMax)
    ui.xMinSlider.valueChanged.connect(canvas.toggleXMin)
    ui.yMinSlider.valueChanged.connect(canvas.toggleYMin)
    ui.yMaxSlider.valueChanged.connect(canvas.toggleYMax)
    ui.densitySlider.valueChanged.connect(canvas.toggleDensity)
    ui.stepSize.valueChanged.connect(canvas.toggleStepSize)
    ui.addPoints.toggled.connect(canvas.OperationalMode)
    ui.selectMode.toggled.connect(canvas.OperationalMode)

    ui.submitVectorField.clicked.connect(canvas.computeFormulaXandY)
    ui.startPush.clicked.connect(canvas.startAnimation)
    ui.stopPush.clicked.connect(canvas.stopAnimation)
    ui.clearAll.clicked.connect(canvas.clearAll)

# Main function to be executed.
if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)
    ui = Ui_MainWindow()
    MainWindow = QtWidgets.QMainWindow()
    ui.setupUi(MainWindow)
    
    canvas = Canvas(ui, ui.centralwidget)
    connect(ui, canvas)
    MainWindow.show()
    sys.exit(app.exec_())