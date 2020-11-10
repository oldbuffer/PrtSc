import win32ui, win32gui, win32con, win32api
from datetime import datetime
import time
from pynput.keyboard import Listener, Key
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QGridLayout, QWidget, QCheckBox, QSystemTrayIcon, \
    QSpacerItem, QSizePolicy, QMenu, QAction, qApp, QFileDialog, QPushButton, QTextEdit
from PyQt5.QtCore import QSize, QThread
from PyQt5 import QtGui
global folder_path

class ScreeenShotThread(QThread):
    def __init__(self, parent=None):
        super(ScreeenShotThread,self).__init__(parent)
        self.value=0

    def run(self):
        def on_press(key):
            if key == Key.print_screen:
                make_scrshot()
                time.sleep(0.3)

        with Listener(on_press=on_press) as listener:
            self.listener = listener
            listener.join()

class MainWindow(QMainWindow):
    """
        Объявление чекбокса и иконки системного трея.
        Инициализироваться будут в конструкторе.
    """
    check_box = None
    tray_icon = None

    def chooseFolder(self):
        global folder_path
        folder_path = QFileDialog.getExistingDirectory(None, 'Select a folder:', 'C:\\', QFileDialog.ShowDirsOnly)
        self.textedit.setText(folder_path)

    # Переопределяем конструктор класса
    def __init__(self):
        # Обязательно нужно вызвать метод супер класса
        QMainWindow.__init__(self)

        self.setMinimumSize(QSize(200, 100))  # Устанавливаем размеры
        self.setWindowTitle("Aperture Screener")  # Устанавливаем заголовок окна
        self.setWindowIcon(QtGui.QIcon("aperture_icon.ico"))
        central_widget = QWidget(self)  # Создаём центральный виджет
        self.setCentralWidget(central_widget)  # Устанавливаем центральный виджет

        grid_layout = QGridLayout(self)  # Создаём QGridLayout
        central_widget.setLayout(grid_layout)  # Устанавливаем данное размещение в центральный виджет
        grid_layout.addWidget(QLabel("Для съемки скриншота нажмите клавишу 'Prt Sc'", self), 0, 0)

        # Добавляем чекбокс, от которого будет зависеть поведение программы при закрытии окна
        self.check_box = QCheckBox('Сворачивать в трей')
        grid_layout.addWidget(self.check_box, 1, 0)
        grid_layout.addWidget(QLabel("Для выбора папки сохранения нажмите 'Browse'", self), 2, 0)
        self.button = QPushButton("Browse", self)
        self.button.setGeometry(210, 70, 50, 25)

        self.button.clicked.connect(self.chooseFolder)
        self.textedit = QTextEdit(self)
        self.textedit.setGeometry(10, 70, 190, 25)
        grid_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding), 3, 0)
        self.ScreeenShotThread_instance = ScreeenShotThread()
        self.ScreeenShotThread_instance.start()

        # Инициализируем QSystemTrayIcon
        self.tray_icon = QSystemTrayIcon(QtGui.QIcon("aperture_icon.ico"))

        '''
            Объявим и добавим действия для работы с иконкой системного трея
            show - показать окно
            hide - скрыть окно
            exit - выход из программы
        '''
        show_action = QAction("Show", self)
        quit_action = QAction("Exit", self)
        hide_action = QAction("Hide", self)
        show_action.triggered.connect(self.show)
        hide_action.triggered.connect(self.hide)
        quit_action.triggered.connect(qApp.quit)
        tray_menu = QMenu()
        tray_menu.addAction(show_action)
        tray_menu.addAction(hide_action)
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    # Переопределение метода closeEvent, для перехвата события закрытия окна
    # Окно будет закрываться только в том случае, если нет галочки в чекбоксе
    def closeEvent(self, event):
        if self.check_box.isChecked():
            event.ignore()
            self.hide()
            self.tray_icon.showMessage(
                "Aperture Screener",
                "Приложение свернуто в трей",
                QSystemTrayIcon.Information,
                3000
            )


def make_scrshot():
    hwnd = win32gui.GetDesktopWindow()
    width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
    height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
    x = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
    y = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)

    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()

    saveBitMap = win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
    saveDC.SelectObject(saveBitMap)
    saveDC.BitBlt((0, 0), (width, height), mfcDC, (x, y), win32con.SRCCOPY)
    dateTimeObj = datetime.now()
    date = dateTimeObj.strftime("%d_%b_%Y_%H_%M_%S_%f")

    # Можно сохранить полученный битмап в BPM огромных размеров
    def get_path():
        try:
            if folder_path is not None:
                return str(folder_path + '/' + date + '.bmp')
            elif folder_path==False:
                return str(date + '.bmp')
        except NameError:
                return str(date + '.bmp')

    saveBitMap.SaveBitmapFile(saveDC, get_path())

def main():

    import sys
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
