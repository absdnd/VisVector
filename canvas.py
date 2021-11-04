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


class MovingObject(object):
    def __init__(self, initial_state, color = [0, 0, 1]):
        self.set_state(initial_state)
        self.set_color(color)
        self.set_solver(None)

    def get_dim(self):
        return 2

    def get_state(self):
        return self.state

    def set_state(self, state):
        self.state = np.array(state)

    def set_color(self, c):
        self.color = c

    def set_velocity(self, velocity):
        self.velocity = velocity

    def set_solver(self, solver):
        self.solver = solver


class Canvas(FigureCanvas):
    def __init__(self, ui , parent, width = 7.3, height = 6, dpi = 100):
        self.fig = Figure(figsize=(width,height), dpi=dpi)
        super(Canvas, self).__init__(self.fig)
        self.setParent(parent)
        self.ui = ui
        self.ax = self.fig.add_subplot(111)

        self.density = 20
        # Setting Axes limits. 
        self.xmin, self.xmax, self.ymin, self.ymax = (-10, 10, -10, 10)

        # Creating a mesh-grid. 
        X = np.linspace(self.xmin, self.xmax, self.density)
        Y = np.linspace(self.ymin, self.ymax, self.density)
        self.X, self.Y = np.meshgrid(X, Y)

        # Per point U and V.
        self.perPointU = "np.cos(X)*Y"
        self.perPointV = "np.sin(Y)*Y"

        self.xText = "np.cos(self.X)*(self.Y)"
        self.yText = "np.cos(self.Y)*(self.Y)"

        self.RK4state = False
        self.ExplicitEulerState = False
        self.midPointState = False

        # values of u and v being set here. 
        self.u = np.cos(self.X)*self.Y
        self.v = np.sin(self.Y)*self.Y

        # Axis xlimit and ylimit being set here. 
        self.ax.set_xlim(self.xmin, self.xmax)
        self.ax.set_ylim(self.ymin, self.ymax)

        self.quiver = self.ax.quiver(self.X, self.Y, self.u, self.v)
        # self.setSlider(-10, 0, 10)

        self._idx = None

        # Scattering x and y data. 
        self.pts = self.ax.scatter([], [], color = 'blue')
        self.ax.grid()

        # Connecting button press event. 
        self.cid1 = self.mpl_connect("button_press_event", self.click)
        self.cid3 = self.mpl_connect("motion_notify_event", self.mouse_move)
        self.cid4 = self.mpl_connect("button_release_event", self.mouse_release)

        self.solverColors = {'RK4': [1, 0.6, 0], 'MidPoint': [0, 1, 1], 'ExplicitEuler': [1, 0, 1]}
        self.objs = []

        # Absolute XMax, YMax, XMin and YMin. 
        self.absXMax, self.absYMax, self.absXMin, self.absYMin = 10, 10, -10, -10

        self.isAnimating = False
        self.addMode = False
        self.dt = 0.01

        # VectorFieldAnimation.
        self.resetObjs = []
        # self.vectorFieldAnimation = None
        self.vectorFieldAnimation = animation.FuncAnimation(self.fig, self.animateStep, frames = 2000, interval = 20)
        self.vectorFieldAnimation.event_source.stop()
        self.animateMode = False
        self.setSlider(-10, 0, 10)
        # self.animation.event_source.stop()

        # Canvas focus policy. 
        # self.fig.canvas.setFocusPolicy( QtCore.Qt.ClickFocus )
        # self.fig.canvas.setFocus()

    # Setting slider values. 
    def setSlider(self, minVal, interVal, maxVal):

        self.ui.yMinSlider.setMinimum(minVal)
        self.ui.yMinSlider.setMaximum(interVal-0.1)
        self.ui.yMinSlider.setValue(self.ymin)

        self.ui.yMaxSlider.setMaximum(maxVal)
        self.ui.yMaxSlider.setMinimum(interVal+0.1)
        self.ui.yMaxSlider.setValue(self.ymax)

        self.ui.xMaxSlider.setMaximum(maxVal)
        self.ui.xMaxSlider.setMinimum(interVal+0.1)
        self.ui.xMaxSlider.setValue(self.xmax)

        self.ui.xMinSlider.setMinimum(minVal)
        self.ui.xMinSlider.setMaximum(interVal-0.1)
        self.ui.xMinSlider.setValue(self.xmin)

        self.ui.densitySlider.setMinimum(20)
        self.ui.densitySlider.setMaximum(100)

        self.ui.stepSize.setMinimum(1)
        self.ui.stepSize.setMaximum(20)

    # UpdatePoints on self. 
    def updatePoints(self):
        # Adding points. 
        xdata = [obj.state[0] for obj in self.objs]
        ydata = [obj.state[1] for obj in self.objs]

        color_stack = []
        for obj in self.objs:
            color_stack.append(obj.color)

        color_stack = np.array(color_stack)

        if self.pts:
            self.pts.remove()
        self.pts = self.ax.scatter(xdata, ydata, color = color_stack)
        self.draw()

    # adding Points on Click event. 
    def addPointOnClick(self, event):
        if not event.inaxes:
            return 

        xclick = event.xdata
        yclick = event.ydata

        if xclick is not None and yclick is not None:
            newObj = MovingObject([xclick, yclick])
            self.objs.append(newObj)
        self.updatePoints()

    def click(self, event):
        if not event.inaxes:
            return

        # Get closest index event. 
        self.get_closest_index(event)

        if self._idx == None:
            if self.addMode:
                self.addPointOnClick(event)

        else:
            if self.selectMode:
                self.assignState()

    def assignState(self):
        obj = self.objs[self._idx]
        # Setting solver and colors. 
        if self.ui.RK4.isChecked():
            obj.set_solver('RK4')
            obj.set_color(self.solverColors['RK4'])

        if self.ui.MidPoint.isChecked():
            obj.set_solver('MidPoint')
            obj.set_color(self.solverColors['MidPoint'])

        if self.ui.ExplicitEuler.isChecked():
           obj.set_solver('ExplicitEuler')
           obj.set_color(self.solverColors['ExplicitEuler'])

        self.updatePoints()



    def get_closest_index(self, event):
        if not event.inaxes:
            return

        xdata = [obj.state[0] for obj in self.objs]
        ydata = [obj.state[1] for obj in self.objs]

        pts_array = np.hstack((np.array([xdata]).T, np.array([ydata]).T))
        cur_loc = np.array([[event.xdata, event.ydata]])
        # print(pts_array, cur_loc)
        dist = np.sqrt(np.sum((cur_loc - pts_array)**2, axis=1))
        # print("dist", dist)
        if len(dist) > 0:
            min_loc  = np.argmin(dist)
            if dist[min_loc] < (self.xmax - self.xmin)/20:
                self._idx = min_loc
            else:
                self._idx = None
        else:
            self._idx = None

    def OperationalMode(self):

        if self.ui.addPoints.isChecked():
            self.addMode = True
            self.selectMode = False

        elif self.ui.selectMode.isChecked():
            self.selectMode = True
            self.addMode = False

        else:
            self.selectMode = False
            self.addMode = False

        print("Add mode is", self.addMode)
        print("Select Mode is", self.selectMode)

    def update_quiver(self):
        self.quiver.remove()
        self.quiver = self.ax.quiver(self.X, self.Y, self.u, self.v)
        self.draw()

    def startAnimation(self):
        self.animateMode = True
        self.resetObjs = self.objs
        self.vectorFieldAnimation.event_source.start()
        # if not self.vectorFieldAnimation:
            # self.vectorFieldAnimation = animation.FuncAnimation(self.fig, self.animateStep, frames = 720, interval = 10)
            # self.vectorFieldAnimation.event_source.stop()

    # Stopping the animation. 
    def stopAnimation(self):
        self.vectorFieldAnimation.event_source.stop()

    def reset(self):
        if self.vectorFieldAnimation:
            self.vectorFieldAnimation = None

    # Derivative in current object state. 
    def getDerivative(self, obj):
        cur_state = obj.get_state()
        X, Y = cur_state[0], cur_state[1]

        # Current derivative. 
        curdX = eval(self.perPointU)
        curdY = eval(self.perPointV)
        return np.array([curdX, curdY])

    # Clear all is being clicked here. 
    def clearAll(self):
        if self.pts:
            self.pts.remove()

        # Clearing all the points. 
        self.objs = []
        self.pts = self.ax.scatter([], [], color = 'blue')

    # Runge Kutta method. 
    def RK4Step(self, obj):
        K1 = self.getDerivative(obj)
        K1pos = obj.state  
        
        K2pos = K1pos + (self.dt/2)*(K1)
        obj.set_state(K2pos)
        K2 = self.getDerivative(obj)
        
        K3pos = K1pos + (self.dt/2)*(K2)
        obj.set_state(K3pos)
        K3 = self.getDerivative(obj)

        K4pos = K1pos + (self.dt)*(K3)
        obj.set_state(K4pos)
        K4 = self.getDerivative(obj)

        # New state obtained here. 
        new_state = K1pos + (self.dt)*(K1/6 + K2/3 + K3/3 + K4/6)
        obj.set_state(new_state)

    # MidpointStep. 
    def MidPointStep(self, obj):
        x, y = obj.state[0], obj.state[1]

        # Updating current state. 
        cur_state = np.array([x, y])
        cur_derivative = self.getDerivative(obj)
        mid_state = cur_state + (self.dt/2)*cur_derivative
        obj.set_state(mid_state)
        
        # Mid derivative. 
        mid_derivative = self.getDerivative(obj)
        new_state = cur_state + self.dt*mid_derivative
    
        obj.set_state(new_state)

    # ExplicitEulerStep taken here. 
    def ExplicitEulerStep(self, obj):
        # x, y = obj.state[0], obj.state[1]

        # Current derivative. 
        cur_derivative = self.getDerivative(obj)
        cur_state = obj.state

        # Updating object state. 
        obj.state = cur_state + self.dt*(cur_derivative)

    # Draw figure function.
    def draw_figure(self):

        # Axes being cleared. 
        self.ax.clear()
        self.ax.set_xlim(self.xmin, self.xmax)
        self.ax.set_ylim(self.ymin, self.ymax)
        self.ax.grid()

        X = np.linspace(self.xmin, self.xmax, self.density)#round(self.density))
        Y = np.linspace(self.ymin, self.ymax, self.density)#round(self.density))

        self.X, self.Y = np.meshgrid(X, Y)

        # U and V being evaluated. 
        self.u = eval(self.xText)
        self.v = eval(self.yText)

        # We get x data, y data and colors for each of the objects. 
        xdata = [obj.state[0] for obj in self.objs]
        ydata = [obj.state[1] for obj in self.objs]
        color_stack = []
        xdata = []
        ydata = []

        for obj in self.objs:
            xdata.append(obj.state[0])
            ydata.append(obj.state[1])
            color_stack.append(obj.color)


        # Quiver, pts and draw function here. 
        self.quiver = self.ax.quiver(self.X, self.Y, self.u, self.v)
        self.pts = self.ax.scatter(xdata, ydata, color = color_stack)
        self.draw()

    def toggleXMin(self):
        self.xmin = self.ui.xMinSlider.value()
        self.draw_figure()

    # Stepsize. 
    def toggleStepSize(self):
        self.dt = self.ui.stepSize.value()/100.
        print("Step size", self.dt)
    
    def toggleXMax(self):
        self.xmax = self.ui.xMaxSlider.value()
        self.draw_figure()

    def toggleYMin(self):
        self.ymin = self.ui.yMinSlider.value()
        self.draw_figure()

    def toggleYMax(self):
        self.ymax = self.ui.yMaxSlider.value()
        self.draw_figure()

    def toggleDensity(self):
        self.density = self.ui.densitySlider.value()
        self.draw_figure()

    def toggleAnimation(self):
        self.animateMode = not self.animateMode

    # AnimateStep function. 
    def animateStep(self, idx):
        offsets = []
        # print("Animate step called")
        if self.animateMode:
            for obj in self.objs:
                if not self.outofBounds(obj):

                    if obj.solver == 'RK4':
                        self.RK4Step(obj)
                    elif obj.solver == 'ExplicitEuler':
                        self.ExplicitEulerStep(obj)
                    elif obj.solver == 'MidPoint':
                        self.MidPointStep(obj)

                    offsets.append([obj.state[0], obj.state[1]])

                else:
                    del obj
        
            if len(offsets) > 0:
                self.pts.set_offsets(offsets)

    # Check whether the value is outofBounds.
    def outofBounds(self, obj):
        xLoc, yLoc = obj.state[0], obj.state[1]
        cond =  (xLoc > self.absXMax or xLoc < self.absXMin or yLoc > self.absYMax or yLoc < self.absYMin)
        return cond

    # Compute formula from X and Y.
    def computeFormulaXandY(self):
        xText = self.ui.uLineEdit.text()
        yText = self.ui.vLineEdit.text()

        xText = xText.upper()
        yText = yText.upper()

        self.perPointU = xText
        self.perPointU = self.perPointU.replace("SIN", "np.sin").replace("COS", "np.cos")

        # Processing yText and replace sin and cosine values. 
        self.perPointV = yText
        self.perPointV = self.perPointV.replace("SIN", "np.sin").replace("COS", "np.cos")

        # X text and Y text being processed on grid. 
        xText = self.perPointU.replace("X", "self.X")
        xText = xText.replace("Y", "self.Y")

        yText = self.perPointV.replace("X", "self.X")
        yText = yText.replace("Y", "self.Y")

        if xText == "":
            xText = "0"
        if yText == "":
            yText = "0"

        self.xText = xText 
        self.yText = yText

        self.u = eval(self.xText)
        self.v = eval(self.yText)
        self.update_quiver()

    def mouse_move(self, event):
        if (self._idx is None) or self.selectMode:
            return

        x, y = event.xdata, event.ydata
        self.objs[self._idx].set_state([x,y])
        self.updatePoints()

    def mouse_release(self, event):
        self._idx = None
