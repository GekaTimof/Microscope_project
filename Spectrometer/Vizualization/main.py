import io
import subprocess
import os


# название исполняемого файла на C
get_data_pass = 'OptoskyDemo'

# рабочая директори
working_directory = '../Get_data'

# Убедитесь, что файл существует в указанной директории
if os.path.isfile(f'./{working_directory}/{get_data_pass}'):
    print("Файл найден")
else:
    print(f"Файл не найден, проверьте путь")

# перейти в директорию
os.chdir(working_directory)

file = open("text1.txt", "w")

# Запуск программы на C
process_set = subprocess.Popen(
    [f'./{get_data_pass}'],
    stdin=subprocess.PIPE,  # Для передачи данных через стандартный ввод
    stdout=subprocess.PIPE,  # Для получения данных через стандартный вывод
    stderr=subprocess.PIPE,  # Для получения ошибок
    text=True,   # Для работы с текстовыми строками
    cwd=working_directory
)

# Функция для отправки команды и чтения полного ответа
def send_command(input_data, process=process_set):        # Отправляем команду
    process.stdin.write(f"{input_data}\n")
    # Очистка буфера ввода
    process.stdin.flush()

    # Чтение троки stdout
    output = [] # = process.stdout.readline()
    while True:
        line = process.stdout.readline()
        if line == '' and process.poll() is not None:
            break
        if line:
            output.append(line.strip())
            print(line)

    return '\n'.join(output)


# Отправка команд и получение ответа
for i in range(1):
    data = f"input_data_{i}"  # Ваши данные для передачи
    result = send_command(data)  # Передача данных в программу
    print(f"Result for {data}: {result}")


# Закрытие потока stdin и завершение процесса
process_set.stdin.close()
process_set.stdout.close()
process_set.stderr.close()
process_set.terminate()