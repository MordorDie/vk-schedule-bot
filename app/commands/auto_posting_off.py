from app import app, command_system
from app.scheduledb import ScheduleDB


def auto_posting_off(uid, key, arg=""):
    # Если пользователя нет в базе, то ему выведет предложение зарегистрироваться
    try:
        with ScheduleDB(app.config) as db:
            user = db.find_user(uid)
        if not user or user[0] == '':
            message = "Вас ещё нет в базе данных, поэтому пройдите простую процедуру регистрации:\n"
            message += 'Введите команду(без кавычек):\n\nрегистрация "название вуза" "факультет" "группа"\n\n'
            message += 'Если вы допустите ошибку, то просто наберите команду заново.\n'
            return message
    except BaseException as e:
        return 'Случилось что то странное, попробуйте ввести команду заново'

    try:
        with ScheduleDB(app.config) as db:
            user = db.find_user(uid)
            if user:
                if db.set_auto_post_time(uid, None, None):
                    return 'Автоматическая отправка расписания успешно отключена'
                else:
                    return 'Случилось что то странное, попробуйте ввести команду заново'
            else:
                return 'Вас ещё нет в базе данных, поэтому пройдите простую процедуру регистрации'
    except BaseException as e:
        return 'Случилось что то странное, попробуйте ввести команду заново'


auto_posting_off_command = command_system.Command()

auto_posting_off_command.keys = ['ap off', 'автопостинг off', '/auto_posting_off', 'auto_posting_off']
auto_posting_off_command.description = 'Выключение автоматической отправки расписания'
auto_posting_off_command.process = auto_posting_off
