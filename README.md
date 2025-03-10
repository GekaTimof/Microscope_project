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




#Старые варианты установки sudo


# разрешить запуск без пароля
sudo visudo
evgeniy ALL=(ALL) NOPASSWD: ~/Documents/Microscope_project/Spectrometer/Visualization/main.py


# установка библиотек и запуск
python3 -m pip install X
python3 main.py



Запуск скрипта из под sudo

sudo chown root:root main.py  # Сделать владельцем root
sudo chmod 4755 main.py      # Установить setuid-бит

Опционально:

Чтобы никто не мог изменять скрипт:
sudo chmod 755 connection.py
sudo chattr +i connection.py  # Сделать неизменяемым

Чтобы разрешить изменения обратно:
sudo chattr -i connection.py
