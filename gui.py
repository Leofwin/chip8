import PyQt5.QtWidgets
from PyQt5.QtMultimedia import QSound
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import QBasicTimer
import settings
import emulator
import sys


class EmulatorWindow(PyQt5.QtWidgets.QMainWindow):
    def __init__(self, parent_emulator, parent=None):
        super().__init__(parent)

        self.setWindowTitle(settings.window_title)
        self.emulator = parent_emulator
        self.generate_menu()

        self.timer = QBasicTimer()
        self.timer.start(1, self)
        self.ticks = 0

        self.beep = QSound(settings.sounds_folder + settings.beep)

        self.screen = Screen(parent_emulator.screen, self)
        self.setCentralWidget(self.screen)

    def generate_menu(self):
        menubar = self.menuBar()
        menu_file = menubar.addMenu("&File")
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

        menu_file.addAction(open_act)
        menu_file.addAction(quit_act)
        menu_help.addAction(about_act)

    def timerEvent(self, e):
        if self.ticks % settings.frequency == 0:
            self.emulator.make_tact()
            self.screen.update_pixels()

        if self.ticks % settings.timer_frequency == 0:
            if self.emulator.sound_timer > 0:
                self.beep.play()

            self.emulator.degrease_timers_if_need()

        self.ticks = (self.ticks + 1) % max(settings.timer_frequency, settings.frequency)

    def keyPressEvent(self, e):
        key_code = e.key()
        if key_code in settings.key_codes.keys():
            self.emulator.pressed_button = settings.key_codes[key_code]

    def load_file(self):
        name = PyQt5.QtWidgets.QFileDialog.getOpenFileName(
            self, 'Загрузить файл', settings.games_folder,
            "All Files (*)")
        if name == ('', ''):
            return

        try:
            self.emulator.reset()
            self.emulator.load_file_in_memory(name[0])
            self.screen.update_pixels()
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

    def restart(self):
        pass


class Screen(PyQt5.QtWidgets.QFrame):
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


class Pixel(PyQt5.QtWidgets.QLabel):
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
    app = PyQt5.QtWidgets.QApplication(sys.argv)
    chip_emulator = emulator.Emulator()
    chip_emulator.load_file_in_memory(settings.games_folder + "BLITZ")

    window = EmulatorWindow(chip_emulator)
    window.show()
    sys.exit(app.exec_())
