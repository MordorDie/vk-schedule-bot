from app import app, helpers
from app.scheduledb import ScheduleDB
from app.scheduleCreator import create_schedule_text
from app import vkapi

from datetime import datetime, timedelta
import threading
from time import sleep


def auto_posting(current_time):
    today = datetime.now()
    week_type = (today.isocalendar()[1] + 1) % 2

    if datetime.weekday(today) == 6:
        today += timedelta(days=1)
        week_type = (week_type + 1) % 2

    day = [helpers.daysOfWeek[datetime.weekday(today)]]

    # Выборка пользователей из базы у которых установлена отправка расписния на текущий день
    with ScheduleDB(app.config) as db:
        users = db.find_users_where(auto_posting_time=current_time, is_today=True)

    if users is None:
        return None
    try:
        count = 0
        for user in users:
            uid = user[0]
            tag = user[1]

            schedule = create_schedule_text(tag, day[0], week_type)
            vkapi.send_message(uid, app.config['TOKEN'], schedule)
            count += 1
            if count > 20:
                sleep(1)

            # Логирование
    except BaseException as e:
        pass

    # Выборка пользователей из базы у которых установлена отправка расписния на завтрашний день,
    # если сегодня воскресенье, то расписание будет отправляться на понедельник.
    if datetime.weekday(datetime.now()) != 6:
        today += timedelta(days=1)

    day = [helpers.daysOfWeek[datetime.weekday(today)]]

    with ScheduleDB(app.config) as db:
        users = db.find_users_where(auto_posting_time=current_time, is_today=False)

    if users is None:
        return None
    try:
        count = 0
        for user in users:
            uid = user[0]
            tag = user[1]

            schedule = create_schedule_text(tag, day[0], week_type)
            vkapi.send_message(uid, app.config['TOKEN'], schedule)
            count += 1
            if count > 20:
                sleep(1)

            # Логирование
    except BaseException as e:
        pass


if __name__ == "__main__":
    while True:
        threading.Thread(target=auto_posting(datetime.now().time().strftime("%H:%M:00"))).start()
        # Вычисляем разницу в секундах, между началом минуты и временем завершения потока
        time_delta = datetime.now() - datetime.now().replace(second=0, microsecond=0)
        # Поток засыпает на время равное количеству секунд до следующей минуты
        sleep(60 - time_delta.seconds)
