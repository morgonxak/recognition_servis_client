import datetime

DEBUG = False

config = {}

#API
config['URL_API_server'] = 'https://192.168.1.69:2561/api'

#Socket server
config['IP_API_server'] = '192.168.1.69'
config['PORT_API_server'] = 9000

#settings for data base
config['IP_DB'] = '127.0.0.1'
config['PORT_DB'] = 5432
config['login_DB'] = 'dima'
config['password_DB'] = 'asm123'
config['name_dataBase'] = 'faceid'


#Settings RealSense
config['size_frame'] = (640, 480)
config['fps'] = 30
#Для определенного турникета
config['sn_realSense'] = ['951422060620', '950122060869']

#jetsonNano
config['path_dir_calassificator'] = '/home/dima/PycharmProjects/face_id_jetsonNano/app_faceId_jetsonNano/data'
config['path_dir_temp'] = '/home/dima/PycharmProjects/face_id_jetsonNano/app_faceId_jetsonNano/data/temp'
config['path_CascadeClassifier'] = r'/home/dima/PycharmProjects/face_id_jetsonNano/app_faceId_jetsonNano/data/haarcascade_frontalface_default.xml'

#Sestem
config['quantity_processing_threads'] = 2  #Количество потоков для обработки

config['classifications'] = {}  #{"model_cvm": model_cvm, "model_knn": model_knn}
config['dictProcessing'] = {}  #Результат обработки  # {"sn":['person_ID' or 'None'] or ''}

config['processing_faceid_threading'] = []  #ДЛя хранения основных потоков обработки - очередь
config['face_recognition_size'] = 200  #Размер распознаного лица
config['time_between_passes'] = datetime.timedelta(minutes=0, seconds=20)  #Время между проходами одного и тогоже человека в сек

#Обновления
config['time_between_updates'] = datetime.timedelta(minutes=1, seconds=30)  #Время между проверками обновления
config['time_last_updates'] = datetime.datetime.now()  #Время последнего обновления

config['version'] = {"version": 0, "changes": "\u041e\u0431\u0443\u0447\u0435\u043d\u043d\u044b\u0439 \u043d\u0430 50 \u0444\u043e\u0442\u043e\u0433\u0440\u0430\u0444\u0438\u044f\u0445 \u043a\u0430\u0436\u0434\u043e\u0433\u043e \u0447\u0435\u043b\u043e\u0432\u0435\u043a\u0430 \u0432 \u0431\u0430\u0437\u0435 614 \u0447\u0435\u043b\u043e\u0432\u0435\u043a"}


config['knn_tolerance'] = 0.6  #Точность распознования
config['obj_db'] = None
config['obj_API'] = None