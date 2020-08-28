import sys
import os
from tkinter import *
from tkinter.ttk import *
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
        self.text = control.options['TEXT']
        self.text_color = control.options['TEXT_COLOR']
        self.bg_color = control.options['BG_COLOR']
        self.geometry = control.options['POSITION']
        width, height = control.options['GEOMETRY'].split('x')
        self.width = int(width)
        self.height = int(height)
        self.font_family = control.options['FONT_FAMILY']
        self.font_size = int(self.height * 0.7)
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
            self.offset_x - 1, self.offset_y, self.width + 1, self.height,
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
        '''
        Check if color is in COLORS list or looks like #ffffff
        '''
        color_valid = color in COLORS
        match = re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', color)
        return color_valid or match

    def change_bg_color(self, color):
        '''
        Change background color
        '''
        if self.color_is_valid(color):
            self.main_canvas.itemconfig(self.bg, fill=color)
            self.main_canvas.config(bg=color)
            self.root.update()
            control.save_to_config('BG_COLOR', color)
            return('bg_color changed to %s' % color)
        else:
            return('wrong bg_color: %s' % color)

    def change_text_color(self, color):
        '''
        Change text color
        '''
        if self.color_is_valid(color):
            self.main_canvas.itemconfig(self.main_text, fill=color)
            self.root.update()
            control.save_to_config('TEXT_COLOR', color)
            return('text_color changed to %s' % color)
        else:
            return('wrong text_color: %s' % color)

    def change_position(self, position):
        '''
        change position, vaild position looks like '+50+50'
        which means the offset from left upper corner of display
        '''
        match = re.search(r'^(?:[-+][0-9]+){2}$', position)
        if match:
            self.root.geometry(position)
            self.root.update()
            control.save_to_config('POSITION', position)
            return('position changed to %s' % position)
        else:
            return('wrong position: %s' % position)

    def change_geometry(self):
        pass

    def change_speed(self):
        pass

    def change_direction(self):
        pass

    def get_option(self, option):
        '''
        Return current value of option
        '''
        return control.options[option.upper()]

    def set_option(self, option, value):
        '''
        Set value of option
        '''
        if option.lower() == 'bg_color':
            return self.change_bg_color(value)
        elif option.lower() == 'text_color':
            return self.change_text_color(value)
        elif option.lower() == 'position':
            return self.change_position(value)
        else:
            return 'unknown element passed the filter!'


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
            if command[0].upper() in self.options:
                if len(command[1:]) > 1:
                    if command[1] == 'set':
                        if len(command[2:]) > 0:
                            return self.widget.set_option(
                                command[0], command[2]
                            )
                        else:
                            return ('more arguments needed')
                    else:
                        return ('Command unknown')
                elif command[1] == 'get':
                    return self.widget.get_option(command[0])
                else:
                    return ('more arguments needed')
            else:
                return('element unknown')
        else:
            return ('Command unknown')


if __name__ == '__main__':
    check_python_version()
    socket_file = os.path.join(work_dir, 'socket.socket')
    config_file = os.path.join(work_dir, 'config')
    control = Control(Flow_text, 'flow_text', socket_file, config_file)
    control.launch_threads()
