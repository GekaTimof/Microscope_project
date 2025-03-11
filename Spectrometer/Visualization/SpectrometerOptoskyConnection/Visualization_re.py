import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
import pyqtgraph as pg
from PyQt5.QtCore import QTimer
from GetData import get_data_from_file

X_file_pass = "../test_data/X_data.txt"
Y_file_pass = "../test_data/Y_data.txt"

Fake_spreading_range = 300
lines_num = 1024

class FakeTimePlot(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Real-Time Plot")
        self.setGeometry(100, 100, 800, 600)

        # Основной виджет
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Макет
        layout = QVBoxLayout()
        self.central_widget.setLayout(layout)

        # График
        self.graphWidget = pg.PlotWidget()
        layout.addWidget(self.graphWidget)

        # Установка пределов осей
        self.graphWidget.setXRange(200, 1200)
        self.graphWidget.setYRange(100, 20000)

        # Данные для графика
        self.x = np.array(get_data_from_file(X_file_pass))
        self.y = np.array(get_data_from_file(Y_file_pass))

        # Линия на графике
        self.curve = self.graphWidget.plot(self.x, self.y, pen="y")

        # Таймер для обновления графика каждую секунду
        self.timer = QTimer()
        self.timer.setInterval(1000)  # 1000 мс = 1 секунда
        self.timer.timeout.connect(self.update_plot)
        self.timer.start()

    def update_plot(self):
        """Функция обновления графика"""
        # Генерация случайных изменений от -Fake_spreading_range до +Fake_spreading_range
        delta = np.random.choice([-1, 1], size=lines_num) * np.random.randint(1, Fake_spreading_range + 1, lines_num)
        self.y = np.clip(self.y + delta, 0, 20000)  # Ограничение значений Y

        self.curve.setData(self.x, self.y)  # Обновление данных графика

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FakeTimePlot()
    window.show()
    sys.exit(app.exec_())

