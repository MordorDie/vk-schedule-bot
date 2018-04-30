from app import app, command_system, helpers
from app.scheduledb import ScheduleDB
from app.scheduleCreator import create_schedule_text
from datetime import datetime, time, timedelta


def schedule(uid, key, data=""):
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

    week_type = -1
    message=''
    if key == 'неделя':
        days = helpers.ScheduleType['неделя']
    elif key == 'сегодня' or key == 'расписание':
        today = datetime.now()
        # Если запрашивается расписание на сегодняшний день,
        # то week_type равен остатку от деления на 2 номера недели в году, т.е он определяет чётная она или нечётная
        week_type = today.isocalendar()[1] % 2

        # Если время больше чем 21:30, то показываем расписание на следующий день
        if today.time() >= time(21, 30):
           today += timedelta(days=1)
        # Если сегодня воскресенье, то показывается расписание на понедельник следующей недели
        # Также в этом случае, как week_type используется тип следующей недели
        if datetime.weekday(today) == 6:
           today += timedelta(days=1)
           week_type = (week_type + 1) % 2

        days = [helpers.daysOfWeek[datetime.weekday(today)]]
    elif key == 'завтра':
        tomorrow = datetime.now()
        # Если запрашивается расписание на сегодняшний день,
        # то week_type равен остатку от деления на 2 номера недели в году, т.е он определяет чётная она или нечётная
        week_type = tomorrow.isocalendar()[1] % 2

        tomorrow += timedelta(days=1)
        # Если сегодня воскресенье, то показывается расписание на понедельник следующей недели
        # Также в этом случае, как week_type используется тип следующей недели
        if datetime.weekday(tomorrow) == 6:
           tomorrow += timedelta(days=1)
           week_type = (week_type + 1) % 2

        days = [helpers.daysOfWeek[datetime.weekday(tomorrow)]]
    else:
        days = [helpers.ScheduleType[key]]

    for day in days:
        try:
            with ScheduleDB(app.config) as db:
                user = db.find_user(uid)
            if user and user[0] != '':
                result = create_schedule_text(user[0], day, week_type)
                for schedule_message in result:
                    message += schedule_message + "\n\n"
            else:
                message = "Вас ещё нет в базе данных, поэтому пройдите простую процедуру регистрации:\n"
                message += 'Введите команду(без кавычек): регистрация "название вуза" "факультет" "группа"\n\n'
                message += 'Если вы допустите ошибку, то просто наберите команду заново.\n'
        except BaseException as e:
            message = "Случилось что то странное, попробуйте ввести команду заново"
    return message


schedule_command = command_system.Command()

schedule_command.keys = ['расписание', 'неделя', 'сегодня', 'завтра', 'понедельник', 'вторник', 'cреда', 'четверг', 'пятница', 'cуббота', 'воскресенье']
schedule_command.description = 'Выводит расписание, также можно написать любой день недели или команду "сегодня" или "завтра"'
schedule_command.process = schedule
