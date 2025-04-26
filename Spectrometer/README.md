# Запуск из под SUDO
## разрешить запуск без пароля
sudo visudo
evgeniy ALL=(ALL) NOPASSWD: ~/Documents/Microscope_project/Spectrometer/Visualization/main.py


## 1
Создаём файл 
nano run_with_sudo.sh
добавляем в него содержимое
#!/bin/bash
sudo /home/evgeniy/Documents/Microscope_project/Spectrometer/Visualization/.venv/bin/python /home/evgeniy/Documents/Microscope_project/Spectrometer/Visualization/main.py "$@"

## 2
Даём разрешения на запуск кода без sudo (через консоль)
sudo visudo
добавляем строчку
evgeniy ALL=(ALL) NOPASSWD: /home/evgeniy/Documents/Microscope_project/Spectrometer/Visualization/.venv/bin/python /home/evgeniy/Documents/Microscope_project/Spectrometer/Visualization/main.py

## 3
Запускаем приложение
./run_with_sudo.sh



# Установка нужных библиотек
pip install numpy pyqt5 pyqtgraph pexpect
