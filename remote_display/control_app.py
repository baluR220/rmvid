import socket
import sys
import os
import traceback


try:
    work_dir = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(work_dir)
    from common.misc import check_python_version
except ImportError:
    print(traceback.format_exc())
    sys.exit()


usage = '''
Usage: <widget> <element> <set> <value>
       <widget> <element> <get>
       <widget> <command>
       help
       exit
'''
widgets = ['flow_text', 'video_player', 'slide_show', 'html_browser']


def connection(socket_file):
    try:
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.settimeout(5)
        client.connect(socket_file)
    except Exception:
        return 0
    else:
        return client


def send_command(conn, command):
    try:
        command = ' '.join(command)
        conn.send(command.encode('utf-8'))
    except Exception:
        return 0
    else:
        data = conn.recv(1024).decode('utf-8')
        conn.close()
        return data


def main():
    while True:
        data = input('> ').split()
        if data:
            if data[0] == 'exit':
                break
            elif data[0] == 'help':
                print(usage)
            else:
                if data[0] in widgets:
                    widget = data[0]
                    if len(data) > 1:
                        socket_file = os.path.join(
                            work_dir, '%s/socket.socket' % widget
                        )
                        conn = connection(socket_file)
                        if conn:
                            response = send_command(conn, data[1:])
                            if response:
                                print(response)
                            else:
                                print('%s is not reachable' % widget)
                        else:
                            print('%s is not running.' % widget)
                    else:
                        print('not enough arguments. try "help"')
                else:
                    print('wrong widget name: %s' % data[0])
        else:
            continue


if __name__ == "__main__":
    check_python_version()
    main()
