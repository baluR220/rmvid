'''
Classes and functions which are common for widgets.
'''
import sys
import os
import socket
import threading


class Control_base():
    '''
    Class that creates threads and an interface for a control application.
    '''
    def __init__(self, widget_class, name, socket_file, config_file):
        self.widget_constructor = widget_class
        self.widget_name = name
        self.socket_file = socket_file
        self.config_file = config_file
        self.read_config()

    def handle_command(self, data):
        return data

    def read_config(self):
        with open(self.config_file) as config:
            self.options = {}
            for line in config:
                line = line.strip()
                if not(line.startswith('#') or line == ''):
                    key, val = line.split('=')
                    self.options[key.strip()] = val.strip()

    def save_to_config(self, option, value):
        with open(self.config_file, 'r+') as config:
            out = []
            for line in config:
                if line.startswith(option):
                    line = '%s = %s\n' % (option, value)
                out.append(line)
            config.seek(0)
            for line in out:
                config.write(line)

    def socket_thread(self):
        '''
        The function to create a socket and establish a connection to the
        control application. Called in a new thread.
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
            if data == 'stop':
                conn.send(('stopping %s' % self.widget_name).encode('utf-8'))
                server.close()
                os.remove(self.socket_file)
                sys.exit()
            else:
                data = self.handle_command(data)
                conn.send(data.encode('utf-8'))
                conn.close()
                break
        self.socket_thread()

    def gui_thread(self):
        '''
        The function to create a gui-like window with visual information.
        Called in a new thread.
        '''
        self.widget = self.widget_constructor()
        self.widget.root.mainloop()

    def launch_threads(self):
        '''
        The function to launch one thread with a tk mainloop
        and other with a socket.
        '''
        threading.Thread(target=self.gui_thread, daemon=True).start()
        threading.Thread(target=self.socket_thread).start()
