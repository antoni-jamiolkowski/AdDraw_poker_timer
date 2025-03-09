import datetime
# to close MainWindow/QApp with Ctrl+C
import signal
import time
from pathlib import Path

from typing import Optional

from PyQt5.QtCore import QSize, QTimer
from PyQt5.QtWidgets import QApplication, QGridLayout, QMainWindow, QWidget, QRadioButton

from settings_window import SettingsWindow
from utils import *

signal.signal(signal.SIGINT, signal.SIG_DFL)

class PokerTimer():
  def __init__(self,
               geometry : QSize = WindowGeometry.FHD.value,
               max_geometry : QSize = WindowGeometry.UHD.value,
               time_step_ms : int = 10,
               config_path: Optional[Path] = None
               ):
    config_path = Path("configs/my_config.json") if config_path is None else config_path
    if not config_path.exists():
      raise ValueError(f"Config file {config_path.absolute()} does not exist!")

    self.cfg = load_config_from_json(config_path)

    self.settings_window = SettingsWindow(self.cfg)
    self.main_window = QMainWindow()
    self.current_state = PokerGameState(self.cfg)

    # Time counters
    self.sec_cnt = 0
    self.time_step_ms = time_step_ms
    self.total_time = time.time()
    self.break_time = 0

    # Constraint the MV, setup and show
    self.main_window.setMaximumHeight(max_geometry.height())
    self.main_window.setMaximumWidth(max_geometry.width())
    self.setup_window(geometry)
    self.main_window.show()

  def setup_window(self,
                   geometry : QSize = WindowGeometry.FHD.value):
    # QT
    self.main_window.setObjectName("MainWindow")
    self.main_window.setWindowTitle("Poker Timer")
    self.main_window.resize(geometry)
    self.central_widget = QWidget()
    self.set_background_img()
    self.main_layout = QGridLayout(self.central_widget)
    self.main_window.setCentralWidget(self.central_widget)

    # QFontDataBase
    self.qfontdb = setupQFontDataBase()
    #QTWidgets
    # Timer
    self.update_timer = QTimer(self.main_layout)
    self.update_timer.start(100)
    self.round_timer = QTimer(self.main_layout)
    self.total_timer = QTimer(self.main_layout)
    self.total_timer.start(1000) # each second update
    self.break_timer = QTimer(self.main_layout)

    self.mv_display = MainWindowDisplay(self.central_widget, self.current_state)
    self.mv_controls = MainWindowControls(self.central_widget)

    self.check = QRadioButton(self.central_widget)
    self.check.clicked.connect(self.hide_show_ctrls)
    self.check.setText("Hide")
    self.check.setStyleSheet("color: white")

    # Add Widgets to main window
    self.main_layout.addWidget(self.mv_controls, 4, 0, 1, 5)
    self.main_layout.addWidget(self.mv_display, 0, 0, 4, 5)
    self.main_layout.addWidget(self.check, 0,0,1,1)

    self.main_layout.setVerticalSpacing(0)

    # Connect widgets to actions
    mv_control_clicks = {"Settings": self.showSettingsWindow,
                         "Reset": self.reset_button_action,
                         "PrevLvl": self.prev_level_button_action,
                         "NextLvl": self.next_level_button_action,
                         "StartStop": self.start_stop_round_timer}
    self.mv_controls.connect_clicks(mv_control_clicks)

    self.round_timer.timeout.connect(self.update_stats_every_sec)
    self.update_timer.timeout.connect(self.update_mv_display_texts)
    self.total_timer.timeout.connect(self.update_total_time)
    self.break_timer.timeout.connect(self.update_break_time)

    # Initialize texts
    self.update_mv_display_texts()

    # Resize Event
    self.main_window.resizeEvent = self.customResizeEvent

  # Event methods
  def customResizeEvent(self, event):
    # Calculate font sizes based on window width and height
    width = self.main_window.width()
    if width >= self.main_window.maximumWidth():
      width = self.main_window.maximumWidth()

    ButtonFontSize = int(width/ 30)
    class DisplayFontSizes:
      ROUND_TIMER = int(width / 7)
      BLINDS = int(width / 15)
      NEXT_BLINDS = int(width / 25)
      LEVEL = int(width / 30)
      TOTAL_TIMER = int(width / 30)
      BREAK_TIMER = int(width / 18)

    self.mv_display.update_fonts(DisplayFontSizes.__dict__)
    self.mv_controls.updateFonts(ButtonFontSize)

  def set_background_img(self, path:Path = Path("images/bg.jpg")):
    self.main_window.setStyleSheet("#MainWindow { "
                                                f" border-image: url({path.absolute()}) 0 0 0 0 stretch stretch;"
                                                "}")

  def update_mv_display_texts(self):
    if self.current_state.current_level >= len(self.cfg.BIG_BLIND_VALUES):
      self.current_state.current_level = len(self.cfg.BIG_BLIND_VALUES)-1
    self.mv_display.update_texts(self.sec_cnt)

  def showSettingsWindow(self):
    self.settings_window.show()

  # Timers
  def update_break_time(self):
    if self.break_time == 0:
      self.break_time = time.time()
    new_time = time.time()
    elapsed = round(new_time - self.break_time, 2)
    time_pprint =  str(datetime.datetime.strftime(datetime.datetime.utcfromtimestamp(elapsed),'%M:%S'))
    self.mv_display.labels["break_timer"].setText(f"BREAK {time_pprint}")

  def update_total_time(self):
    new_time = time.time()
    elapsed = round(new_time - self.total_time, 2)
    time_pprint =  str(datetime.datetime.strftime(datetime.datetime.utcfromtimestamp(elapsed),'%H:%M:%S'))
    self.mv_display.labels["total_timer"].setText(f"{time_pprint}")

  # method called by timer
  def update_stats_every_sec(self):
    self.sec_cnt += self.time_step_ms
    if self.sec_cnt >= 1000: # count to a second
      self.sec_cnt = 0
      self.current_state.counter_increment()

  def start_stop_round_timer(self):
    if self.round_timer.isActive():
      self.round_timer.stop()
      self.break_time = 0
      self.break_timer.start(1000)
      self.mv_controls.start_stop_set("stop")
    else:
      self.round_timer.start(self.time_step_ms)
      self.break_time = 0
      self.break_timer.stop()
      self.mv_controls.start_stop_set("start")
    self.mv_display.labels["break_timer"].setText(f"")

  # Actions
  def next_level_button_action(self):
    self.current_state.nxt_level()
    self.update_mv_display_texts()

  def prev_level_button_action(self):
    self.current_state.prev_level()
    self.update_mv_display_texts()

  def reset_button_action(self):
    self.current_state.reset_level()
    self.update_mv_display_texts()


  def hide_show_ctrls(self):
    if self.mv_controls.isHidden():
      self.mv_controls.setHidden(False)
    else:
      self.mv_controls.setHidden(True)

if __name__ == "__main__":
  import sys
  app = QApplication(sys.argv)
  import argparse as argp
  parser = argp.ArgumentParser()
  parser.add_argument("-g", "--geometry", default="VGA", choices=WindowGeometry._member_map_)
  parser.add_argument("-c", "--config", default=None, type=Path, help="Path to a .json file with PokerConfig")
  args = parser.parse_args()
  geometry = getattr(WindowGeometry, args.geometry)

  ptw = PokerTimer(geometry=geometry.value,
                         config_path=args.config)
  sys.exit(app.exec_())
