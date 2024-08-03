#!/usr/bin/python3.12

from socket import *
import os

SERVER_NAME = "localhost"
SERVER_PORT = 3000

serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(("", SERVER_PORT))
serverSocket.listen(10)


def parse_http(message: str) -> dict:
    environment = {}
    message_sections = message.splitlines()
    method, path, http_version = message_sections.pop(0).split(" ")

    environment["Method"] = method
    environment["Path"] = path
    environment["Http_Version"] = http_version

    for message_section in message_sections:
        if message_section != "":
            header_name, header_value = message_section.split(":", 1)
            environment[header_name] = header_value

    return environment


while True:
    connectionSocket, clientAddr = serverSocket.accept()

    try:
        req = parse_http(connectionSocket.recv(2048).decode())

        if req.get("Path").replace("/", "") == "":
            file_name = "index.html"
        else:
            file_name: str = req.get("Path").replace("/", "")

        file = open(file_name, "rb")
        file_data = file.read()
        mimetype = file_name.split(".")[1]
        response = f"HTTP/1.1 200 OK\nConnection: close\nContent-Type: text/{mimetype}\nContent-Length: {os.path.getsize(file_name)}\n\n"
        connectionSocket.send(response.encode())
        connectionSocket.send(file_data)
        file.close()
    except FileNotFoundError:
        response = "HTTP/1.1 404 Not Found"
        connectionSocket.send(response.encode())
    except Exception:
        response = "HTTP/1.1 500 Internal Server Error"
        connectionSocket.send(response.encode())
    finally:
        connectionSocket.close()
