from app import app, command_system
from app.scheduledb import ScheduleDB


def report(uid, key, arg=""):
    if arg != '':
        with ScheduleDB(app.config) as db:
            if db.add_report(uid, arg):
                return "Сообщение принято"
            else:
                return "Случилось что то странное, попробуйте ввести команду заново"
    else:
        return 'Вы отправили пустую строку. Пример: сообщение "ваше сообщение"'


report_command = command_system.Command()

report_command.keys = ['сообщение', 'репорт', '/report', 'report', '/send_report', 'send_report']
report_command.description = 'Можно отправить информацию об ошибке или что то ещё. Введите команду(без кавычек): сообщение "ваше сообщение"'
report_command.process = report
