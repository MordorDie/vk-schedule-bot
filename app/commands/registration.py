from app import app, command_system
from app.scheduledb import ScheduleDB


def registration(uid, key, data=""):
   if data == '':
       return 'Вы не указали где хотите зарегистрироваться'

   try:
        with ScheduleDB(app.config) as db:
            organizations = db.get_similar_organizations(data)

        if len(organizations) != 0:
            if organizations[0][2] > 0.8:
                message = 'Вы зарегистрированны в: {}'.format(organizations[0][1])
            else:
                message = 'Вы зарегистрированны в наиболее совпадающей с запросом группе: {}\n-----\nДругие похожие:\n'.format(organizations[0][1])
                for org in organizations:
                    message += "{}\n".format(org[1])

            with ScheduleDB(app.config) as db:
                user = db.find_user(uid)
                if user:
                    db.update_user(uid, " ", " ", organizations[0][0])
                else:
                    db.add_user(uid, " ", " ", organizations[0][0])
            message += '\n\n Напишите "помощь", чтобы узнать доступные команды'

            return message
        else:
            return 'Случилось что то странное, попробуйте ввести команду заново'
   except BaseException as e:
       return 'Случилось что то странное, попробуйте ввести команду заново'


registration_command = command_system.Command()

registration_command.keys = ['регистрация', '/registration', 'registration']
registration_command.description = 'Введите команду(без кавычек): регистрация "название вуза" "факультет" "группа"'
registration_command.process = registration
