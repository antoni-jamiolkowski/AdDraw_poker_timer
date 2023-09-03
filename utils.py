from enum import Enum, IntEnum, unique
from typing import Optional

import pyqtgraph as pg
from numpy import asarray
from PyQt5 import QtCore
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QFont, QFontDatabase, QMouseEvent
from PyQt5.QtWidgets import (QHBoxLayout, QLabel, QLineEdit, QMessageBox,
                             QPushButton, QSizePolicy, QSlider, QVBoxLayout,
                             QWidget)


@unique
class PokerMode(IntEnum):
  NORMAL = 0
  HEADSUP = 1


@unique
class WindowGeometry(Enum):
  UHD = QSize(3840, 2160)
  FHD = QSize(1920, 1080)
  VGA = QSize(640, 480)
  QVGA = QSize(320, 240)


@unique
class FontFamilies(Enum):
  ORIGAMI_MOMMY = "ORIGAMI MOMMY"
  MONOFONTO = "Monofonto"
  SPACEMONO = "Monospace"
  NOTOMONO = "Noto Mono"
  TLWGMONO = "Tlwg Mono"
  FREEMONO = "FreeMono"
  GOMONO = "Go Mono"


class MyTime:
  def __init__(self, m, s):
    self.m = m
    self.s = s

  # @staticmethod
  def _list(self):
    return list((self.m, self.s))

  def _arr(self):
    return asarray([self.m, self.s])


class PokerConfig:
  LVL_N : int = -1 # Number of Levels in the PokerGame
  LINEAR_BB_STEP : int = -1 # BigBlind value to increase the BB value by every Level
  SWITCH_LVL_IDX : int = -1 # After which level Blinds should switch to scaling by scaling_factor
  SCALING_FACTOR : int = -1 # scaling factor to scale the blinds by after Switch level
  CHIP_INCREMENT : int = -1 # Smallest difference between chips
  BIG_BLIND_VALUES : list = [] # BB Values for every level of the game
  LEVEL_PERIOD : MyTime = MyTime(-1,-1)


Family = FontFamilies.MONOFONTO.value
Family2 = FontFamilies.MONOFONTO.value
Family3 = FontFamilies.MONOFONTO.value


class PokerGameState:
  def __init__(self,
               config: PokerConfig
               ):
    self.current_level = 0
    self.update_config(config)

  def update_config(self, config: PokerConfig, update_counters: bool = True):
    self.config = config
    if update_counters:
      self.minute = config.LEVEL_PERIOD.m
      self.second = config.LEVEL_PERIOD.s
    self.update_blinds()

  def update_blinds(self) -> None:
    self.big_blind = self.config.BIG_BLIND_VALUES[self.current_level]
    self.small_blind = int(self.big_blind / 2)
    if (self.current_level != len(self.config.BIG_BLIND_VALUES)-1):
      self.nxt_big_blind = self.config.BIG_BLIND_VALUES[self.current_level+1]
      self.nxt_small_blind = int(self.nxt_big_blind / 2)
      return
    # If current level is the last one, next blinds are not available
    self.nxt_big_blind = "N/A"
    self.nxt_small_blind = "N/A"

  def counter_increment(self):
    if self.minute == 0 and self.second == 0:
      self.current_level += 1
      self.minute, self.second = self.config.LEVEL_PERIOD._list()
      return
    if self.second == 0:
      self.minute -= 1
      self.second = 59
      return
    self.second -= 1
    self.update_blinds()

  def nxt_level(self):
    self.current_level += 1
    self.minute = self.config.LEVEL_PERIOD.m
    self.second = self.config.LEVEL_PERIOD.s
    self.update_blinds()

  def prev_level(self):
    if self.current_level != 1:
      self.current_level -= 1
    self.minute = self.config.LEVEL_PERIOD.m
    self.second = self.config.LEVEL_PERIOD.s
    self.update_blinds()

  def reset_level(self):
    self.current_level = 1
    self.minute = self.config.LEVEL_PERIOD.m
    self.second = self.config.LEVEL_PERIOD.s
    self.update_blinds()

  def _list(self):
    return (self.current_level, self.minute, self.second,
            self.big_blind, self.small_blind,
            self.nxt_big_blind, self.nxt_small_blind)


def setupQFontDataBase():
  qfont_db = QFontDatabase()
  qfont_db.addApplicationFont("./fonts/origami-mommy/origa___.ttf")
  qfont_db.addApplicationFont("./fonts/monofont/monofontorg.otf")
  return qfont_db


class MyFonts:
  Timer = QFont()
  Timer.setFamily(Family)
  Timer.setFixedPitch(True)
  Timer.setBold(True)
  Blinds = QFont()
  Blinds.setBold(True)
  Blinds.setFamily(Family2)
  PushButton = QFont()
  PushButton.setBold(True)
  PushButton.setFamily(Family3)


class MyForm(QWidget):
  def __init__(self, name, font, value):
    super().__init__()
    self.name = name
    self.label = MyLabel(name, font)
    self.line_edit = MyQLineEdit(value)
    self.layout = QHBoxLayout(self)
    self.layout.addWidget(self.label    )
    self.layout.addWidget(self.line_edit)

  def updateText(self, value: Optional[str] = None):
    self.label.setText(self.name)
    self.line_edit.updateText(value)

  def updateFonts(self, font_size: int):
    labelFont = self.label.font()
    labelFont.setPointSize(font_size)
    self.label.setFont(labelFont)
    lineEditFont = self.line_edit.font()
    lineEditFont.setPointSize(font_size)
    self.line_edit.setFont(lineEditFont)


class Level_Timer_Control(QWidget):
  def __init__(self, parent: QWidget) -> None:
    super().__init__(parent)
    self.pb_prev_level = MyPushButton("prev_lvl_pb", whats_this="Button that goes to Level-1, cannot go below 1")
    self.pb_next_lvl = MyPushButton("next_lvl_pb", whats_this="Button that goes to Level+1")
    self.pb_start_stop = MyPushButton("start_stop_pb", whats_this="Button that starts/stops the timer")
    self.layout = QHBoxLayout(self)
    self.layout.addWidget(self.pb_prev_level)
    self.layout.addWidget(self.pb_start_stop)
    self.layout.addWidget(self.pb_next_lvl)

  def updateFonts(self, font_size: int):
    font = self.pb_prev_level.font()
    font.setPointSize(font_size)
    self.pb_prev_level.setFont(font)
    font = self.pb_next_lvl.font()
    font.setPointSize(font_size)
    self.pb_next_lvl.setFont(font)
    font = self.pb_start_stop.font()
    font.setPointSize(font_size)
    self.pb_start_stop.setFont(font)


class MyQLineEdit(QLineEdit):
  def __init__(self, value: int, font: MyFonts = MyFonts.Blinds):
    super().__init__()
    self.value = value
    self.setText(f"{value}")
    self.setSizeIncrement(QtCore.QSize(1, 1))
    self.setFont(font)
    self.setLayoutDirection(QtCore.Qt.LeftToRight)
    self.setAutoFillBackground(False)
    sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(0)
    sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
    self.setSizePolicy(sizePolicy)

  def updateText(self,
                 value: Optional[str] = None):
    if value is not None:
      self.value = int(value)
    self.setText(f"{self.value}")

  def mousePressEvent(self, a0) -> None:
    self.setText("")
    return super().mousePressEvent(a0)

  def leaveEvent(self, a0) -> None:
    self.updateText()
    return super().leaveEvent(a0)


class MyLabel(QLabel):
  def __init__(self,
               name: str,
               font : QFont,
               layout_dir: QtCore.Qt.AlignmentFlag = QtCore.Qt.AlignmentFlag.AlignCenter,
               autofillbg: bool = True,
               scaled_content: bool = True,
               line_width: int = 2,
               color : str = "white",
               bg_color: str = "rgba(40,40,40,70%)",
               border_color: str = "gold",
               padding: str = "0"):
    super().__init__()
    self.setSizeIncrement(QtCore.QSize(5, 5))
    self.setFont(font)
    self.setLayoutDirection(QtCore.Qt.LeftToRight)
    self.setAutoFillBackground(autofillbg)
    self.setScaledContents(scaled_content)
    self.setAlignment(layout_dir)
    self.setObjectName(name)
    self.setLineWidth(line_width)
    self.setStyleSheet(f"background-color: {bg_color};"
                       f"color: {color};"
                       f"border: 5px solid {border_color};"
                       f"border-radius: 20px;"
                       f"padding: {padding}px")


class MyPushButton(QPushButton):
  def __init__(self,
               name : str,
               whats_this :str = "This is a button, DUH",
               font: QFont = MyFonts.PushButton,
               unclicked_style_sheet: str = "border-radius: 0; background-color: rgba(220, 220, 220, 95%); border: 2px solid black;"):
    super().__init__()
    sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(0)
    sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
    self.setSizePolicy(sizePolicy)
    self.setFont(font)
    self.setWhatsThis(whats_this)
    self.setObjectName(name)
    self.setStyleSheet("QPushButton {" f"{unclicked_style_sheet}" "}"
                        "QPushButton:pressed{"
                        "  background-color: rgba(40, 40, 40, 95%);"
                        "  border:2px solid black;"
                        "color : white"
                        "}"
                        )

  def mousePressEvent(self, e: QMouseEvent) -> None:
    if e.button() == 2:
      print(self.whatsThis())
      x = QMessageBox(self)
      x.setWindowTitle("Info")
      x.setText(self.whatsThis())
      x.setIcon(QMessageBox.Information)
      x.exec()
    else:
      return super().mousePressEvent(e)


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


class MySlider(QWidget):
  def __init__(self,
               name: str = "Slider",
               init_val: int = 5,
               range_low : int = 1,
               range_high: int = 10,
               step: int = 1):
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

class SettingsWindow(QWidget):
  def __init__(self, config: PokerConfig):
    super().__init__()
    self.config = config
    self.x = list(range(config.LVL_N))
    self.calculate_plots()
    self.graphWidget = pg.PlotWidget()

    lowest_scaling_factor = int(1.1 * 10)
    max_scaling_factor = int(1.5 * 10)
    step = int(0.1 * 10)
    self.scale_slider = MySlider(name="SF",
                                  init_val=self.config.SCALING_FACTOR * 10,
                                  range_low=lowest_scaling_factor,
                                  range_high=max_scaling_factor,
                                  step = step)
    self.scale_slider.slider.valueChanged[int].connect(self.changeScalingFactorValue)

    self.switch_lvl_idx_slider = MySlider(name="SP",
                                        init_val=self.config.SWITCH_LVL_IDX,
                                        range_low=1,
                                        range_high=self.config.LVL_N,
                                        step=1)
    self.switch_lvl_idx_slider.slider.valueChanged[int].connect(self.changeSwitchingPointValue)

    linear_bb_slider_step = 50
    min_start_val = linear_bb_slider_step
    max_start_val = 500
    self.lin_bb_step_slider = MySlider(name="SV",
                                      init_val=self.config.LINEAR_BB_STEP//linear_bb_slider_step,
                                      range_low=min_start_val//linear_bb_slider_step,
                                      range_high=max_start_val//linear_bb_slider_step,
                                      step=linear_bb_slider_step//linear_bb_slider_step)
    self.lin_bb_step_slider.slider.valueChanged[int].connect(self.changeLinearBBStepValue)

    self.lvl_n_slider = MySlider(name="LVL_N",
                                  init_val=self.config.LVL_N,
                                  range_low=2,
                                  range_high=2*self.config.LVL_N,
                                  step=1)
    self.lvl_n_slider.slider.valueChanged[int].connect(self.changeLvlNumberValue)

    self.apply_button = MyPushButton("Apply!", "This button sets GameConfig based on slider values")
    self.apply_button.setText("Apply!")
    self.apply_and_close_button = MyPushButton("Apply!", "This button sets GameConfig based on slider values")
    self.apply_and_close_button.setText("Apply&Close!")

    self.resize(WindowGeometry.VGA.value)
    self.layout = QVBoxLayout(self)
    self.layout.addWidget(self.graphWidget)
    self.layout.addWidget(self.scale_slider)
    self.layout.addWidget(self.switch_lvl_idx_slider)
    self.layout.addWidget(self.lin_bb_step_slider)
    self.layout.addWidget(self.lvl_n_slider)

    self.layoutX = QHBoxLayout(self)
    self.layoutX.addWidget(self.apply_button)
    self.layoutX.addWidget(self.apply_and_close_button)
    self.layout.addLayout(self.layoutX)

    pen = pg.mkPen(width=10, style=QtCore.Qt.DashDotDotLine)
    self.data_line_s = self.graphWidget.plot(self.x, self.scaled, name="Scaled", pen=pen, symbol="o", symbolSize=30, symbolBrush=('b'))
    self.data_line_l = self.graphWidget.plot(self.x, self.linear, name="Linear", pen=pen, symbol="o", symbolSize=30, symbolBrush=('g'))
    self.data_line_y = self.graphWidget.plot(self.x, self.y, name="Combined", pen=pen, symbol="o", symbolSize=30, symbolBrush=('r'))
    self.data_line_sw = self.graphWidget.plot([self.config.SWITCH_LVL_IDX], [self.y[self.config.SWITCH_LVL_IDX]], name="SW_PT", pen=pen, symbol="o", symbolSize=40, symbolBrush=('yellow'))
    styles = {'color':'r', 'font-size':'20px'}
    self.graphWidget.setLabel('left', 'BigBlind', **styles)
    self.graphWidget.setLabel('bottom', 'Level', **styles)
    self.graphWidget.addLegend()
    self.graphWidget.setMouseEnabled(False,False)
    self.graphWidget.showGrid(x=True, y=True)
    self.graphWidget.setBackground('w')


  def updatePlots(self):
    self.data_line_y.setData(self.x, self.y)  # Update the data.
    self.data_line_s.setData(self.x, self.scaled)  # Update the data.
    self.data_line_l.setData(self.x, self.linear)  # Update the data.
    self.data_line_sw.setData([self.config.SWITCH_LVL_IDX], [self.y[self.config.SWITCH_LVL_IDX]])

  def changeScalingFactorValue(self, a0):
    self.config.SCALING_FACTOR = int(a0) / 10
    self.calculate_plots()
    self.scale_slider.line_edit.updateText(self.config.SCALING_FACTOR)
    self.updatePlots()

  def changeSwitchingPointValue(self, a0):
    self.config.SWITCH_LVL_IDX = int(a0)
    self.calculate_plots()
    self.switch_lvl_idx_slider.line_edit.updateText(a0)
    self.updatePlots()

  def changeLinearBBStepValue(self, a0):
    self.config.LINEAR_BB_STEP = int(a0) * 50
    self.calculate_plots()
    self.lin_bb_step_slider.line_edit.updateText(a0*50)
    self.updatePlots()

  def changeLvlNumberValue(self, a0):
    self.config.LVL_N = int(a0)
    self.x = list(range(0, self.config.LVL_N, 1))
    if self.config.SWITCH_LVL_IDX > len(self.x):
      self.config.SWITCH_LVL_IDX = self.x[-1]
      self.switch_lvl_idx_slider.line_edit.updateText(self.config.SWITCH_LVL_IDX)
    self.switch_lvl_idx_slider.slider.setMaximum(self.config.LVL_N-1)
    self.calculate_plots()
    self.lvl_n_slider.line_edit.updateText(self.config.LVL_N)
    self.updatePlots()

  def calculate_plots(self):
    lvl_n = self.config.LVL_N
    switch_lvl_idx = self.config.SWITCH_LVL_IDX
    scale_f = self.config.SCALING_FACTOR
    lin_bb_step = self.config.LINEAR_BB_STEP
    generator1 = gen_func(lin_bb_step, lvl_n, None, scale_linear)
    linear = list(generator1)
    scale_start_val = get_last_version(linear[switch_lvl_idx], switch_lvl_idx, 1/scale_f)
    generator2 = gen_func(linear[switch_lvl_idx], lvl_n, scale_f, scale_by_factor, round_it=True)
    generator3 = gen_func(scale_start_val, lvl_n, scale_f, scale_by_factor, round_it=True)
    scaled = list(generator2)
    scaled_rev = list(generator3)
    y = []
    for _ in range(0, lvl_n):
      if _ < switch_lvl_idx:
        y.append(linear[_])
      else:
        y.append(scaled[_ - switch_lvl_idx])

    self.y = y
    self.linear = linear
    self.scaled = scaled_rev
    self.config.BIG_BLIND_VALUES = [int(x) for x in y]