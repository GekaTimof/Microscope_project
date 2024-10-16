import  subprocess

get_data_pass = '../Get_data/OptoskyDemo'


# Запуск программы C один раз
process = subprocess.Popen(
    [f'./{get_data_pass}'],
    stdin=subprocess.PIPE,  # Для передачи данных через стандартный ввод
    stdout=subprocess.PIPE,  # Для получения данных через стандартный вывод
    stderr=subprocess.PIPE,  # Для получения ошибок
    text=True   # Для работы с текстовыми строками
)

# Функция для отправки данных и получения ответа
def send_command(input_data):
    process.stdin.write(f"{input_data}\n")  # Отправка данных
    process.stdin.flush()  # Очистка буфера, чтобы данные дошли до процесса
    output = process.stdout.readline()  # Чтение строки из stdout
    return output.strip()  # Возврат строки без символов новой строки


# Пример многократного взаимодействия
for i in range(10):
    data = f"input_data_{i}"  # Ваши данные для передачи
    result = send_command(data)  # Передача данных в программу
    print(f"Result for {data}: {result}")


# Завершение процесса, если он больше не нужен
process.stdin.close()
process.stdout.close()
process.terminate()
