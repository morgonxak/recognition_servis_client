import pyrealsense2 as rs
import numpy
import cv2
import pickle
import face_recognition


pipeline_cam_1 = rs.pipeline()
pipeline_cam_2 = rs.pipeline()

config_cam_1 = rs.config()
config_cam_2 = rs.config()

config_cam_1.enable_stream(rs.stream.color, 640, 480, rs.format.rgb8, 30)
config_cam_1.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
config_cam_1.enable_device('951422060620')

config_cam_2.enable_stream(rs.stream.color, 640, 480, rs.format.rgb8, 30)
config_cam_2.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
config_cam_2.enable_device('950122060869')

# Инициализация моделей нейросетей

model_knn = pickle.load(open(r'/app_faceId_jetsonNano/data/classificators/2/knn_model.pk', 'rb'))
model_cvm = pickle.load(open(r'/app_faceId_jetsonNano/data/classificators/2/cvm_model.pk', 'rb'))


def predict_cvm(face_encoding):
    '''
    Проверяет пользователя по модели CVM
    :param face_encoding: Получаем дескриптор
    :return: person_id -- Уникальный идентификатор пользователя
    '''

    # Прогнозирование всех граней на тестовом изображении с использованием обученного классификатора

    person_id = model_cvm.predict([face_encoding])

    return person_id

def predict_knn(face_encoding, tolerance=0.42):
    '''
    Проверяет пользователя по модели knn
    :param face_encoding:
    :return: person_id, dist == уникальный идентификатор и дистанция до него
    '''
    closest_distances = model_knn.kneighbors([face_encoding], n_neighbors=1)

    are_matches = [closest_distances[0][i][0] <= tolerance for i in range(1)]

    if are_matches[0]:
        person_id = model_knn.predict([face_encoding])[0]
    else:
        person_id = "Unknown"

    return person_id

def getFrame_cam(pipeline_cam):
    '''
    Генератор кадров глубины и RGB
    :return:
    '''
    align_to = rs.stream.color
    align = rs.align(align_to)

    while True:
        frames = pipeline_cam.wait_for_frames()

        # Align the depth frame to color frame
        aligned_frames = align.process(frames)

        # Получить выровненные кадры
        aligned_depth_frame = aligned_frames.get_depth_frame()
        color_frame = aligned_frames.get_color_frame()

        # Проверить, что оба кадра действительны
        if not aligned_depth_frame or not color_frame:
            continue

        depth_image = numpy.asanyarray(aligned_depth_frame.get_data())
        color_image = numpy.asanyarray(color_frame.get_data())

        color_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2RGB)

        yield color_image, depth_image


def accurate_check(frame):
    '''
    Проверка фотографии с полощью нескольких нейронных сетей
    :param personID_predict_cvm:
    :param personID_euclidean_distance:
    :return: personID или None
    '''

    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

    # Найти все лица в текущем кадре видео
    face_locations = face_recognition.face_locations(small_frame)

    # Проверка если количество лиц на кадре больше 1 или нет лиц совсем
    if len(face_locations) != 1:
        #print("Проверка если количество лиц на кадре больше 1 или нет лиц совсем")
        return -1

    # Вычесляем дескриптор
    face_encoding = face_recognition.face_encodings(small_frame, face_locations)[0]

    personID_predict_cvm = predict_cvm(face_encoding)
    personID_predict_knn = predict_knn(face_encoding)

    if personID_predict_cvm == personID_predict_knn:
        return personID_predict_cvm[0]
    else:
        return "Unknown"

if __name__ == '__main__':
    pipeline_cam_1.start(config_cam_1)
    pipeline_cam_2.start(config_cam_2)

    for freme1, freme2 in zip(getFrame_cam(pipeline_cam_1), getFrame_cam(pipeline_cam_2)):
        color_image_1, depth_image_1 = freme1
        color_image_2, depth_image_2 = freme2


        # cv2.imshow("freme1_color", color_image_1)
        # cv2.imshow("freme2_color", color_image_2)
        #
        # cv2.imshow("freme1_depth", depth_image_1)
        # cv2.imshow("freme2_depth", depth_image_2)

        person_id_1 = accurate_check(color_image_1)
        person_id_2 = accurate_check(color_image_2)


        print(person_id_1, person_id_2)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break