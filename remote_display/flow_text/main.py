import sys
import os
from tkinter import *
from tkinter.ttk import *
from config import *
import re
import traceback


try:
    work_dir = os.path.dirname(os.path.realpath(__file__))
    import_path = os.path.dirname(work_dir)
    sys.path.append(import_path)
    from common.widget import Control_base
    from common.config import COLORS
    from common.misc import check_python_version
except ImportError:
    print(traceback.format_exc())
    sys.exit()


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
        Creates a root window, draws a canvas with a rectangle and a text.
        The rectangle acts as a background color for the text.
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
        Moves a text alongside the length of a canvas.
        '''
        bounds = self.main_canvas.bbox(self.main_text)
        length = bounds[2] - bounds[0]
        self.main_canvas.move(self.main_text, -1, 0)
        if self.main_canvas.coords(self.main_text)[0] > -length:
            self.main_canvas.after(10, self.move_widget)
        else:
            self.main_canvas.move(self.main_text, length + self.width, 0)
            self.main_canvas.after(10, self.move_widget)

    def color_is_valid(self, color):
        color_valid = color in COLORS
        match = re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', color)
        return color_valid or match

    def change_bg(self, color):
        if self.color_is_valid(color):
            self.main_canvas.itemconfig(self.bg, fill=color)
            self.root.update()
            return('bg color changed to %s' % color)
        else:
            return('bg wrong color: %s' % color)


class Control(Control_base):
    '''
    Class that handles commands from the control application.
    '''
    def handle_command(self, command: str) -> str:
        '''
        Determines which command to execute. Always returns a string
        that is sent to the control application.
        '''
        command = command.split()
        if len(command) > 1:
            if command[0] == 'bg_color':
                return self.widget.change_bg(command[1])
            else:
                return('element unknown')
        else:
            return ('Command unknown')


if __name__ == '__main__':
    check_python_version()
    socket_file = os.path.join(work_dir, 'text.socket')
    control = Control(Flow_text, 'flow_text', socket_file)
    control.launch_threads()
