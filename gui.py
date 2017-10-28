from PyQt5.QtWidgets import QMainWindow, QAction, QApplication, QFrame, QLabel
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import QBasicTimer
import settings
import emulator
import sys


class EmulatorWindow(QMainWindow):
    def __init__(self, parent_emulator, parent=None):
        super().__init__(parent)

        self.setWindowTitle(settings.window_title)
        self.emulator = parent_emulator
        self.generate_menu()

        self.timer = QBasicTimer()
        self.timer.start(settings.frequency, self)

        self.screen = Screen(parent_emulator.screen, self)
        self.setCentralWidget(self.screen)

    def generate_menu(self):
        menubar = self.menuBar()
        menu_file = menubar.addMenu("&File")
        menu_help = menubar.addMenu("&Help")

        open = QAction("Open", self)
        open.setShortcut(QKeySequence("Ctrl+O"))
        open.triggered.connect(self.load_file)

        about = QAction("About", self)
        about.setShortcut(QKeySequence("Ctrl+H"))
        about.triggered.connect(self.show_help)

        menu_file.addAction(open)
        menu_help.addAction(about)

    def timerEvent(self, e):
        self.emulator.make_tact()
        self.screen.update_pixels()

    def load_file(self):
        pass

    def show_help(self):
        pass


class Screen(QFrame):
    def __init__(self, screen_data, parent=None):
        super().__init__(parent)

        width = screen_data.width * settings.pixel_size
        height = screen_data.height * settings.pixel_size
        self.setFixedSize(width, height)
        self.screen_data = screen_data
        self.points = []
        for i in range(self.screen_data.width * self.screen_data.height):
            self.points.append(None)
        self.create_pixels()

    def _get_index(self, x, y):
        return self.screen_data.width * y + x

    def create_pixels(self):
        for y in range(self.screen_data.height):
            for x in range(self.screen_data.width):
                index = self._get_index(x, y)
                value = self.screen_data.get_value(x, y)
                self.points[index] = Pixel(x, y, value, self)

    def update_pixels(self):
        for y in range(self.screen_data.height):
            for x in range(self.screen_data.width):
                index = self._get_index(x, y)
                value = self.screen_data.get_value(x, y)
                if self.points[index].value != value:
                    self.points[index].update_color(value)


class Pixel(QLabel):
    def __init__(self, x, y, value, parent=None):
        super().__init__(parent)
        self.value = None

        self.setGeometry(
            x * settings.pixel_size,
            y * settings.pixel_size,
            settings.pixel_size,
            settings.pixel_size
        )
        self.update_color(value)
        self.show()

    def update_color(self, value):
        if value != self.value:
            self.value = value
            color = settings.active_color if value else settings.background_color
            self.setStyleSheet("QLabel {background-color: %s;}" % color)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    chip_emulator = emulator.Emulator()
    chip_emulator.load_file_in_memory("MAZE")

    window = EmulatorWindow(chip_emulator)
    window.show()
    sys.exit(app.exec_())
