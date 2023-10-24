import json
from dataclasses import dataclass
from enum import Enum, unique
from pathlib import Path

from numpy import asarray
from PyQt5 import QtCore
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QFont, QFontDatabase, QMouseEvent
from PyQt5.QtWidgets import (QGridLayout, QHBoxLayout, QLabel, QMessageBox,
                             QPushButton, QSizePolicy, QWidget)


@unique
class WindowGeometry(Enum):
  UHD = QSize(3840, 2160)
  FHD = QSize(1920, 1080)
  SETTINGS = QSize(1440,760)
  VGA = QSize(640, 480)
  QVGA = QSize(320, 240)


@unique
class MonospacedFontFamilies(Enum):
  ORIGAMI_MOMMY = "ORIGAMI MOMMY"
  MONOFONTO = "Monofonto"
  SPACEMONO = "Monospace"
  NOTOMONO = "Noto Mono"
  TLWGMONO = "Tlwg Mono"
  FREEMONO = "FreeMono"
  GOMONO = "Go Mono"


@unique
class FontFamilies(Enum):
  SPACE_GROT_REG = "SpaceGrotesk"


class MyTime:
  def __init__(self, m:int, s:int):
    self.m = m
    self.s = s

  @classmethod
  def fromstr(cls, string:str):
    if ":" in string:
      x = string.split(":")
      m, s = int(x[0]), int(x[-1])
    else:
      m = int(string)
      s = 0
    return cls(m,s)

  def _list(self):
    return list((self.m, self.s))

  def _arr(self):
    return asarray([self.m, self.s])


@dataclass
class PokerConfig:
  NAME: str = "NULL"
  STARTING_CHIP_AMOUNT: int = -1
  CHIP_INCREMENT : int = -1 # Smallest difference between chips
  BIG_BLIND_VALUES : any = -1 # BB Values for every level of the game
  LEVEL_PERIOD : MyTime = MyTime(-1,-1)

Family =  MonospacedFontFamilies.MONOFONTO.value
Family2 = MonospacedFontFamilies.MONOFONTO.value
Family3 = FontFamilies.SPACE_GROT_REG.value


class PokerGameState:
  def __init__(self,
               config: PokerConfig
               ):
    self.current_level = 1
    self.update_config(config)

  def update_config(self, config: PokerConfig, update_counters: bool = True):
    self.config = config
    assert(isinstance(config.LEVEL_PERIOD, MyTime))
    assert(isinstance(config.BIG_BLIND_VALUES, list))

    if update_counters:
      self.reset_timer()

  def get_state(self):
    cur_bb = self.config.BIG_BLIND_VALUES[self.current_level-1]
    cur_sb = int(cur_bb / 2)
    if cur_sb % self.config.CHIP_INCREMENT != 0:
      raise ValueError(f"Small Blind cannot be smaller than chip increment sb: {cur_sb}, chip_inc: {self.config.CHIP_INCREMENT}")
    if (self.current_level != len(self.config.BIG_BLIND_VALUES)-1):
      nxt_bb = self.config.BIG_BLIND_VALUES[self.current_level]
      nxt_sb = int(nxt_bb / 2)
    else:
      nxt_bb = "N/A"
      nxt_sb = "N/A"
    return [self.current_level,
            self.minute, self.second,
            cur_bb, cur_sb,
            nxt_bb, nxt_sb]

  def counter_increment(self):
    if self.minute == 0 and self.second == 0:
      self.current_level += 1
      self.reset_timer()
      return
    if self.second == 0:
      self.minute -= 1
      self.second = 59
      return
    self.second -= 1

  def nxt_level(self):
    if self.current_level != len(self.config.BIG_BLIND_VALUES)-1:
      self.current_level += 1
    self.reset_timer()

  def prev_level(self):
    if self.current_level != 1:
      self.current_level -= 1
    self.reset_timer()

  def reset_level(self):
    self.current_level = 1
    self.reset_timer()

  def reset_timer(self):
    self.minute, self.second = self.config.LEVEL_PERIOD._list()

def setupQFontDataBase():
  qfont_db = QFontDatabase()
  qfont_db.addApplicationFont("./fonts/origami-mommy/origa___.ttf")
  qfont_db.addApplicationFont("./fonts/monofont/monofontorg.otf")
  qfont_db.addApplicationFont("./fonts/space-grotesk/static/SpaceGrotesk-Bold.ttf")
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


def get_std_size_policy(obj) -> QSizePolicy:
  sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
  sizePolicy.setHorizontalStretch(0)
  sizePolicy.setVerticalStretch(0)
  sizePolicy.setHeightForWidth(obj.sizePolicy().hasHeightForWidth())
  return sizePolicy


def get_fixed_size_policy(): #DUNNO IF THIS WORKS
  sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
  return sizePolicy


def load_config_from_json(path: Path) -> PokerConfig | bool:
  def dict_to_config(_dict: dict):
    _dict["LEVEL_PERIOD"] = MyTime(*_dict["LEVEL_PERIOD"])
    return PokerConfig(**_dict)
  if not path.exists() or path.is_dir():
    return False
  with open(path, "r") as f:
    config = json.load(f)
  return dict_to_config(config)


def dump_config_to_json(config: PokerConfig):
  cdict = config.__dict__
  cdict["LEVEL_PERIOD"] = cdict["LEVEL_PERIOD"]._list()
  return cdict


class MyLabel(QLabel):
  def __init__(self,
               name: str,
               init_text: str = "",
               font : QFont = MyFonts.Blinds,
               layout_dir: QtCore.Qt.AlignmentFlag = QtCore.Qt.AlignmentFlag.AlignCenter,
               autofillbg: bool = True,
               scaled_content: bool = True,
               line_width: int = 2,
               color : str = "white",
               bg_color: str = "rgba(40,40,40,70%)",
               border_color: str = "transparent",
               border_width: int = 5,
               padding: str = "0"):
    super().__init__()
    self.setFont(font)
    self.setLayoutDirection(QtCore.Qt.LeftToRight)
    self.setAutoFillBackground(autofillbg)
    self.setScaledContents(scaled_content)
    self.setAlignment(layout_dir)
    self.setObjectName(name)
    self.setText(init_text)
    self.setLineWidth(line_width)
    self.setStyleSheet(f"background-color: {bg_color};"
                       f"color: {color};"
                       f"border: {border_width}px solid {border_color};"
                       f"border-radius: 0;"
                       f"padding: {padding}px")


class MyPushButton(QPushButton):
  def __init__(self,
               name : str,
               text: str = "NULL",
               whats_this :str = "This is a button, DUH",
               font: QFont = MyFonts.PushButton,
               unclicked_style_sheet: str = "border-radius: 0; background-color: rgba(220, 220, 220, 95%); border: 2px solid black;"):
    super().__init__()
    self.setSizePolicy(get_std_size_policy(self))
    self.setFont(font)
    self.setWhatsThis(whats_this)
    self.setObjectName(name)
    self.setText(text)
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


class MainWindowControls(QWidget):
  def __init__(self, parent: QWidget):
    super().__init__(parent=parent)
    self.setObjectName("MainWindowCtrl")
    self.buttons = {}
    self.buttons["Settings"]  = MyPushButton("lc_pb", "Settings", whats_this="Click to load a config from a file")
    self.buttons["Reset"]     = MyPushButton("reset_pb", "Reset", whats_this="Resets the Level to 1 and timer to round period")
    self.buttons["PrevLvl"]   = MyPushButton("prev_lvl_pb", "◀", whats_this="Button that goes to Level-1, cannot go below 1")
    self.buttons["StartStop"] = MyPushButton("start_stop_pb", "⏯️", whats_this="Button that starts/stops the timer")
    self.buttons["NextLvl"]   = MyPushButton("next_lvl_pb", "▶", whats_this="Button that goes to Level+1")
    layout = QHBoxLayout(self)
    for button in self.buttons.values():
      layout.addWidget(button)
    self.setAutoFillBackground(True)
    self.setLayout(layout)
    self.setStyleSheet("background-color: transparent;") # to make the background not white

  def updateFonts(self, font_size: int):
    for name, button in self.buttons.items():
      font = button.font()
      font.setPointSize(font_size)
      if name == "StartStop":
        font.setPointSize(int(font_size * 1.3)) # increase since it's smaller for some reason than < >
      button.setFont(font)

  def connect_clicks(self, function_list: dict):
    for name, val in function_list.items():
      self.buttons[name].clicked.connect(val)

  def start_stop_set(self, state: str):
    if state == "stop":
      self.buttons["StartStop"].setStyleSheet("background-color: rgba(220,220,220,95%);"
                                               "border: 2px solid black;"
                                               "color: black;")
    elif (state =="start"):
      self.buttons["StartStop"].setStyleSheet("background-color: rgba(40,40,40,95%);"
                                              "border: 2px solid black;"
                                              "color: white;")



class MainWindowDisplay(QWidget):
  def __init__(self, parent: QWidget, current_state: PokerGameState) -> None:
    super().__init__(parent)
    self.current_state = current_state
    self.setObjectName("MainWindowDisplay")
    self.labels = {}
    self.labels["round_timer"] = MyLabel("RoundTimer",
                                          init_text="0:0",
                                          font=MyFonts.Timer)
    self.labels["break_timer"] = MyLabel("BreakTimer",
                                          init_text="",
                                          font=MyFonts.Timer,
                                          border_color="transparent",
                                          bg_color="transparent",
                                          layout_dir=QtCore.Qt.AlignmentFlag.AlignBottom | QtCore.Qt.AlignmentFlag.AlignHCenter)
    self.labels["total_timer"] = MyLabel("TotalTimer",
                                          init_text="0:00:00",
                                          font=MyFonts.Timer,
                                          border_color="transparent",
                                          bg_color="transparent",
                                          layout_dir=QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignHCenter)
    self.labels["level"] = MyLabel("Level",
                                    border_color="transparent",
                                    bg_color="transparent",
                                    layout_dir=QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignHCenter)

    self.labels["blinds"] = MyLabel("CurBlinds")
    self.labels["next_blinds"] = MyLabel("NxtBlinds",
                                          border_color="transparent",
                                          bg_color="transparent",
                                          layout_dir=QtCore.Qt.AlignmentFlag.AlignBottom | QtCore.Qt.AlignmentFlag.AlignHCenter)
    layout = QGridLayout(self)
    self.setLayout(layout)
    layout.addWidget(self.labels["round_timer"] , 0, 2, 4, 3)
    layout.addWidget(self.labels["break_timer"] , 3, 2, 1, 3)
    layout.addWidget(self.labels["total_timer"] , 0, 2, 1, 3)
    layout.addWidget(self.labels["blinds"]      , 0, 0, 4, 2)
    layout.addWidget(self.labels["level"]       , 0, 0, 1, 2)
    layout.addWidget(self.labels["next_blinds"] , 3, 0, 1, 2)

  def update_fonts(self, font_sizes: dict):
    for name, val in font_sizes.items():
      name = name.lower()
      if name in self.labels.keys():
        font = self.labels[name].font()
        font.setPointSize(val)
        self.labels[name].setFont(font)

  def update_texts(self, sec_cnt:int):
    def vanishing_comma(sec_cnt: int,
                        on_time: int = 100,
                        position: int = 300):
      if (sec_cnt > position) and (sec_cnt < (position + on_time)):
        return " "
      return ":"
    l, m, s, bb, sb, nbb, nsb = self.current_state.get_state()
    print_comma = vanishing_comma(sec_cnt)
    self.labels["round_timer"].setText(f"{m}{print_comma}{s:02d}")
    self.labels["blinds"].setText(f"{sb}/{bb}")
    self.labels["next_blinds"].setText(f"NEXT:{nsb}/{nbb}")
    self.labels["level"].setText(f"LEVEL {l:02d}")
