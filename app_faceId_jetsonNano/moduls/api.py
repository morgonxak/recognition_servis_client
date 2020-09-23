import requests
import os
from app_faceId_jetsonNano import config as config_app

'''
    api faceId
    Функционал:
    get
     -Получить количество пользователей (getNumberUsers)
     -Получить информацию о пользователе по его id (getUserInformationByUserId)
     -Получить информацию о пользователе по его ФИО (getInformationAboutTheUserByHisName)  --------------------
     -Получить версию последнего классификатора (getTheVersionOfTheLastClassifier)
     -Получить классификатор (getClassifier)

    Post
     -Создать пользователя с уникальным id (createUserWithUniqueId)
     -Создание нового пропукново пункта (createNewCheckpoint)  ---------

    delete
     -Удаление пользователя по ID (deleteUserById)
     -Удаление пропускново пункта (deleteCheckpoint) --------------

    put
     -Изменить информацию о пользователе по его ID (changeUserInformationByUserId)
     -Изменить параметры пропускново пункта (changeCheckpointSettings)  ------------
'''

class api_server_faceID:
    def __init__(self, URL:str):
        self.url = URL

    ##############  GET  #######################
    def getNumberUsers(self):
        '''
        Получить количество пользователей
        :return:
        '''
        response = requests.get(os.path.join(self.url, 'getNumberUsers'), verify=False)

        if response.status_code == 200:
            return response.text, response.headers
        else:
            return -1

    def getUserInformationByUserId(self, personId:str):
        '''
        Получить информацию о пользователе по его id
        :param personId:
        :return:
        '''

        response = requests.get(os.path.join(self.url, 'getUserInformationByUserId'), json={"person_id": personId}, verify=False)
        if response.status_code == 200:
            return response.json(), response.headers
        else:
            return -1

    def getTheVersionOfTheLastClassifier(self):
        '''
        Получить версию последнего классификатора
        :return:
        '''
        response = requests.get(os.path.join(self.url, 'getTheVersionOfTheLastClassifier'), verify=False)

        if response.status_code == 200:
            return response.json(), response.headers
        else:
            return -1

    def getClassifier(self):
        '''
        Получить классификатор файлы
        :return:
        '''
        response = requests.get(os.path.join(self.url, 'getClassifier'), verify=False)

        if response.status_code == 200:
            return response.json, response.headers
        else:
            return -1


if __name__ == '__main__':
    URL = config_app['URL_API_server']
    test_api = api_server_faceID(URL)

    count_users = test_api.getNumberUsers()
    info_users = test_api.getUserInformationByUserId('b9e1d2bc-ac4f-4b5b-bec3-fd586c8c3e1')
    info_version = test_api.getTheVersionOfTheLastClassifier()
    #classification = test_api.getClassifier()

    #print(count_users)
    #print(info_users)
    print(info_version[0])
    #print(classification)