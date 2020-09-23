import os
import socket
import io
import threading
import zipfile

class get_data_server(threading.Thread):

    def __init__(self, IP, PORT):
        super().__init__()
        self.ip = IP
        self.post = PORT


    def __connect(self):
        '''
        Подключаемся для получения данных
        :return:
        '''
        sock = socket.socket()
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.connect((self.ip, self.post))
        return sock

    def get_file(self, path_save):
        '''
        Получаем данные и складываем куда надо
        :param path_save:
        :return:
        '''
        sock = self.__connect()
        pp = open(path_save, 'wb')

        buf = memoryview(bytearray(1024*1024*10))
        nbytes = 1

        while nbytes:
            toread = 1024*1024*10
            view = buf[:]
            while toread:
               nbytes = sock.recv_into(view, toread)
               view = view[nbytes:]
               toread -= nbytes
               if nbytes == 0:
                    buf=buf[:-toread]
                    break

            pp.write(buf)
        print('.', end='')
        sock.close()
        return 0

    def set_path_save(self, path_save):
        print("path_save", path_save)
        self.path_save = path_save

    def run(self):
        self.get_file(self.path_save)

    def unpack(self, path_zip_file, path_save):
        '''
        распаковывает zip вайл
        :param path_zip_file:
        :param path_save:
        :return:
        '''
        if zipfile.is_zipfile(path_zip_file):
            z = zipfile.ZipFile(path_zip_file, 'r')
            z.extractall(path_save)

if __name__ == '__main__':
    ip = '192.168.1.69'
    port = 9000
    test_data_server = get_data_server(ip, port)

    #test_data_server.get_file("test.zip")
    test_data_server.unpack('/home/dima/PycharmProjects/face_id_jetsonNano/app_faceId_jetsonNano/data/temp/1.zip', '/home/dima/PycharmProjects/face_id_jetsonNano/app_faceId_jetsonNano/data/classificators/2')
