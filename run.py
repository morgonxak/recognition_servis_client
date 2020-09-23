from app_faceId_jetsonNano import config, DEBUG
from app_faceId_jetsonNano.moduls import api, cam_RealSense, DB, socket_get_classification, processing
import pickle
import queue
import cv2
import threading
import datetime
import os

def loadClassigication(path_calssification):
    '''

    :return:
    '''
    try:
        model_knn = pickle.load(open(os.path.join(path_calssification, 'knn_model.pk'), 'rb'))
        model_cvm = pickle.load(open(os.path.join(path_calssification, 'cvm_model.pk'), 'rb'))

        config['classifications'] = {"model_cvm": model_cvm, "model_knn": model_knn}
    except BaseException as e:
        print("error loadClassigication:", str(e))
        return -1
    return 0

def threading_getResult_and_read_DB():
    '''
    Получения результата распознования
    действия
    1. если пришло None - нечего
    2. Ели потшло personId добавить в базу
    3. Unknown - нечего
    :return:
    '''
    openDoor = {'951422060620': 'Открытия двери',  #Решим, personId, timeEvent
                '950122060869': 'Закрытия двери'}

    temp_last_peson_id = {'951422060620': [None, None],  #personId, timeEvent
                          '950122060869': [None, None]}

    def pullEvent(personID, sn):
        '''
        Отправляет данные о том что открыл дверь пользователю
        :param personID:
        :return:
        '''
        #Проверка на частое распознование пользователя
        if not temp_last_peson_id[sn][0] is None and personID == temp_last_peson_id[sn][0]:
            if datetime.datetime.now() - temp_last_peson_id[sn][1] < config['time_between_passes']:
                return -1

        time_event = datetime.datetime.now()


        dict_data = {}
        dict_data['person_id'] = personID


        dict_data['time_event'] = str(time_event)

        dict_data['events'] = openDoor.get(sn, "Такой устройства нат")
        dict_data['event_source'] = "ТЕстовая дверь"
        dict_data['subject'] = "JetsonNano"
        dict_data['summary'] = sn
        config['obj_db'].pull_event(dict_data)

        #Для отслеживания частого распознования
        temp_last_peson_id[sn][0] = personID
        temp_last_peson_id[sn][1] = time_event

        print(dict_data)

    while True:
        res1 = config['dictProcessing'].pop('951422060620', None)
        res2 = config['dictProcessing'].pop('950122060869', None)

        if not res1 is None and res1 != "Unknown":
            pullEvent(res1, "951422060620")

        if not res2 is None and res2 != "Unknown":
            pullEvent(res2, "950122060869")

def threading_check_for_updates():
    '''
    Проверка обновлений для классикаторов
    :return:
    '''
    while True:
        if datetime.datetime.now() - config['time_last_updates'] > config['time_between_updates']:
            #update
            response_last_version = config['obj_API'].getTheVersionOfTheLastClassifier()
            print(response_last_version)
            if config['version'] == response_last_version[0]:
                config['time_last_updates'] = datetime.datetime.now()
                continue

            try:
                connect_serser = socket_get_classification.get_data_server(config['IP_API_server'], config['PORT_API_server'])
                connect_serser.set_path_save(os.path.join(config['path_dir_temp'], str(response_last_version[0]['version'])+'.zip'))
                connect_serser.start()

            except BaseException as e:
                print("Error_connnet sersver:", str(e))
            else:
                response = config['obj_API'].getClassifier()
                if DEBUG: print(response)
                path_unpack = os.path.join(config['path_dir_calassificator'], 'classificators', str(response_last_version[0]['version']))
                if DEBUG: print(path_unpack)
                #Распаковываем
                connect_serser.unpack(connect_serser.path_save, path_unpack)

                #Загружаем новые данные
                loadClassigication(path_unpack)
                print("Загрузка завершена")

            config['time_last_updates'] = datetime.datetime.now()
            config['version'] = response_last_version[0]


face_detector = cv2.CascadeClassifier(config['path_CascadeClassifier'])

def pull_queue(frame, queue_obj, sn):
    '''
    принимает кадр с камеры и принимает решения отправить ее для распознования или нет (сама и отправляет)
    :param frame:
    :param queue_obj:
    :param sn:
    :return:
    '''
    def get_face(image):
        '''
        Классификатор хаара для быстрого определения лиц
        если на фото 1 человет то отправляем размеры лица
        :param image:
        :return:
        '''
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = face_detector.detectMultiScale(gray, 1.3, 5)
        if len(faces) == 1:
            return faces
        else:
            return None

    faces = get_face(frame)
    if not faces is None:
        x, y, w, h = faces[0]
        #если человек далеко стоит то не не отправляем с очередь распознования
        if w >= config['face_recognition_size']:
            #cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            queue_obj.put([frame, sn])
            if DEBUG: print(x, y, w, h)

def main():
    #Загрузка классификатором
    path_load_calssification = os.path.join(config['path_dir_calassificator'], 'classificators', str(config['version']['version']))
    loadClassigication(path_load_calssification)

    # база Данных
    config['obj_db'] = DB.BD(config)
    config['obj_API'] = api.api_server_faceID(config['URL_API_server'])

    #Запустить очередь на обработку
    queue_obj = queue.Queue()
    for count in range(config['quantity_processing_threads']):
        threading_obj = processing.processing_faceid(queue_obj, config)
        threading_obj.name = 'processing_face_id:' + str(count)
        config['processing_faceid_threading'].append(threading_obj)
        threading_obj.start()

    #запуск потока ослеживание обновлений с сервера
    obj_update = threading.Thread(target=threading_check_for_updates)
    obj_update.name = "threading update"
    obj_update.start()

    #Основной цикл программы по получению кадров с камеры и отсылки данных в очередь
    list_Obj_Cam = []
    for sn_cam in config['sn_realSense']:
        cam = cam_RealSense.cameraRealSense(sn_cam)
        cam.start_RS()
        list_Obj_Cam.append(cam)

    config['threading_getResult_and_read_DB'] = threading.Thread(target=threading_getResult_and_read_DB)
    config['threading_getResult_and_read_DB'].name = 'threading_getResult_and_read_DB'
    config['threading_getResult_and_read_DB'].start()



    for count, ((RGB_cam_0, Depth_cam_0), (RGB_cam_1, Depth_cam_1)) in enumerate(zip(list_Obj_Cam[0].getFrame_cam(), list_Obj_Cam[1].getFrame_cam())):

        cv2.imshow("cam1", RGB_cam_0)
        cv2.imshow("cam2", RGB_cam_1)

        pull_queue(RGB_cam_0, queue_obj, list_Obj_Cam[0].sn)
        pull_queue(RGB_cam_1, queue_obj, list_Obj_Cam[1].sn)


        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("close threading")
        for i in config['processing_faceid_threading']:
            del i