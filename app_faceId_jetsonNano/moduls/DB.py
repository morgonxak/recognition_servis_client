import psycopg2
from app_faceId_jetsonNano import config as config_app

class BD:
    def __init__(self, dict_connect_settings):
        #Соеденения с базой данных
        try:
            self.con = psycopg2.connect(
                database=dict_connect_settings['name_dataBase'],
                user=dict_connect_settings['login_DB'],
                password=dict_connect_settings['password_DB'],
                host=dict_connect_settings['IP_DB'],
                port=dict_connect_settings['PORT_DB'])

        except BaseException as e:
            raise ValueError("Error connect BD: " + str(e))

        try:
            self.cur = self.con.cursor()
        except BaseException as e:
            raise ValueError("Error create cursor " + str(e))

    def getData_by_person_id(self, person_id):
        '''
        Получает информацию по индитификатору пользователя
        :param person_id: 'b9e1d2bc-ac4f-4b5b-bec3-fd586c8c3e49'
        :return: [('004EF89D', 'b9e1d2bc-ac4f-4b5b-bec3-fd586c8c3e49', 'Шумелев Дмитрий Игоривич')]
        '''
        try:
            self.cur.execute("SELECT card_id_code, person_id, full_name FROM user_bd WHERE person_id = '{}'".format(person_id))

            rows = self.cur.fetchall()
        except BaseException as e:
            raise ValueError("Error get Users info: " + str(e))
        else:
            return rows

    def pull_event(self, dict_data):
        '''
        Добовляет данные событий
        :param dict_data:
        :return:
        '''
        try:
            self.cur.execute(
                "INSERT INTO visits (person_id, time_event, events, event_source, subject, summary) VALUES ('{}','{}','{}','{}', '{}', '{}')".format(
                    dict_data['person_id'], dict_data['time_event'], dict_data['events'], dict_data['event_source'], dict_data['subject'], dict_data['summary'])
            )
            self.con.commit()
        except BaseException as e:
            print("error", e)

    def get_latest_version(self):
        '''
        Получает последнюю версию классификатора
                   version_classification,                              changes,                               path_classification
        :return:  (1,                      'Обученный на 50 фотографиях каждого человека в базе 614 человек', 'data/classificators/1')
        '''
        try:
            #SELECT version_classification, changes, path_classification FROM classification WHERE person_id = MAX (version_classification)
            #SELECT MAX (version_classification) from classification UNION SELECT version_classification, changes, path_classification from classification

            self.cur.execute("SELECT MAX (version_classification) from classification")
            max_version_classification = self.cur.fetchall()

            self.cur.execute("SELECT version_classification, changes, path_classification FROM classification WHERE version_classification = {}".format(max_version_classification[0][0]))
            rows = self.cur.fetchall()

        except BaseException as e:
            raise ValueError("Error get Users info: " + str(e))
        else:
            return rows[0]

if __name__ == '__main__':
    import datetime
    test_BD = BD(config_app)
    personID = 'b9e1d2bc-ac4f-4b5b-bec3-fd586c8c3e1'
    info_user = test_BD.getData_by_person_id(personID)

    dict_data = {}
    dict_data['person_id'] = personID
    dict_data['time_event'] = str(datetime.datetime.now())
    dict_data['events'] = "Открытия двери"
    dict_data['event_source'] = "ТЕстовая дверь"
    dict_data['subject'] = "тест"
    dict_data['summary'] = "тест"

    test_BD.pull_event(dict_data)
    print(info_user)
