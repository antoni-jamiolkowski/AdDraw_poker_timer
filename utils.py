from enum import Enum, IntEnum, unique

from numpy import asarray
from PyQt5 import QtCore
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QFont, QFontDatabase
from PyQt5.QtWidgets import QLabel, QPushButton, QSizePolicy


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


Family = FontFamilies.MONOFONTO.value
Family2 = FontFamilies.MONOFONTO.value
Family3 = FontFamilies.MONOFONTO.value


class MyTime:
  def __init__(self, m, s):
    self.m = m
    self.s = s

  # @staticmethod
  def _list(self):
    return list((self.m, self.s))

  def _arr(self):
    return asarray([self.m, self.s])


class PokerParameters:
  def __init__(self,
               level_period: MyTime,
               level: int,
               bb_step: int):

    assert self.check_time(level_period), f"??? {level_period._list()}"
    assert level > 0
    assert bb_step > 1 and bb_step % 2 == 0

    self.level_period = level_period
    self.level = level
    self.bb_step = bb_step

  def check_time(self, new_time: MyTime):
    if (new_time._arr() > 59).any():
      raise ValueError(f"Both .m and .s have to be lower than 59")
    if (new_time._arr() < 0).any():
      raise ValueError(f"Both .m and .s have to be greater than 0")
    return True


class PokerStats:
  def __init__(self,
               config: PokerParameters
               ):
    self.update_config(config)

  def update_config(self, config: PokerParameters):
    self.config = config
    self.level = config.level
    self.minute = config.level_period.m
    self.second = config.level_period.s
    self.update_blinds()

  def update_blinds(self):
    self.big_blind = self.config.bb_step * self.level
    self.small_blind = int(self.big_blind / 2)
    self.nxt_big_blind = self.config.bb_step * (self.level+1)
    self.nxt_small_blind = int(self.nxt_big_blind / 2)

  def counter_increment(self):
    if self.minute == 0 and self.second == 0:
      self.level += 1
      self.minute, self.second = self.config.level_period
      return
    if self.second == 0:
      self.minute -= 1
      self.second = 59
      return
    self.second -= 1
    self.update_blinds()

  def nxt_level(self):
    self.level += 1
    self.minute = self.config.level_period.m
    self.second = self.config.level_period.s
    self.update_blinds()

  def prev_level(self):
    if self.level != 1:
      self.level -= 1
    self.minute = self.config.level_period.m
    self.second = self.config.level_period.s
    self.update_blinds()

  def _list(self):
    return (self.level, self.minute, self.second,
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
               font: QFont = MyFonts.PushButton,
               unclicked_style_sheet: str = "  background-color: rgba(220, 220, 220, 95%); border: 2px solid black;"):
    super().__init__()
    sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(0)
    sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
    self.setSizePolicy(sizePolicy)
    self.setFont(font)
    self.setObjectName(name)
    self.setStyleSheet("QPushButton {" f"{unclicked_style_sheet}" "}"
                        "QPushButton:pressed{"
                        "  background-color: rgba(40, 40, 40, 95%);"
                        "  border:2px solid black;"
                        "color : white"
                        "}"
                        )
