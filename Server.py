import socket

s = socket.socket()
print("Socket created")

s.bind(('localhost', 9999))

s.listen(3)
print('Waiting for connections')

# while True:
c, addr = s.accept()
print('Connected with ', addr)
print('received = ', c.recv(1024).decode())
c.close()
