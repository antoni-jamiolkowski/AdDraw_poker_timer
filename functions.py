from enum import Enum
from math import asin, cos, degrees, expm1, log10, radians, sin, sinh

from PyQt5.QtWidgets import QHBoxLayout, QSlider, QVBoxLayout


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


import os
import sys  # We need sys so that we can pass argv to QApplication

import pyqtgraph as pg
from PyQt5 import QtCore, QtWidgets
from pyqtgraph import PlotWidget, plot

from utils import MyFonts, MyLabel, MyQLineEdit


class MySlider(QtWidgets.QWidget):
  def __init__(self, name:str = "Slider", init_val:int = 5, range_low :int = 1, range_high:int = 10, step:int= 1):
    super().__init__()
    self.slider = QSlider(QtCore.Qt.Horizontal)
    self.slider.setFocusPolicy(QtCore.Qt.StrongFocus)
    self.slider.setTickPosition(QSlider.TicksBothSides)
    self.slider.setTickInterval(int(step))
    self.slider.setMaximum(int(range_high))
    self.slider.setMinimum(int(range_low))
    self.slider.setValue(int(init_val))
    self.slider.setSingleStep(int(step))

    self.line_edit = MyQLineEdit(init_val)
    self.line_edit.setText(f"{init_val}")

    self.label = MyLabel("val", MyFonts.Blinds)
    self.label.setText(f"{name}")

    self.layout = QHBoxLayout(self)
    self.layout.addWidget(self.label)
    self.layout.addWidget(self.line_edit)
    self.layout.addWidget(self.slider)

class MainWindow(QtWidgets.QMainWindow):

    def updatePlots(self):
      self.data_line_y.setData(self.x, self.y)  # Update the data.
      self.data_line_s.setData(self.x, self.scaled)  # Update the data.
      self.data_line_l.setData(self.x, self.linear)  # Update the data.
      self.data_line_sw.setData([self.switch_point], [self.y[self.switch_point]])

    def changeScalingValue(self, a0):
      self.scaling_factor = int(a0) / 10
      self.calculate_plots()
      self.scale_slider.line_edit.updateText(self.scaling_factor)
      self.updatePlots()

    def changeSwitchingPointValue(self, a0):
      self.switch_point = int(a0)
      self.calculate_plots()
      self.switch_point_slider.line_edit.updateText(a0)
      self.updatePlots()

    def changeStartValue(self, a0):
      self.start_val = int(a0) * 50
      self.calculate_plots()
      self.start_val_slider
      self.updatePlots()

    def changeLvlNumber(self, a0):
      self.lvl_n = int(a0)
      self.x = list(range(0, self.lvl_n, 1))
      if self.switch_point > len(self.x):
        self.switch_point = self.x[-1]
        self.switch_point_slider.line_edit.updateText(self.switch_point)
      self.switch_point_slider.slider.setMaximum(self.lvl_n-1)
      self.calculate_plots()
      self.lvl_n_slider.line_edit.updateText(self.lvl_n)
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
        self.x = list(range(self.lvl_n))
        self.scaling_factor = 1.2
        self.switch_point = 6
        self.start_val = 200

        self.calculate_plots()

        self.graphWidget = pg.PlotWidget()

        lowest_scaling_factor = int(1.1 * 10)
        max_scaling_factor = int(1.5 * 10)
        step = int(0.1 * 10)
        self.scale_slider = MySlider(name="SF",
                                     init_val=self.scaling_factor * 10,
                                     range_low=lowest_scaling_factor,
                                     range_high=max_scaling_factor,
                                     step = step)
        self.scale_slider.slider.valueChanged[int].connect(self.changeScalingValue)

        self.switch_point_slider = MySlider(name="SP",
                                            init_val=self.switch_point,
                                            range_low=1,
                                            range_high=self.lvl_n,
                                            step=1)
        self.switch_point_slider.slider.valueChanged[int].connect(self.changeSwitchingPointValue)

        start_val_step = 50
        min_start_val = start_val_step
        max_start_val = 500

        self.start_val_slider = MySlider(name="SV",
                                         init_val=self.start_val//start_val_step,
                                         range_low=min_start_val//start_val_step,
                                         range_high=max_start_val//start_val_step,
                                         step=start_val_step//start_val_step)
        self.start_val_slider.slider.valueChanged[int].connect(self.changeStartValue)



        self.lvl_n_slider = MySlider(name="LVL_N",
                                     init_val=self.lvl_n,
                                     range_low=2,
                                     range_high=2*self.lvl_n,
                                     step=1)
        self.lvl_n_slider.slider.valueChanged[int].connect(self.changeLvlNumber)


        self.setGeometry(0,0, 1920,1080)
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.graphWidget)
        self.layout.addWidget(self.scale_slider)
        self.layout.addWidget(self.switch_point_slider)
        self.layout.addWidget(self.start_val_slider)
        self.layout.addWidget(self.lvl_n_slider)

        widget = QtWidgets.QWidget()
        widget.setLayout(self.layout)
        self.setCentralWidget(widget)


        # plot data: x, y values
        pen = pg.mkPen(width=10, style=QtCore.Qt.DashDotDotLine)
        self.data_line_s = self.graphWidget.plot(self.x, self.scaled, name="Scaled", pen=pen, symbol="o", symbolSize=30, symbolBrush=('b'))
        self.data_line_l = self.graphWidget.plot(self.x, self.linear, name="Linear", pen=pen, symbol="o", symbolSize=30, symbolBrush=('g'))
        self.data_line_y = self.graphWidget.plot(self.x, self.y, name="Combined", pen=pen, symbol="o", symbolSize=30, symbolBrush=('r'))
        self.data_line_sw = self.graphWidget.plot([self.switch_point], [self.y[self.switch_point]], name="SW_PT", pen=pen, symbol="o", symbolSize=40, symbolBrush=('yellow'))
        styles = {'color':'r', 'font-size':'20px'}
        self.graphWidget.setLabel('left', 'BigBlind', **styles)
        self.graphWidget.setLabel('bottom', 'Level', **styles)
        self.graphWidget.addLegend()
        self.graphWidget.setMouseEnabled(False,False)
        self.graphWidget.showGrid(x=True, y=True)
        self.graphWidget.setBackground('w')




if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())
