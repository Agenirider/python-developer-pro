# h1 Анализатор логов web сервера

# h2 Поля лог-файла
'$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" '
'$status $body_bytes_sent "$http_referer" '
'"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
 '$request_time';

# h2 Запуск через командную строку

python log_analyzer.py

доступные опции:
--config указывается пусть к конфиг файлу

конфиг-файл по умолчанию config.ini

# h3 Трубемая структира конфигурационного файла
[DEFAULT]
REPORT_SIZE = 1000
REPORT_DIR = ./reports
LOG_DIR = ./log
TMP_DIR =  ./tmp
LOG_FILE =  performer.log

# h2 Результат
В директории reports генерируется файл с раширением html содержащий таблицу с данными

# h2 Логирование процесса 
Генерируется лог файл perfomer.log
Значение по умолячанию performer.log

# h2 Тестирование
python.exe -m unittest -v test.py

