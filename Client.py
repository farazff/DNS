import socket

ClientSocket = socket.socket()
host = '8.8.8.8'
port = 53

ClientSocket.settimeout(30)
ClientSocket.connect((host, port))
ClientSocket.send(bytes("hello i am learning DNS!!!", 'utf-8'))
