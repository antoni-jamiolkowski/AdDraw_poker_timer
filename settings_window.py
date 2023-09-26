import json
from pathlib import Path

import pyqtgraph as pg
from PyQt5 import QtCore
from PyQt5.QtWidgets import (QFileDialog, QGridLayout, QHBoxLayout,
                             QVBoxLayout, QWidget)

from utils import *


class SettingsWindow(QWidget):
  def __init__(self, config: PokerConfig, bg_color: str = "rgb(120,120,120)"):
    super().__init__()
    self.resize(WindowGeometry.SETTINGS.value)
    self.setStyleSheet(f" background-color: {bg_color};")
    self.cfg = config
    self.x = list(range(config.LVL_N))
    if self.cfg.BIG_BLIND_VALUES == [] or self.cfg.BIG_BLIND_VALUES == -1: # if uninitialized
      print("BIG_BLIND_VALUES are empty! calculating values from plots")
      self.calculate_plots()
    self.sizePolicy_Std = get_std_size_policy(self)
    grand_layout = QHBoxLayout(self)
    self.setLayout(grand_layout)
    # Sliders
    self.sliders = {}
    self.scale_factor_scale = int(1 / self.cfg.SCALE_FACTOR_STEP)
    lowest_scaling_factor = int(self.cfg.MIN_SCALE_FACTOR * self.scale_factor_scale)
    max_scaling_factor = int(self.cfg.MAX_SCALE_FACTOR * self.scale_factor_scale)
    self.sliders["scale"] = MySlider(name="ScaleF",
                                     init_val=int(self.cfg.SCALING_FACTOR * self.scale_factor_scale),
                                     init_text=self.cfg.SCALING_FACTOR,
                                     range_low=lowest_scaling_factor,
                                     range_high=max_scaling_factor,
                                     step = 1)

    self.sliders["switch_lvl_idx"] = MySlider(name="SwitchLvl",
                                              init_val=self.cfg.SWITCH_LVL_IDX,
                                              init_text=self.cfg.SWITCH_LVL_IDX,
                                              range_low=1,
                                              range_high=self.cfg.LVL_N,
                                              step=1)

    self.lin_bb_step_scale = self.cfg.MIN_LINEAR_BB_STEP
    min_start_val = self.lin_bb_step_scale
    max_start_val = self.cfg.MAX_LINEAR_BB_STEP
    self.sliders["lin_bb_step"] = MySlider(name="LinBBStep",
                                       init_val=self.cfg.LINEAR_BB_STEP//self.lin_bb_step_scale,
                                       init_text= self.cfg.LINEAR_BB_STEP,
                                       range_low=min_start_val//self.lin_bb_step_scale,
                                       range_high=max_start_val//self.lin_bb_step_scale,
                                       step=1)

    self.sliders["lvl_n"] = MySlider(name="LvlNum",
                                  init_val=self.cfg.LVL_N,
                                  init_text=self.cfg.LVL_N,
                                  range_low=2,
                                  range_high=2*self.cfg.LVL_N,
                                  step=1)

    # Buttons
    self.buttons = {}
    self.buttons["apply"] = MyPushButton("apply_btn",
                                     text="Apply!",
                                     whats_this="This button sets GameConfig based on slider values")

    self.buttons["apply_and_close"] = MyPushButton("apply_close_btn",
                                               text="Apply and Close!",
                                               whats_this="This button sets GameConfig based on slider values")

    self.buttons["load_config"] = MyPushButton("config_load", text="Load Config", whats_this="Loads Config from file",
                                    font=self.buttons["apply_and_close"].font())
    self.buttons["save_config"] = MyPushButton("config_save", text="Save Config", whats_this="Saves Config to file",
                                    font=self.buttons["apply_and_close"].font())

    # Config
    self.cfg_window = ConfigWindow(config)

    # Graph
    self.graphWidget = pg.PlotWidget(self)
    self.graphWidget.setSizePolicy(self.sizePolicy_Std)
    self.cfg_window.setSizePolicy(self.sizePolicy_Std)

    pen = pg.mkPen(width=10, style=QtCore.Qt.DashDotDotLine)
    self.data_line_s = self.graphWidget.plot(self.x, self.scaled, name="Scaled", pen=pen, symbol="o", symbolSize=30, symbolBrush=('b'))
    self.data_line_l = self.graphWidget.plot(self.x, self.linear, name="Linear", pen=pen, symbol="o", symbolSize=30, symbolBrush=('g'))
    self.data_line_y = self.graphWidget.plot(self.x, self.y, name="Combined", pen=pen, symbol="o", symbolSize=30, symbolBrush=('r'))
    self.data_line_sw = self.graphWidget.plot([self.cfg.SWITCH_LVL_IDX], [self.y[self.cfg.SWITCH_LVL_IDX]], name="SW_PT", pen=pen, symbol="o", symbolSize=40, symbolBrush=('yellow'))
    styles = {'color':'r', 'font-size':'20px'}
    self.graphWidget.setLabel('left', 'BigBlind', **styles)
    self.graphWidget.setLabel('bottom', 'Level', **styles)
    self.graphWidget.addLegend()
    self.graphWidget.setMouseEnabled(False,False)
    self.graphWidget.showGrid(x=True, y=True)
    self.graphWidget.setBackground('w')

    # Layout assignments
    GLayout = QGridLayout()
    for sid, slider in enumerate(self.sliders.values()):
      GLayout.addWidget(slider, sid, 0, 1, 3)

    ButtonLayout = QHBoxLayout()
    ButtonLayout.addWidget(self.buttons["apply"])
    ButtonLayout.addWidget(self.buttons["apply_and_close"])

    VVLayout = QVBoxLayout()
    VVLayout.addWidget(self.cfg_window)
    VVLayout.addWidget(self.buttons["load_config"])
    VVLayout.addWidget(self.buttons["save_config"])

    HHLayout = QHBoxLayout()
    HHLayout.addLayout(GLayout)
    HHLayout.addLayout(VVLayout)

    VLayout = QVBoxLayout()
    VLayout.addLayout(HHLayout)
    VLayout.addLayout(ButtonLayout)

    grand_layout.addWidget(self.graphWidget)
    grand_layout.addLayout(VLayout)

    # Events + Actions
    self.resizeEvent = self.customResizeEvent
    self.sliders["scale"].slider.valueChanged[int].connect(self.changeScalingFactorValue)
    self.sliders["switch_lvl_idx"].slider.valueChanged[int].connect(self.changeSwitchingPointValue)
    self.sliders["lin_bb_step"].slider.valueChanged[int].connect(self.changeLinearBBStepValue)
    self.sliders["lvl_n"].slider.valueChanged[int].connect(self.changeLvlNumberValue)
    self.buttons["load_config"].clicked.connect(self.load_config_from_a_file)
    self.buttons["save_config"].clicked.connect(self.save_config_to_a_file)
    self.cfg_window.pb_apply.clicked.connect(self.apply_cfg_window)
    self.cfg_window.pb_refresh.clicked.connect(self.refresh_cfg_window)

  def load_config_from_a_file(self):
    json_path = Path(QFileDialog(self).getOpenFileName(filter="File (*.json)")[0])
    config = load_config_from_json(json_path)
    if config: # if it's not False, then update
      self.update_config(config)

  def save_config_to_a_file(self):
    path = Path( QFileDialog(self).getSaveFileName(self, filter="*.json")[0])
    dict_config = dump_config_to_json(self.cfg)
    with open(path, "w") as f:
      json.dump(dict_config, f)

  def customResizeEvent(self, event):
    # # Calculate font sizes based on window width and height
    width = self.width()
    if width >= self.maximumWidth():
      width = self.maximumWidth()
    ButtonFontSize = int(width / 60)
    ButtonLCFontSize = int(width / 90)
    font = self.buttons["apply_and_close"].font()
    font.setPointSize(ButtonFontSize)
    self.buttons["apply_and_close"].setFont(font)
    self.buttons["apply"].setFont(font)
    font.setPointSize(ButtonLCFontSize)
    self.buttons["load_config"].setFont(font)
    self.buttons["save_config"].setFont(font)
    sliderFontSize = int(width/120)
    font = self.sliders["scale"].label.font()
    font.setPointSize(sliderFontSize)
    for slider in self.sliders.values():
      slider.label.setFont(font)

  def updatePlots(self):
    self.data_line_y.setData(self.x, self.y)
    self.data_line_s.setData(self.x, self.scaled)
    self.data_line_l.setData(self.x, self.linear)
    self.data_line_sw.setData([self.cfg.SWITCH_LVL_IDX], [self.y[self.cfg.SWITCH_LVL_IDX]])

  def changeScalingFactorValue(self, a0):
    self.cfg.SCALING_FACTOR = a0 / self.scale_factor_scale
    self.calculate_plots()
    self.sliders["scale"].updateText(self.cfg.SCALING_FACTOR)
    self.updatePlots()
    self.cfg_window.update_config(self.cfg)

  def changeSwitchingPointValue(self, a0):
    self.cfg.SWITCH_LVL_IDX = int(a0)
    self.calculate_plots()
    self.sliders["switch_lvl_idx"].updateText(a0)
    self.updatePlots()
    self.cfg_window.update_config(self.cfg)

  def changeLinearBBStepValue(self, a0):
    self.cfg.LINEAR_BB_STEP = int(a0) * self.lin_bb_step_scale
    self.calculate_plots()
    self.sliders["lin_bb_step"].updateText(self.cfg.LINEAR_BB_STEP)
    self.updatePlots()
    self.cfg_window.update_config(self.cfg)

  def changeLvlNumberValue(self, a0):
    self.cfg.LVL_N = int(a0)
    self.x = list(range(0, self.cfg.LVL_N, 1))
    if self.cfg.SWITCH_LVL_IDX > len(self.x):
      self.cfg.SWITCH_LVL_IDX = self.x[-1]
      self.sliders["switch_lvl_idx"].updateText(self.cfg.SWITCH_LVL_IDX)
    self.sliders["switch_lvl_idx"].slider.setMaximum(self.cfg.LVL_N-1)
    self.calculate_plots()
    self.sliders["lvl_n"].updateText(self.cfg.LVL_N)
    self.updatePlots()
    self.cfg_window.update_config(self.cfg)

  def calculate_plots(self):
    lvl_n = self.cfg.LVL_N
    switch_lvl_idx = self.cfg.SWITCH_LVL_IDX
    scale_f = self.cfg.SCALING_FACTOR
    lin_bb_step = self.cfg.LINEAR_BB_STEP
    generator1 = gen_func(lin_bb_step, lvl_n, None, scale_linear, bb_inc=self.cfg.MIN_LINEAR_BB_STEP)
    linear = list(generator1)
    scale_start_val = get_scale_value_level_0(linear[switch_lvl_idx], switch_lvl_idx, 1/scale_f)
    generator2 = gen_func(linear[switch_lvl_idx], lvl_n, scale_f, scale_by_factor, bb_inc=self.cfg.MIN_LINEAR_BB_STEP)
    generator3 = gen_func(scale_start_val, lvl_n, scale_f, scale_by_factor, bb_inc=self.cfg.MIN_LINEAR_BB_STEP)
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
    self.cfg.BIG_BLIND_VALUES = [int(x) for x in y]

  def update_config(self, config: PokerConfig):
    self.cfg = config
    self.x = list(range(config.LVL_N))
    self.calculate_plots()

    self.cfg_window.update_config(config)

    self.scale_factor_scale = int(1 / self.cfg.SCALE_FACTOR_STEP)
    lowest_scaling_factor = int(self.cfg.MIN_SCALE_FACTOR * self.scale_factor_scale)
    max_scaling_factor = int(self.cfg.MAX_SCALE_FACTOR * self.scale_factor_scale)

    self.sliders["scale"].slider.setMaximum(int(max_scaling_factor))
    self.sliders["scale"].slider.setMinimum(int(lowest_scaling_factor))
    self.sliders["scale"].slider.setValue(int(self.cfg.SCALING_FACTOR * self.scale_factor_scale))
    self.sliders["scale"].updateText(str(self.cfg.SCALING_FACTOR))

    self.sliders["switch_lvl_idx"].slider.setMaximum(self.cfg.LVL_N)
    self.sliders["switch_lvl_idx"].slider.setMinimum(1)
    self.sliders["switch_lvl_idx"].slider.setValue(int(self.cfg.SWITCH_LVL_IDX))
    self.sliders["switch_lvl_idx"].updateText(str(self.cfg.SWITCH_LVL_IDX))

    self.lin_bb_step_scale = self.cfg.MIN_LINEAR_BB_STEP
    min_start_val = self.lin_bb_step_scale
    max_start_val = self.cfg.MAX_LINEAR_BB_STEP
    self.sliders["lin_bb_step"].slider.setMaximum(max_start_val//self.lin_bb_step_scale)
    self.sliders["lin_bb_step"].slider.setMinimum(min_start_val//self.lin_bb_step_scale)
    self.sliders["lin_bb_step"].slider.setValue(self.cfg.LINEAR_BB_STEP//self.lin_bb_step_scale)
    self.sliders["lin_bb_step"].updateText(str(self.cfg.LINEAR_BB_STEP))

    self.sliders["lvl_n"].slider.setMaximum(2*self.cfg.LVL_N)
    self.sliders["lvl_n"].slider.setMinimum(2)
    self.sliders["lvl_n"].slider.setValue(self.cfg.LVL_N)
    self.sliders["lvl_n"].updateText(str(self.cfg.LVL_N))

    self.updatePlots()

  def apply_cfg_window(self):
    print("X")
    self.update_config(self.cfg_window.get_config())

  def refresh_cfg_window(self):
    self.cfg_window.update_config(self.cfg)
