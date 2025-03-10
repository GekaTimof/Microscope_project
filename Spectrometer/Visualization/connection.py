import os
import sys
import pexpect
import numpy as np

# Проверка прав доступа
if os.geteuid() != 0:
    os.execvp('sudo', ['sudo', sys.executable] + sys.argv)

working_directory = os.path.abspath("../Get_data")
get_data_pass = os.path.join(working_directory, "OptoskyDemo")

# Запуск процесса с помощью pexpect
child = pexpect.spawn(f'{get_data_pass}', cwd=working_directory, encoding="utf-8", timeout=10)
# child.logfile = sys.stdout

try:
    child.expect("Enter :", timeout=5)
    print("Скрипт запущен")
except pexpect.TIMEOUT:
    print("Нет ответа от спектрометра, проверьте подключение")
    sys.exit(1)

# Открываем спектрометр
child.sendline("0")
child.expect("success!")
print("Подключение прошло успешно")
child.expect("Enter :")

# Запуск синхронного спектрального снятия
child.sendline("31")
child.expect("input")
child.sendline("10")  # Вводим значение интегрального времени
child.expect("number")  # Ожидаем вывода "Pixel number :"

# Ожидание окончания процесса снятия спектра
child.expect("Count")
child.expect("==========")

# # Создание массива для хранения данных
# data = np.zeros(1024)
#
# # Чтение данных спектра
# i = 0
# while True:
#     line = child.readline().strip()
#     if not line:
#         break
#     try:
#         # Извлекаем данные по числовому значению пикселя
#         data[i] = float(line.split()[-1])
#         i += 1
#     except ValueError:
#         pass


print("Измеренные данные:", child.before)

# Закрытие спектрометра
child.sendline("100")
child.close()
print("Сеанс завершен")
