import socket
import sys


socket_file = './socket'
try:
    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    client.settimeout(5)
    client.connect(socket_file)
except Exception:
    print('widget is not running')
    sys.exit()
while True:
    data = input('> ')
    try:
        client.send(data.encode('utf-8'))
    except Exception:
        print('widget is not reachable', end='')
    if data == 'exit':
        client.close()
        break
    else:
        data = client.recv(1024).decode('utf-8')
        print(data)
