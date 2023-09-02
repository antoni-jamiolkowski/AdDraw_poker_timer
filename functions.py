# # import matplotlib
# # import matplotlib.pyplot as plt

# # matplotlib.use('TkAgg')

from enum import Enum
from math import asin, cos, degrees, expm1, log10, radians, sin, sinh

# import pyqtgraph as pg
# from PyQt5 import QtWidgets
# from pyqtgraph import PlotWidget, plot


from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QSlider


class MyFunc(Enum):
  SINH = sinh
  COS = cos
  SIN = sin
  ASIN = asin
  EXP = expm1

def gen_func_exp(length, myfunc):
  for x in range(length):
    yield myfunc(x)


def round_to_smallest_chip_increment(x: int, smallest_chip_increment: int = 50):
  min = x // smallest_chip_increment
  min_val = min * smallest_chip_increment
  max_val = (min + 1) * smallest_chip_increment
  if (x - min_val)  < (max_val - x) and min_val > 0:
    return min_val
  return max_val

def gen_func(start_val, length, scaling_factor=None, func=None, round_it: bool = True):
  last_x = start_val
  for x in range(length):
    new_val = func(last_x, x if not scaling_factor else scaling_factor)
    if scaling_factor:
      if round_it:
        yield round_to_smallest_chip_increment(last_x)
      else:
        yield last_x
      last_x = new_val
    else:
      yield new_val
def scale_by_factor(x, val):
  return x * val

def scale_linear(x, val):
  return x * (val+1)

def get_last_version(start_val, iters, scale):
  out_val = start_val
  for _ in range(iters):
    out_val = out_val * scale
  return out_val


# class MainWindow(QtWidgets.QMainWindow):

#   def __init__(self, *args, **kwargs):
#     super(MainWindow, self).__init__(*args, **kwargs)

#     self.graphWidget = pg.PlotWidget()
#     self.setCentralWidget(self.graphWidget)

#     hour = [1,2,3,4,5,6,7,8,9,10]
#     temperature = [30,32,34,32,33,31,29,32,35,45]

#     # plot data: x, y values
#     self.graphWidget.plot(hour, temperature)


# if __name__ == "__main__":
#   # lvls = 15
#   # start_val = 100
#   # scaling_factor = 1.2
#   # switch_point = 9
#   # generator1 = gen_func(start_val, lvls, None, scale_linear)
#   # linear = list(generator1)

#   # start_val = get_last_version(linear[switch_point], switch_point, 1/scaling_factor)

#   # generator2 = gen_func(linear[switch_point], lvls, scaling_factor, scale_by_factor, round_it=True)
#   # generator3 = gen_func(start_val, lvls, scaling_factor, scale_by_factor, round_it=True)


#   # scaled = list(generator2)
#   # scaled_rev = list(generator3)

#   # y = []
#   # for _ in range(0, lvls):
#   #   if _ < switch_point:
#   #     y.append(linear[_])
#   #   else:
#   #     y.append(scaled[_ - switch_point])


#   # print(f"LIN       : {linear}")
#   # print(f"SCALE     : {scaled}")
#   # print(f"SCALE REV : {scaled_rev}")
#   # print(f"FINAL     : {y}")

  # plt.plot([x for x in linear], 'ob--', markersize=15)
  # plt.plot([x for x in scaled_rev], 'go--', markersize=15)
  # plt.plot([x for x in y], 'r^--', markersize=15)
  # plt.legend(["linear", str(scaling_factor), "combo"])
  # plt.ylabel('BB value')
  # plt.grid(True)
  # plt.tight_layout()
  # plt.
  # plt.show()




from PyQt5 import QtWidgets
from PyQt5 import QtCore
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import sys  # We need sys so that we can pass argv to QApplication
import os

class MainWindow(QtWidgets.QMainWindow):

    def changeValue(self, a0):
      self.scaling_factor = int(a0) / 10 + 1
      self.calculate_plots()
      self.updatePlots()

    def updatePlots(self):
      self.data_line_y.setData(self.x, self.y)  # Update the data.
      self.data_line_s.setData(self.x, self.scaled)  # Update the data.
      self.data_line_l.setData(self.x, self.linear)  # Update the data.

    def changeSwitchingPointValue(self, a0):
      self.switch_point = int(a0)
      self.calculate_plots()
      self.updatePlots()

    def calculate_plots(self):
      generator1 = gen_func(self.start_val, self.lvl_n, None, scale_linear)
      linear = list(generator1)
      start_val = get_last_version(linear[self.switch_point], self.switch_point, 1/self.scaling_factor)
      generator2 = gen_func(linear[self.switch_point], self.lvl_n, self.scaling_factor, scale_by_factor, round_it=True)
      generator3 = gen_func(start_val, self.lvl_n, self.scaling_factor, scale_by_factor, round_it=True)
      scaled = list(generator2)
      scaled_rev = list(generator3)
      y = []
      for _ in range(0, self.lvl_n):
        if _ < self.switch_point:
          y.append(linear[_])
        else:
          y.append(scaled[_ - self.switch_point])

      self.y = y
      self.linear = linear
      self.scaled = scaled_rev

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.lvl_n = 15
        self.x = list(range(15))
        self.scaling_factor = 1.2
        self.switch_point = 6
        self.start_val = 100

        self.calculate_plots()

        self.graphWidget = pg.PlotWidget()
        self.slider = QSlider(QtCore.Qt.Horizontal, self)
        self.slider.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.slider.setTickPosition(QSlider.TicksBothSides)
        self.slider.setTickInterval(5)
        self.slider.setMaximum(10)
        self.slider.setMinimum(1)
        self.slider.setValue(int((self.scaling_factor-1)*10))
        self.slider.setSingleStep(1)
        self.slider.valueChanged[int].connect(self.changeValue)

        self.slider_start_val = QSlider(QtCore.Qt.Horizontal, self)
        self.slider_start_val.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.slider_start_val.setTickPosition(QSlider.TicksBothSides)
        self.slider_start_val.setTickInterval(5)
        self.slider_start_val.setMaximum(self.lvl_n)
        self.slider_start_val.setMinimum(1)
        self.slider_start_val.setValue((self.switch_point))
        self.slider_start_val.setSingleStep(1)
        self.slider_start_val.valueChanged[int].connect(self.changeSwitchingPointValue)


        # self.slider.setFixedWidth(10)


        # self.slider.set
        # self.slider.setSizeIncrement(QtCore.QSize(1, 1))
        # # self.slider.setFont()
        # self.slider.setLayoutDirection(QtCore.Qt.LeftToRight)
        # self.slider.setAutoFillBackground(False)
        # sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        # sizePolicy.setHorizontalStretch(0)
        # sizePolicy.setVerticalStretch(0)
        # sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        # self.slider.setSizePolicy(sizePolicy)
        self.setGeometry(0,0, 1920,1080)
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.graphWidget)
        self.layout.addWidget(self.slider)
        self.layout.addWidget(self.slider_start_val)

        widget = QtWidgets.QWidget()
        widget.setLayout(self.layout)
        self.setCentralWidget(widget)


        # plot data: x, y values
        pen = pg.mkPen(width=10, style=QtCore.Qt.DashDotDotLine)
        self.data_line_s = self.graphWidget.plot(self.x, self.scaled, name="Scaled", pen=pen, symbol="o", symbolSize=30, symbolBrush=('b'))
        self.data_line_l = self.graphWidget.plot(self.x, self.linear, name="Linear", pen=pen, symbol="o", symbolSize=30, symbolBrush=('g'))
        self.data_line_y = self.graphWidget.plot(self.x, self.y, name="Combined", pen=pen, symbol="o", symbolSize=30, symbolBrush=('r'))
        styles = {'color':'r', 'font-size':'20px'}
        self.graphWidget.setLabel('left', 'BigBlind', **styles)
        self.graphWidget.setLabel('bottom', 'Level', **styles)
        self.graphWidget.addLegend()
        self.graphWidget.showGrid(x=True, y=True)
        self.graphWidget.setBackground('w')




if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())
