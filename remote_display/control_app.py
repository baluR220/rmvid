import socket
import sys
import os


try:
    work_dir = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(work_dir)
    from common.misc import check_python_version
except ImportError:
    print(traceback.format_exc())
    sys.exit()


def main():
    socket_file = 'flow_text/text.socket'
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


if __name__ == "__main__":
    check_python_version()
    main()
