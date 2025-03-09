Запуск скрипта из под sudo

sudo chown root:root connection.py  # Сделать владельцем root
sudo chmod 4755 connection.py      # Установить setuid-бит

Опционально:

Чтобы никто не мог изменять скрипт:
sudo chmod 755 connection.py
sudo chattr +i connection.py  # Сделать неизменяемым

Чтобы разрешить изменения обратно:
sudo chattr -i connection.py
