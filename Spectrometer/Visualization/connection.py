import os
import sys
import pexpect
import numpy as np
import time
# from Visualization import get_data_from_massage
lines_num_X = 2048
lines_num_Y = 1044

def get_data_from_massage(massage: str):
    data = np.zeros(lines_num_X)
    i = 0
    for line in massage.splitlines():
        if line.strip():
            data[i] = line.split()[-1]
            i += 1
    return data

# Полный путь к исполняемому файлу
working_directory = os.path.abspath("../Get_data")
# Название скрипта для получения данных
get_data_pass = os.path.join(working_directory, "OptoskyDemo")

# Запускаем процесс
child = pexpect.spawn(f'{get_data_pass}', cwd=working_directory, encoding="utf-8", timeout=10)


# try to start script (this script tp get data from spectrometer)
try:
    # Читаем вывод до появления "Enter :"
    child.expect("Enter :", timeout=5)
    print("Скрипт запущен")
except:
    print("Нет ответа от спектрометра, проверьте подключение")
    sys.exit(1)

# try to connect to spectrometer
try:
    # Отправляем команду (например, "0" для подключения к спектрометру)
    child.sendline("0")
    child.expect("success!", timeout=5)
    print("Подключене прошло успешно")
except:
    print("Не удолось подключиться к спектрометру, проверьте подключен ли спектрометр и наличие прав (sudo)")
    sys.exit(1)

# Читаем ответ
child.expect("Enter :")

print("Пустой запуск")
child.sendline("23")
child.expect("Enter :")

print("Настоящий запуск")
child.sendline("23")
child.expect("Wavelength")

child.expect("====")
data = get_data_from_massage(child.before)
print(data)
child.expect("Enter :")

# Завершаем программу (отправляем команду выхода "100")
print("Завершаем сеанс")
child.sendline("100")
child.close()
