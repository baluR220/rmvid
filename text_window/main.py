import sys
import os
import socket
import threading
from tkinter import *
from tkinter.ttk import *
from config import *
from time import sleep
import re


PYTHON_VERSION = sys.version.split(' ')[0]
WRONG_PYTHON_VERSION = "Python version should be 3.8 \
or newer. Your's is %s" % PYTHON_VERSION

assert sys.version_info >= (3, 8), WRONG_PYTHON_VERSION


class Flow_text():
    '''
    Flowing text widget.
    '''
    def __init__(self):
        self.text = TEXT
        self.text_color = TEXT_COLOR
        self.bg_color = BG_COLOR
        self.geometry = GEOMETRY
        self.width = int(WIDTH)
        self.height = int(HEIGHT)
        self.font_size = int(self.height * 0.7)
        self.font_family = FONT_FAMILY
        self.offset_y = -self.height * 0.08
        self.offset_x = 0

        self.draw_widget()
        self.move_widget()

    def draw_widget(self):
        '''
        Creates root window, draws canvas with rectangle and text.
        Rectangle acts as bacground color for text.
        '''
        self.root = Tk()
        self.root.overrideredirect(1)
        self.root.geometry(self.geometry)
        self.root.resizable(False, False)

        self.main_canvas = Canvas(
            self.root, width=self.width, height=self.height,
            highlightthickness=0
        )
        self.main_canvas.pack()
        self.bg = self.main_canvas.create_rectangle(
            self.offset_x, self.offset_y, self.width, self.height,
            fill=self.bg_color, outline=self.bg_color
        )

        self.main_text = self.main_canvas.create_text(
            self.offset_x, self.offset_y, anchor=NW, fill=self.text_color,
            text=self.text, font=(self.font_family, self.font_size)
        )
        self.root.update()

    def move_widget(self):
        '''
        Move text alohgside the length of canvas.
        '''
        bounds = self.main_canvas.bbox(self.main_text)
        length = bounds[2] - bounds[0]
        self.main_canvas.move(self.main_text, -1, 0)
        if self.main_canvas.coords(self.main_text)[0] > -length:
            self.main_canvas.after(10, self.move_widget)
        else:
            self.main_canvas.move(self.main_text, length + self.width, 0)
            self.main_canvas.after(10, self.move_widget)

    def change_bg(self, color):
        match = re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', color)
        if match:
            self.main_canvas.itemconfig(self.bg, fill=color)
            self.root.update()
            return('bg: color changed to %s' % color)
        else:
            return('bg: wrong color! %s' % color)


class Control():
    '''
    Class that handles commands from control application.
    '''
    def __init__(self, widget):
        self.widget = widget

    def handle_command(self, command: str) -> str:
        '''
        Determine what command to execute. Always return string
        that will be sent to control application.
        '''
        command = command.split()
        if command[0] == 'bg':
            return self.widget.change_bg(command[1])
        else:
            return('done')


def socket_thread():
    '''
    Function to create socket and establish connection to the
    control application. Called in new thread.
    '''
    socket_file = './socket'
    if os.path.exists(socket_file):
        os.remove(socket_file)
    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    server.bind(socket_file)
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
            data = control.handle_command(data)
            conn.send(data.encode('utf-8'))
    socket_thread()


def gui_thread():
    '''
    Function to create gui-like window with visual information.
    Called in new thread.
    '''
    global control
    flow_text = Flow_text()
    control = Control(flow_text)
    flow_text.root.mainloop()


if __name__ == '__main__':
    threading.Thread(target=gui_thread, daemon=True).start()
    threading.Thread(target=socket_thread).start()
