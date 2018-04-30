from app import app, command_system
from app.scheduledb import ScheduleDB

import re
import difflib


def auto_posting_on(uid, key, arg=""):
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

    data = arg.split(' ', maxsplit=1)
    time = data[0]
    type = ''

    if len(data) == 2:
        type = data[1]
    try:
        if re.match(time, r'\d{1,2}:\d\d'):
            raise BaseException
    except:
        return "Вы отправили пустую строку или строку неправильного формата. Правильный формат ЧЧ:ММ"

    try:
        with ScheduleDB(app.config) as db:
            user = db.find_user(uid)

            if user and user[0] != "":
                hour = ''.join(filter(lambda x: x.isdigit(), re.split(r':', time)[0]))
                minutes = ''.join(filter(lambda x: x.isdigit(), re.split(r':', time)[1]))

                if difflib.SequenceMatcher(None, type, 'сегодня').ratio() > \
                        difflib.SequenceMatcher(None, type, 'завтра').ratio() or type == '':
                    is_today = True
                else:
                    is_today = False

                # Проверка на соответствие введённых пользователем данных принятому формату
                if not hour.isdigit() or not minutes.isdigit():
                    return 'Вы отправили пустую строку или строку неправильного формата. Правильный формат ЧЧ:ММ'


                if db.set_auto_post_time(uid, (hour + ":" + minutes + ":" + "00").rjust(8, '0'), is_today):
                    return 'Время установлено'
                else:
                    return 'Случилось что то странное, попробуйте ввести команду заново'
            else:
                return 'Вас ещё нет в базе данных, поэтому пройдите простую процедуру регистрации'
    except BaseException as e:
        return 'Случилось что то странное, попробуйте ввести команду заново'


auto_posting_on_command = command_system.Command()

auto_posting_on_command.keys = ['ap', 'автопостинг', '/auto_posting_on', 'auto_posting_on']
auto_posting_on_command.description = 'Включение и выбор времени для автоматической отправки расписания в диалог, время должно иметь формат ЧЧ:ММ'
auto_posting_on_command.process = auto_posting_on
