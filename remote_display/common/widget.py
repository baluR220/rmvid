'''
Classes and functions common for widgets.
'''
import sys
import os
import socket
import threading


class Control():
    '''
    Class that creates threads and handles commands
    from control application.
    '''
    def __init__(self, widget_class, socket_file):
        self.widget_constructor = widget_class
        self.socket_file = socket_file

    def handle_command(self, command: str) -> str:
        '''
        Determine what command to execute. Always return string
        that will be sent to control application.
        '''
        command = command.split()
        if command[0] == 'bg' and len(command) == 2:
            return self.widget.change_bg(command[1])
        else:
            return('command unknown')

    def socket_thread(self):
        '''
        Function to create socket and establish connection to the
        control application. Called in new thread.
        '''
        if os.path.exists(self.socket_file):
            os.remove(self.socket_file)
        server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        server.bind(self.socket_file)
        server.listen(1)
        conn, addr = server.accept()
        while True:
            data = conn.recv(1024).decode('utf-8')
            if data == 'exit':
                conn.close()
                break
            elif data == 'stop':
                conn.send('stoping widget'.encode('utf-8'))
                sys.exit()
            else:
                data = self.handle_command(data)
                conn.send(data.encode('utf-8'))
        socket_thread()

    def gui_thread(self):
        '''
        Function to create gui-like window with visual information.
        Called in new thread.
        '''
        self.widget = self.widget_constructor()
        self.widget.root.mainloop()

    def launch_threads(self):
        '''
        Launch one thread with tk mainloop and other with socket.
        '''
        threading.Thread(target=self.gui_thread, daemon=True).start()
        threading.Thread(target=self.socket_thread).start()
