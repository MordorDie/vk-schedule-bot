from app import vkapi
import os
import importlib
from app.command_system import command_list
from app.scheduledb import ScheduleDB
import difflib

def load_modules():
    # путь от рабочей директории, ее можно изменить в настройках приложения
    files = os.listdir("app/commands")
    modules = filter(lambda x: x.endswith('.py'), files)
    for m in modules:
        importlib.import_module("app.commands." + m[0:-3])


def get_answer(uid, body):
    data = body.split(' ', maxsplit=1)
    user_command = data[0]
    arg = ""
    if len(data) == 2:
        arg = data[1]

    # Сообщение по умолчанию если распознать не удастся
    message = "Не удалось распознать запрос. Напишите 'помощь', чтобы узнать доступные команды"
    max_ratio = 0
    command = None
    key = ''
    for c in command_list:
        for k in c.keys:
            ratio1 = difflib.SequenceMatcher(None, k, user_command).ratio()
            ratio2 = difflib.SequenceMatcher(None, k, body).ratio()
            ratio = max(ratio1, ratio2)

            if ratio > max_ratio:
                max_ratio = ratio
                command = c
                key = k
                if ratio >= 0.95:
                    message = c.process(uid, key, arg)
                    return message
    if max_ratio > 0.5:
        message = command.process(uid, key, arg)
        message = 'Ваш запрос распознан как: {}\n\n{}'.format(key, message)
        return message

    return message


def create_answer(data, token):
    load_modules()
    user_id = data['user_id']
    message = get_answer(user_id, data['body'].lower())
    vkapi.send_message(user_id, token, message)
