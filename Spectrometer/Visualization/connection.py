import os
import sys
import pexpect

# Полный путь к исполняемому файлу
working_directory = os.path.abspath("../Get_data")
# Название скрипта для получения данных
get_data_pass = os.path.join(working_directory, "OptoskyDemo")

# Запускаем процесс
child = pexpect.spawn(get_data_pass, cwd=working_directory, encoding="utf-8", timeout=10)

# try to start script (this script tp get data from spectrometer)
try:
    # Читаем вывод до появления "Enter :"
    child.expect("Enter :", timeout=5)
    print(child.before)  # Вывод меню
except:
    print("Нет ответа од спектрометра, проверьте подключение")
    sys.exit(1)

# try to connect to spectrometer
try:
    # Отправляем команду (например, "0" для подключения к спектрометру)
    child.sendline("0")
    child.expect("success!", timeout=5)
    print("Подключене прошло успешно")
except:
    print("Не удолось подключиться к спектрометру, проверьте ваши права (sudo)")
    sys.exit(1)

# Читаем ответ
child.expect("Enter :")
print(child.before)  # Вывод после команды

# Завершаем программу (отправляем команду выхода "100")
print("Завершаем сеанс")
child.sendline("100")
child.close()
