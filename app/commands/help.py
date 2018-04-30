from app import command_system


def help(uid, key, data=""):
    message = 'Список команд:\n'

    for c in command_system.command_list:
        message += '{}: {}\n\n'.format(c.keys[0], c.description)
    return message


help_command = command_system.Command()

help_command.keys = ['помощь', '/help', 'help']
help_command.description = 'Выводит информацию о боте и список доступных команд'
help_command.process = help
