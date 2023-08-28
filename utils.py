from PyQt5 import QtCore
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QFont, QFontDatabase
from PyQt5.QtWidgets import QLabel, QPushButton, QSizePolicy, QGraphicsEffect


def setupQFontDataBase():
  qfont_db = QFontDatabase()
  qfont_db.addApplicationFont("./fonts/origami-mommy/origa___.ttf")
  qfont_db.addApplicationFont("./fonts/monofont/monofontorg.otf")
  return qfont_db


class WindowGeometry:
  UHD = QSize(3840, 2160)
  FHD = QSize(1920, 1080)
  VGA = QSize(640, 480)
  QVGA = QSize(320, 240)


class FontFamilies:
  ORIGAMI_MOMMY = "ORIGAMI MOMMY"
  MONOFONTO = "Monofonto"
  SPACEMONO = "Monospace"
  NOTOMONO = "Noto Mono"
  TLWGMONO = "Tlwg Mono"
  FREEMONO = "FreeMono"
  GOMONO = "Go Mono"

Family = FontFamilies.MONOFONTO
Family2 = FontFamilies.MONOFONTO
Family3 = FontFamilies.MONOFONTO

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
