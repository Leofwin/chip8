import sys
import threading
import time
from contextlib import contextmanager

import PyQt5.QtWidgets
from PyQt5.QtGui import QKeySequence, QPainter, QColor, QPen
from PyQt5.QtMultimedia import QSound
from PyQt5.QtWidgets import QMainWindow

import emulator
import settings


@contextmanager
def painter(device):
    painter = QPainter()
    painter.begin(device)
    yield painter
    painter.end()


def start_thread(method):
    th = threading.Thread(target=method)
    th.setDaemon(True)
    th.start()


class EmulatorWindow(QMainWindow):
    def __init__(self, parent_emulator, parent=None):
        super().__init__(parent)

        self.setWindowTitle(settings.window_title + " | Delay mode: activated")
        self.emulator = parent_emulator
        self.generate_menu()

        self.beep = QSound(settings.sounds_folder + settings.beep)
        self.screen = Screen(parent_emulator.screen, self)
        self.is_pause_thread = False
        self.is_sound_timer_running = False
        self.is_delay_timer_running = False
        self.is_need_to_make_delay = True

        self.setCentralWidget(self.screen)
        start_thread(self.start_emulator_work)

    def change_delay_mode(self):
        self.is_need_to_make_delay = not self.is_need_to_make_delay
        mode = "activated" if self.is_need_to_make_delay else "deactivated"
        self.setWindowTitle(settings.window_title + " | Delay mode: {0}".format(mode))

    def start_delay_timer_work(self):
        self.is_delay_timer_running = True
        while not self.is_pause_thread and self.emulator.delay_timer > 0:
            self.emulator.delay_timer -= 1
            time.sleep(1 / settings.timer_frequency)
        self.is_delay_timer_running = False

    def start_sound_timer_work(self):
        self.is_sound_timer_running = True
        while not self.is_pause_thread and self.emulator.sound_timer > 0:
            self.emulator.sound_timer -= 1
            time.sleep(1 / settings.timer_frequency)
        self.is_sound_timer_running = False

    def start_emulator_work(self):
        while not self.is_pause_thread:
            self.emulator.make_tact()
            if self.emulator.is_need_to_draw:
                if self.is_need_to_make_delay:
                    time.sleep(0.001)
                self.screen.update()
            if self.emulator.delay_timer > 0 and not self.is_delay_timer_running:
                start_thread(self.start_delay_timer_work)
            if self.emulator.sound_timer > 0 and not self.is_sound_timer_running:
                start_thread(self.start_sound_timer_work)

    def generate_menu(self):
        menubar = self.menuBar()
        menu_file = menubar.addMenu("&File")
        menu_game = menubar.addMenu("&Game")
        menu_help = menubar.addMenu("&Help")

        open_act = PyQt5.QtWidgets.QAction("Open", self)
        open_act.setShortcut(QKeySequence("Ctrl+O"))
        open_act.triggered.connect(self.load_file)

        about_act = PyQt5.QtWidgets.QAction("About", self)
        about_act.setShortcut(QKeySequence("Ctrl+H"))
        about_act.triggered.connect(self.show_help)

        quit_act = PyQt5.QtWidgets.QAction("Quit", self)
        quit_act.setShortcut(QKeySequence("Ctrl+Q"))
        quit_act.triggered.connect(self.close)

        change_delay_mode_act = PyQt5.QtWidgets.QAction("Change delay mode", self)
        change_delay_mode_act.setShortcut(QKeySequence("Ctrl+D"))
        change_delay_mode_act.triggered.connect(self.change_delay_mode)

        menu_file.addAction(open_act)
        menu_file.addAction(quit_act)
        menu_help.addAction(about_act)
        menu_game.addAction(change_delay_mode_act)

    def keyPressEvent(self, e):
        key_code = e.key()
        if key_code in settings.key_codes.keys():
            self.emulator.pressed_button = settings.key_codes[key_code]

    def keyReleaseEvent(self, e):
        key_code = e.key()
        if key_code in settings.key_codes.keys() and \
                        self.emulator.pressed_button == settings.key_codes[key_code]:
            self.emulator.pressed_button = None

    def load_file(self):
        name = PyQt5.QtWidgets.QFileDialog.getOpenFileName(
            self, 'Загрузить файл', settings.games_folder,
            "All Files (*)")
        if name == ('', ''):
            return

        try:
            self.is_pause_thread = True
            time.sleep(0.1)
            self.emulator.reset()
            self.emulator.load_file_in_memory(name[0])
            self.screen.update()
            self.is_pause_thread = False
            start_thread(self.start_emulator_work)
        except Exception as e:
            PyQt5.QtWidgets.QMessageBox.critical(
                self,
                "Не удалось загрузить файл",
                "Не удалось загрузить файл. "
                "Проверьте существование файла или"
                "обратитесь к разработчику проекта",
                PyQt5.QtWidgets.QMessageBox.Close)

    def show_help(self):
        PyQt5.QtWidgets.QMessageBox.information(
            self, "About", settings.help_msg,
            PyQt5.QtWidgets.QMessageBox.Ok
        )


class Screen(PyQt5.QtWidgets.QFrame):
    def __init__(self, screen_data, parent=None):
        super().__init__(parent)

        width = screen_data.width * settings.pixel_size
        height = screen_data.height * settings.pixel_size
        self.setFixedSize(width, height)
        self.screen_data = screen_data
        self.update()

    def draw_pixels(self, qp):
        qp.setPen(QPen(0))
        active_color = QColor(settings.active_color)
        background_color = QColor(settings.background_color)
        for y in range(self.screen_data.height):
            for x in range(self.screen_data.width):
                value = self.screen_data.get_value(x, y)
                color = active_color if value else background_color
                qp.setBrush(QColor(color))
                qp.drawRect(
                    x * settings.pixel_size,
                    y * settings.pixel_size,
                    settings.pixel_size,
                    settings.pixel_size
                )

    def paintEvent(self, e):
        with painter(self) as qp:
            self.draw_pixels(qp)


def print_help():
    print("This program is a CHIP-8 emulator (v. 0.9).\n"
          "To run emulator: write path to file as first argument.\n"
          "Example: python gui.py /games/MAZE\n"
          "Created by Leofwin <leofwin98@yandex.ru>")


if __name__ == "__main__":
    game = settings.games_folder + "MAZE"
    if len(sys.argv) >= 2:
        if sys.argv[1] == "--help" or sys.argv[1] == "-h":
            print_help()
            sys.exit(0)
        game = sys.argv[1]

    app = PyQt5.QtWidgets.QApplication(sys.argv)
    chip_emulator = emulator.Emulator()
    chip_emulator.load_file_in_memory(game)

    window = EmulatorWindow(chip_emulator)
    window.show()
    sys.exit(app.exec_())
