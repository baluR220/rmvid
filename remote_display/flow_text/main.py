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
        self.speed_list = [50, 25, 10, 8, 5]
        self.text = control.options['TEXT']
        self.text_color = control.options['TEXT_COLOR']
        self.bg_color = control.options['BG_COLOR']
        self.geometry = control.options['POSITION']
        width, height = control.options['GEOMETRY'].split('x')
        self.width = int(width)
        self.height = int(height)
        direction = control.options['DIRECTION']
        self.font_family = control.options['FONT_FAMILY']
        self.font_size = int(self.height * 0.7)
        self.offset_y = -self.height * 0.08
        self.offset_x = 0
        self.speed = int(control.options['SPEED'])
        self.draw_widget()
        self.prepare_to_move(direction)
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
            highlightthickness=0, bg=self.bg_color
        )
        self.main_canvas.pack()
        self.main_text = self.main_canvas.create_text(
            self.offset_x, self.offset_y, anchor=NW, fill=self.text_color,
            text=self.text, font=(self.font_family, self.font_size)
        )

    def find_text_length(self):
        '''
        Find length of main_text whenever it s needed.
        '''
        bounds = self.main_canvas.bbox(self.main_text)
        length = bounds[2] - bounds[0]
        return length

    def prepare_to_move(self, direction):
        '''
        Place main_text accordingly to the direction
        '''
        length = self.find_text_length()
        if direction.lower() == 'right':
            self.direct = 1
            self.main_canvas.move(self.main_text, -length, 0)
        else:
            self.direct = -1
            self.main_canvas.move(self.main_text, self.width, 0)

    def move_widget(self):
        '''
        Moves a text alongside the length of a canvas.
        '''
        length = self.find_text_length()
        self.main_canvas.move(self.main_text, self.direct, 0)
        period = self.speed_list[self.speed - 1]
        if self.direct == -1:
            is_shown = self.main_canvas.coords(self.main_text)[0] > -length
            start_point = self.width + length
        elif self.direct == 1:
            is_shown = self.main_canvas.coords(self.main_text)[0] < self.width
            start_point = -(length + self.width)
        if is_shown:
            self.main_canvas.after(period, self.move_widget)
        else:
            self.main_canvas.move(self.main_text, start_point, 0)
            self.main_canvas.after(period, self.move_widget)

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
        color = color[0]
        if self.color_is_valid(color):
            if color == control.options['BG_COLOR']:
                return('bg_color is already %s' % color)
            else:
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
        color = color[0]
        if self.color_is_valid(color):
            if color == control.options['TEXT_COLOR']:
                return('text_color is already %s' % color)
            else:
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
        position = position[0]
        match = re.search(r'^(?:[-+][0-9]+){2}$', position)
        if match:
            if position == control.options['POSITION']:
                return('position is already %s' % position)
            else:
                self.root.geometry(position)
                self.root.update()
                control.save_to_config('POSITION', position)
                return('position changed to %s' % position)
        else:
            return('wrong position: %s' % position)

    def change_geometry(self, geometry):
        '''
        Chnage width and height of flow_text widget
        '''
        geometry = geometry[0]
        match = re.search(r'^[0-9]+x[0-9]+$', geometry)
        if match:
            if geometry == control.options['GEOMETRY']:
                return('geometry is already %s' % geometry)
            else:
                width, height = geometry.split('x')
                width = int(width)
                height = int(height)
                self.main_canvas.config(width=width, height=height)
                self.width = width
                font_size = int(height * 0.7)
                offset_y = -height * 0.08
                font = (control.options['FONT_FAMILY'], font_size)
                self.main_canvas.itemconfig(self.main_text, font=font)
                self.main_canvas.coords(self.main_text, (0, offset_y))
                self.root.update()
                control.save_to_config('GEOMETRY', geometry)
                return('geometry changed to %s' % geometry)
        else:
            return('wrong geometry: %s' % geometry)

    def change_speed(self, speed):
        '''
        Change speed of movemenet
        '''
        speed = speed[0]
        if speed.isdigit():
            if speed == control.options['SPEED']:
                return('speed is already %s' % speed)
            else:
                int_speed = int(speed)
                if int_speed in range(1, 6):
                    self.speed = int_speed
                    control.save_to_config('SPEED', speed)
                    return('speed changed to %s' % speed)
                else:
                    return('wrong speed: %s' % speed)
        else:
            return('wrong speed: %s' % speed)

    def change_direction(self, direction):
        '''
        Change direction of movement
        '''
        direction = direction[0]
        if direction in ['left', 'right']:
            if direction == control.options['DIRECTION']:
                return('direction is already %s' % direction)
            else:
                self.prepare_to_move(direction)
                control.save_to_config('DIRECTION', direction)
                return('direction changed to %s' % direction)
        else:
            return('wrong direction: %s' % direction)

    def change_text(self, text):
        '''
        Change text
        '''
        if text:
            text = ' '.join(text)
            self.main_canvas.itemconfig(self.main_text, text=text)
            self.root.update()
            control.save_to_config('TEXT', text)
            return('text changed to %s...' % text[:20])
        else:
            return('wrong text: %s' % text[:20])

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
        elif option.lower() == 'geometry':
            return self.change_geometry(value)
        elif option.lower() == 'direction':
            return self.change_direction(value)
        elif option.lower() == 'speed':
            return self.change_speed(value)
        elif option.lower() == 'text':
            return self.change_text(value)
        else:
            return 'unknown element passed the filter!'


class Control(Control_base):
    '''
    Class that handles commands from the control application.
    '''
    def handle_command(self, command):
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
                                command[0], command[2:]
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
