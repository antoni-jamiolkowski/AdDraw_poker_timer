from pathlib import Path

import pyqtgraph as pg
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import (QFileDialog, QGridLayout, QHBoxLayout, QLineEdit,
                             QVBoxLayout, QWidget, QTableWidget, QTableWidgetItem, QHeaderView)

from utils import *


class SettingsWindow(QWidget):
  def __init__(self, config: PokerConfig, bg_color: str = "rgb(120,120,120)"):
    super().__init__()
    self.resize(WindowGeometry.SETTINGS.value)
    self.setStyleSheet(f" background-color: {bg_color};")
    self.cfg = config
    if self.cfg.BIG_BLIND_VALUES == [] or self.cfg.BIG_BLIND_VALUES == -1: # if uninitialized
      raise ValueError("BIG_BLIND_VALUES are empty! calculating values from plots, dummy values")

    self.x = range(len(self.cfg.BIG_BLIND_VALUES))

    self.sizePolicy_Std = get_std_size_policy(self)
    grand_layout = QHBoxLayout(self)
    self.setLayout(grand_layout)

    # Buttons
    self.buttons = {}
    self.buttons["load_config"] = MyPushButton("config_load", text="Load Config", whats_this="Loads Config from file")

    # Config
    val = self.cfg.BIG_BLIND_VALUES
    tablewidget= QTableWidget()
    tablewidget.setSizePolicy(get_std_size_policy(tablewidget))
    tablewidget.setColumnCount(2)
    tablewidget.setRowCount(len(val))
    tablewidget.setAutoFillBackground(True)
    tablewidget.setAlternatingRowColors(True)
    tablewidget.setHorizontalHeaderItem(0, QTableWidgetItem("BIG BLIND"))
    tablewidget.setHorizontalHeaderItem(1, QTableWidgetItem("PERIOD"))
    tablewidget.setStyleSheet("text-align: center; color: black")
    for id, x in enumerate(val):
      tablewidget.setItem(id, 0,  QTableWidgetItem(str(self.cfg.BIG_BLIND_VALUES[id])))
      tablewidget.setItem(id, 1,  QTableWidgetItem(f"{self.cfg.LEVEL_PERIOD.m}:{self.cfg.LEVEL_PERIOD.s}"))

    tablewidget.horizontalHeader().setStretchLastSection(True)
    tablewidget.horizontalHeader().setSectionResizeMode(
        QHeaderView.Stretch)
    self.tablewidget = tablewidget


    # Graph
    self.graphWidget = pg.PlotWidget(self)
    self.graphWidget.setSizePolicy(self.sizePolicy_Std)

    pen = pg.mkPen(width=10, style=QtCore.Qt.DashDotDotLine)
    self.data_line_y = self.graphWidget.plot(self.x, self.cfg.BIG_BLIND_VALUES, name="X", pen=pen, symbol="o", symbolSize=30, symbolBrush=('r'))
    styles = {'color':'r', 'font-size':'20px'}
    self.graphWidget.setLabel('left', 'BigBlind', **styles)
    self.graphWidget.setLabel('bottom', 'Level', **styles)
    self.graphWidget.addLegend()
    self.graphWidget.setMouseEnabled(False,False)
    self.graphWidget.showGrid(x=True, y=True)
    self.graphWidget.setBackground('w')


    VLay = QVBoxLayout()
    VLay.addWidget(self.tablewidget)
    VLay.addWidget(self.buttons["load_config"])

    self.grand_lay_objs = [self.graphWidget,
                           VLay]

    for x in self.grand_lay_objs:
      if isinstance(x, QGridLayout | QHBoxLayout | QVBoxLayout):
        grand_layout.addLayout(x)
      else:
        grand_layout.addWidget(x)

    # Events + Actions
    self.resizeEvent = self.customResizeEvent
    self.buttons["load_config"].clicked.connect(self.load_config_from_a_file)

  def load_config_from_a_file(self):
    json_path = Path(QFileDialog(self, directory="configs").getOpenFileName(filter="File (*.json)")[0])
    config = load_config_from_json(json_path)
    if config:
      print(f"Valid config found at {json_path}!")
      for name, val in config.__dict__.items():
        setattr(self.cfg, name, val)
      print(self.cfg)
      self.update()

  def customResizeEvent(self, event) -> None:
    width = self.width()
    height = self.height()
    if width >= self.maximumWidth():
      width = self.maximumWidth()
    ButtonLCFontSize = int(width / 60)
    font = self.buttons["load_config"].font()
    font.setPointSize(ButtonLCFontSize)
    self.buttons["load_config"].setFont(font)

    from math import floor
    w = floor(width*0.45)
    self.graphWidget.setMinimumWidth(w)
    self.tablewidget.setMinimumHeight(int(height*0.6))
    font = self.tablewidget.font()
    ButtonLCFontSize = int(width / 80)
    font.setPointSize(ButtonLCFontSize)
    self.tablewidget.setFont(font)
    self.tablewidget.resizeRowsToContents()
    self.tablewidget.resizeColumnsToContents()
    self.tablewidget.horizontalHeader().setFont(font)
    self.tablewidget.verticalHeader().setFont(font)
    self.tablewidget.horizontalHeaderItem(0).setFont(font)
    self.tablewidget.horizontalHeaderItem(1).setFont(font)


  def update(self):
    self.x = range(len(self.cfg.BIG_BLIND_VALUES))
    self.data_line_y.setData(self.x, self.cfg.BIG_BLIND_VALUES)

    for x in range(self.tablewidget.rowCount()):
      self.tablewidget.removeRow(x)
    self.tablewidget.setRowCount(len(self.cfg.BIG_BLIND_VALUES))
    for id, x in enumerate(self.cfg.BIG_BLIND_VALUES):
      self.tablewidget.setItem(id, 0,  QTableWidgetItem(str(x)))
      self.tablewidget.setItem(id, 1,  QTableWidgetItem(f"{self.cfg.LEVEL_PERIOD.m}:{self.cfg.LEVEL_PERIOD.s}"))

