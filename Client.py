import socket

ClientSocket = socket.socket()
host = 'localhost'
port = 9999

ClientSocket.settimeout(30)
ClientSocket.connect((host, port))
ClientSocket.send(bytes("hello i am learning DNS!!!", 'utf-8'))
