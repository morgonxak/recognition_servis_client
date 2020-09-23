import pyrealsense2 as rs
import numpy
import cv2
from app_faceId_jetsonNano import config as config_app

class mode:
    '''Содержет режимы работы устройства'''
    def __init__(self, config):
        self.config = config

    def eneble_depth_and_rgb_cam(self):
        self.config.enable_stream(rs.stream.color, config_app['size_frame'][0], config_app['size_frame'][1], rs.format.rgb8, config_app['fps'])
        self.config.enable_stream(rs.stream.depth, config_app['size_frame'][0], config_app['size_frame'][1], rs.format.z16, config_app['fps'])

    def eneble_rgb_cam(self):
        self.config.enable_stream(rs.stream.color, config_app['size_frame'][0], config_app['size_frame'][1], rs.format.rgb8, config_app['fps'])

    def disable_depth_and_rgb_cam(self):
        self.config.disable_stream(rs.stream.color)
        self.config.disable_stream(rs.stream.depth)

    def disable_depth_cam(self):
        self.config.disable_stream(rs.stream.depth)

class cameraRealSense(mode):

    def __init__(self, sn: str):

        self.sn = sn
        self.pipeline = rs.pipeline()

        self.config = rs.config()

        self.config.enable_device(sn)

        self.status_stream = False
        self.status_init = False
        self.current_mode_camer = 3

        mode.__init__(self, self.config)

        # режимы работы камеры
        self.camera_modes = {1: self.eneble_depth_and_rgb_cam,
                             2: self.eneble_rgb_cam,
                             3: self.disable_depth_and_rgb_cam,
                             4: self.disable_depth_cam
                             }


    def start_RS(self, mode_camer:int=2):
        '''
        Запускает камеру и инециализирует запись в определенную папку
        :param type_init: True - обычная для отображения с камеры  False - Для чтения из файла
        :param pathSave_rosbag: c:\\video.bag
        :return:
        '''

        #Камера
        if not self.status_init:

            self.camera_modes.get(mode_camer, self.camera_modes[2])()

            profile = self.pipeline.start(self.config)

            self.status_stream = True
            self.status_init = True
            self.current_mode_camer = mode_camer
            return 0
        return -1


    def stop_camera(self):
        '''
        Останавливает камеру либо для типа чтения с файла или с RS
        :param type_init:
        :return:
        '''
        if self.status_init == True:
            self.camera_modes.get(3)()
            self.current_mode_camer = 3
            return 0
        return -1

    def __generator_RGB(self, frames):
        '''
        Генератор RGB изображений
        :param frame:
        :return:
        '''
        color_frame = frames.get_color_frame()
        if not color_frame:
            return None

        color_image = numpy.asanyarray(color_frame.get_data())
        color_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2RGB)

        return color_image, None

    def __generator_RGB_Depth(self, frames, align):
        '''
        Геренатор RGB и Depth изображений выровненные
        :return:
        '''
        # Align the depth frame to color frame
        aligned_frames = align.process(frames)

        # Получить выровненные кадры
        aligned_depth_frame = aligned_frames.get_depth_frame()
        color_frame = aligned_frames.get_color_frame()

        # Проверить, что оба кадра действительны
        if not aligned_depth_frame or not color_frame:
            return None

        depth_image = numpy.asanyarray(aligned_depth_frame.get_data())
        color_image = numpy.asanyarray(color_frame.get_data())

        color_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2RGB)

        return color_image, depth_image

    def getFrame_cam(self):
        '''
        Генератор кадров глубины и RGB
        :return:
        '''
        align_to = rs.stream.color
        align = rs.align(align_to)

        while True:
            if self.current_mode_camer == 3:
                continue

            frames = self.pipeline.wait_for_frames()
            generator = None

            if self.current_mode_camer == 4:
                generator = self.__generator_RGB(frames)

            if self.current_mode_camer == 2:
                #Работаем только с RGB камерой
                generator = self.__generator_RGB(frames)

            if self.current_mode_camer == 1:
                generator = self.__generator_RGB_Depth(frames, align)

            if not generator is None:
                yield generator

    def set_mode(self, mode_camer:int):
        self.camera_modes.get(mode_camer, self.camera_modes[2])()
        self.current_mode_camer = mode_camer


if __name__ == '__main__':
    cam_1 = cameraRealSense('951422060620')

    cam_1.start_RS(3)

    cam_1.set_mode(1)
    print(cam_1.current_mode_camer)

    for count, (RGB, Depth) in enumerate(cam_1.getFrame_cam()):
        print("count-------------------", count)
        cv2.imshow("RGB", RGB)
        if not Depth is None:
            cv2.imshow("depth", Depth)

        if count % 4 == 0:
            cam_1.set_mode(1)
            print(cam_1.current_mode_camer)
            print("*"*20)

        if count % 8 == 0:
            cam_1.set_mode(2)
            print(cam_1.current_mode_camer)
            print("*" * 20)

        if count % 12 == 0:
            cam_1.set_mode(4)
            print(cam_1.current_mode_camer)
            print("*" * 20)

        q = cv2.waitKey(1)
        if q == 27:
            break