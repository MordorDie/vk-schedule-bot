from app import command_system


def start(uid, key, data=""):
    message = '''Привет! Чтобы начать пользоваться ботом сделайте несколько действий:\n
Введите команду(без кавычек): регистрация "название вуза" "факультет" "группа"\n\n
Если вы допустите ошибку, то просто наберите команду заново.\n\n
Мануал по использованию бота
vk.com/topic-165732899_38346859'''
    return message


start_command = command_system.Command()

start_command.keys = ['старт', '/start', 'start']
start_command.description = 'Выводит стартовое сообщение и предложение зарегистрироваться'
start_command.process = start
