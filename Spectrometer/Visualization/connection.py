import os
import pexpect

# Полный путь к исполняемому файлу
working_directory = os.path.abspath("../Get_data")
# Название скрипта для получения данных
get_data_pass = os.path.join(working_directory, "OptoskyDemo")

# Запускаем процесс
child = pexpect.spawn(get_data_pass, cwd=working_directory, encoding="utf-8", timeout=10)

# Читаем вывод до появления "Enter :"
child.expect("Enter :")
print(child.before)  # Вывод меню

# Отправляем команду (например, "2" для API Get vendor)
child.sendline("2")

# Читаем ответ
child.expect("Enter :")
print(child.before)  # Вывод после команды

# Завершаем программу (отправляем команду выхода "100")
child.sendline("100")
child.close()
