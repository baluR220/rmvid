import os
import subprocess
import sys
from datetime import datetime
from tkinter import *
from tkinter.ttk import *
import hashlib
import ctypes
from idlelib.tooltip import Hovertip
import sqlite3
from re import fullmatch
import traceback
from time import sleep
import threading


def nostart(text):
	'''
	Create error window if there is some problem with config 
	and don't start main program

	in: text to show in error window
	out: error window and no main program launch
	'''
	nostart = Tk()
	nostart.title('Error')
	position_x = int(nostart.winfo_screenwidth()/2 - nostart.winfo_reqwidth()/2)
	position_y = int(nostart.winfo_screenheight()/2 - nostart.winfo_reqheight()/2)
	nostart.geometry("+%d+%d" % (position_x, position_y))
	nostart.resizable(False, False)
	nostart_label = Label(nostart, text=text, font=(None, 10), wraplength=500)
	nostart_label.pack(padx=20, pady=10)
	nostart_button = Button(nostart, text='OK', width=10, command=sys.exit)
	nostart_button.pack(pady=10)
	nostart.mainloop()

#define platform specific names
_platform = sys.builtin_module_names
if 'posix' in _platform:
	nostart('Wrong platform. Choose client for Linux')
elif 'nt' in _platform:
	slash = '\\' 
	config = 'config'
	platform = 'nt'
	interpreter = 'python'
#magic from C to make tray icon specific
	myappid = 'rmvid-client'
	ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
else:
	nostart('Sorry, OS not recognized.')
	
#get config, parse it
work_dir = os.path.dirname(os.path.realpath(__file__)) + slash
path_to_config = work_dir + config

if not os.path.exists(path_to_config):
	nostart('Config not found. Run config_make first')
	
def load_config():
	global options
	with open(path_to_config) as config:
		options = {}
		for line in config:
			line = line.strip()
			if not(line.startswith('#') or  line == '') :
				key, val = line.split('=')
				options[key] = val

load_config()
#get options from config
try:
	path_to_log = options['path_to_log']
	path_to_client = options['path_to_client']
	path_to_content = options['path_to_content']
	path_to_tools = options['path_to_tools']
	path_to_groups = options['path_to_groups']
	client_address = options['address']
	video_quality = options['video_quality']
except Exception as error:
	nostart('Config is incomplete: %s' % error)

source = ['rmvid']
path_to_db = path_to_groups + 'rmvid.db'
path_to_player = path_to_tools + 'player.py'
path_to_converter = path_to_tools + 'converter.py'

#icons base64
main_logo = b'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAAdgAAA\
HYBTnsmCAAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAFkSURBVDiNzVI9S4JRFH7uua9viqIigqkY1GQNE\
YkRjdHa2NavKMKG5qZo8C8E/YGW1sbKhlIQCoQISnAQxM/3454G09fKG7X1TJd7zvMB5xEAUvm13fO5+TylzYv06UGuAR2Y5dFJa\
bHS2nqqv1WTpZuzVQPAIBbPZElQwlXoCWBBKwCBvgUlpW+FWbgADAIw8PsjSk+aIkMSQgzfBoBYo1EzZ5NZVOux/vZeuaWnsmCOh\
30Rx8/sCQAAlOuAVZv8ppJaZ8Gi2+2Qcp3xnzExxVLGMouFXEQfANg/vlWPXU+AvCHrk39L4tHoh71f4T8JjA77R4yvYEgT1RfT2\
jm870xb3NxYb909lEP1RiAqw2R+EhiZCxlky25PbeXl1XUIEELIEEvyqjJOQCSRTTVnioVcVJv3owfPrjE2JWBYAVc5Wt5XKFaYr\
LLt2L2KNeiYLqk4Q7zqqSyDAbnsNu0aESUA2O9PS32QRfLf5QAAAABJRU5ErkJggg=='
warning_logo = b'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAAbw\
AAAG8B8aLcQwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAITSURBVDiNfVNNaBNREP7mdXeTpiFJpYnSf2n\
TJlYRKdUoWhrUJEpaqtU1jSJsSAWhFC89N8WTlxRPgr140pMH8SIiRKQHsSDUkxT8B7Hpn0i0yiY7HlIky2598B7MN998M2/eGzAz\
dtrDV6+1Hxk60/o/joDNIiIau5yZb5T0T82N/OX4ydg8EZEdV7IDx9KZiX0dyE5fFJCpGbfuFbPEsUUAdy3JmNkEnNM0n2LQcn6izt\
/SVMVK67+RzK2sUlnvKRQK32v5liuIP5hJ9JO/pQl4/obxaOEX3Luc0Aadfh3KjIVfa1xIayGvmybVwSr8+CXj4YsSQEA65oXXhclj0\
XhoRwEWYi41JKQGp7UvsseJG/F6SRDmbAXOX8kkOwNInD5k22yAgFNHPegOUOJENJ40CaiqqhAjn4kT7B9rW8PtwPRZFwzB+f2qqvwTK\
MvuqUiYgn0d5ugDe4GDXYqpir5wA6JBKehb35wCABoZz+52yZXl29frPAGfOSNvH6aqGCi+3cD4ndKPn0alR8hUzg1HyBIMAE8WGQ+\
elSy9CLS6kBqQPVJF5AQTjY5EbH80OvcAve2y1eF24NKADBCNCjCWPnxjKwlAuI3Q3+uwOvQK3q8aIPCSxEyzN+9XukNtokuxmYzNjT\
WT7ZSArZKO1x/1d4bgWWLm6vSltMMkcX0t2TAEFb9+tpZHYmuh8PQVM/NfKfHCdnYDhr4AAAAASUVORK5CYII='
reload_logo = b'iVBORw0KGgoAAAANSUhEUgAAABAAAAARCAYAAADUryzEAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAGXRFWHRTb2Z\
0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAAdJJREFUeNpi+P//PwMuDAQBQNwAxAI41RAw4AAQgxgfgDiBaAOgNi8AacxPDXkBwlC\
DHqAbhK7RAKSIl5fnW3Zi8CNpaek3HeXRD97O5Px/c7rO/8Ro/9dQgxbA9DAxQAEjIyPI1vPFGWG8hzr0OEUF2Dnfvn3LAZN//VuS4c6\
D5zDuAxgDZrMAExPTxwnV0R/mNEW9g9kCUhjo6/raz9sZ5gVQmChgeAGkGKRoe7//V6jCBLRABNEOOAMRFFiru0K/qagog0K7AS1MArA\
EsgASm0EAZMv5qVb/obYJEIjaBqi6CbBABNnC8PUvNyxMPjDgAcCwKlzXHQxi5gMD3oAJqAHkPwZu5q+w2FDApRkk9+/fPz5Frucwyy7A\
ovHhna/S34EB+RLkNDwOmABSA1IL0oMcjQ2gADwyyRUWDg24/A5SgxzY8FAFxTkwEb0FRSU/P993aGJZAEsPIDGQHEgNkH8BFtiMsKgAB\
wgT00FrS5NfNaESIp9+sX+/+5btFUhOWfiXGB/bT86W1S/eHD1+hg0YDvYg/4P1wQyAGiIADYN4c1PDlyY6Sr9A4meu3GM7efq8OJC5EI\
gLkGMKxQDk0IbmSAGktH8AqPYBulqAAAMAnFCcu6uk/bkAAAAASUVORK5CYII='
trash_logo = b'iVBORw0KGgoAAAANSUhEUgAAABAAAAARCAYAAADUryzEAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAGXRFWHRTb2Z0d2\
FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAAUtJREFUeNpi/P//PwM6YGRknACkDNCELwDVFmCoRTcAqNkBSO3fOcGPgZvpO1js6z9OBve\
CTSCmI1D9AWT1TAxUAA+A+D+Z+AHYC0BnN3i42BUvDT3NQ4yN0atNv+zYc6gXqLcB5oUPf/7+/QNTcP2nDYYmZDGo2g/IYXBhz/6jAjAF\
MX23wPSbf8pgjCwGAlC1F1AMABHfGUQggfLgIZje+1wfjJHFYGpQDAD6BeycBz81CIc4VA1MD3I0Hrz0RuwfIQOgag5iSwcfXn3+/4uQAV\
A1H7AZcOHE5Sd/CBkAVXMBmwEP3r7/RDAMoGqwG3D67AVwQspPDQELSPD+AGNkMaiaD1gzEzBF/j8/1YpBjuU8Vtsf/TFkMMw+BooBRpgY\
C5qaj937BTjUZAP/YzPg1uMPII0/cGZnoAtAZUAAgWDYANQDDwOAAAMAlIyxW6CV9mkAAAAASUVORK5CYII='
play_logo = b'iVBORw0KGgoAAAANSUhEUgAAABAAAAARCAYAAADUryzEAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAGXRFWHRTb2Z0d2Fy\
ZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAAUhJREFUeNpi+P//PwMIA4ECEBfA+MRimGYDIP4PxRdAfGINYGKAAIEgPzeGlzOFfsxtigK55D\
wjI2MDAxEAZgADPy8nAwvDd44A8fX8t6drvQEaWA805AIQGxBlADIQYrovMtv7MAPUNQeAhhSQZAAMgFxzfprlb2cH636gISCDFEgyAATk\
mC+ILI+88q2vKsYcFMDormEiJqCYGX5xxcuv5UByzQKSDEB2TayL3EtomiHdgP0fvd80zTshDgpYmBgLMRq/MYh+rDtkyD9/6ZqvQG4oMAE\
Rb8Cpb27vsidfErp3b+NEILcBqPkDsjxOA/4wcP7oOu/yr3fGKmYg1xHZVoIGXP9p8yZuwh2Re/dWbQRyE9BtxWrAo6dvGG7+snqx9qowH9\
BWVqBQIFDjBoIBhJQbP0BzI0iTAEnZGWqIACnZGIYBAgwARIAF66tJymgAAAAASUVORK5CYII='
add_logo = b'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAQAAAC1+jfqAAAABGdBTUEAALGPC/xhBQAAACBjSFJNAAB6JgAAgIQAAPoAAA\
CA6AAAdTAAAOpgAAA6mAAAF3CculE8AAAAAmJLR0QAAKqNIzIAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAAHdElNRQfkAR0KJi1VhA9BAAAAck\
lEQVQoz72RQQqAIBBFX1LHyMO0KGjTOdx0tzZBnSQ9SRA0bUQUzE3QG/igPPgwAzEah6PlFYMgmPhLJUITZVbI8F2o0fRB63ye/n2zg0MKYx\
VSbJCKliFUjEzAwhoqttSfEYT55z2kwhVlFo3lSM/9AH/RJPcXeIy8AAAAJXRFWHRkYXRlOmNyZWF0ZQAyMDIwLTAxLTI5VDEwOjM4OjQ1Kz\
AwOjAwE3GebQAAACV0RVh0ZGF0ZTptb2RpZnkAMjAyMC0wMS0yOVQxMDozODo0NSswMDowMGIsJtEAAAAZdEVYdFNvZnR3YXJlAHd3dy5pbmt\
zY2FwZS5vcmeb7jwaAAAAAElFTkSuQmCC'
freeze_logo = b'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAQAAAC1+jfqAAAABGdBTUEAALGPC/xhBQAAACBjSFJNAAB6JgAAgIQAAPoAA\
ACA6AAAdTAAAOpgAAA6mAAAF3CculE8AAAAAmJLR0QAAKqNIzIAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAAHdElNRQfkARwOLjPY53eTAAAA2k\
lEQVQoz33RvUpDMQCG4aflgEUo9SA46NLGQVd3rWNvwQsQB5eKF6K9CO9BHHVQUBycdOmo4FYnrX9xOKectKJflpfkI3mTUGVFdFvyhugM6klh\
G+eznBa6SaGLCzO5920R1Dx71YAMB+aQWfNiF7QsedI3NoCR+McYFVu3BcGJaF8QBKeiHUE7NbgTLZf8aGx+WjD35aHkdbG6QYYFNT1113LQw\
42cicW/khkGGvbkjr2DQxyBt8lBTR+GJa+Kriq54qk3Zb9/IS2kk1vThSKXok7JQ59a1dIP/0pNkQtAWPgAAAAldEVYdGRhdGU6Y3JlYXRlAD\
IwMjAtMDEtMjhUMTQ6NDY6NTErMDA6MDByt2TXAAAAJXRFWHRkYXRlOm1vZGlmeQAyMDIwLTAxLTI4VDE0OjQ2OjUxKzAwOjAwA+rcawAAABl0\
RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAAASUVORK5CYII='

def print_to_log(data):
	'''
	Print info to log file named with today date; 
	write info with time and source of event
	
	in: data to write to log file
	out: note in log file with today's date
	'''
	date = path_to_log + datetime.today().strftime('%Y.%m.%d')
	time = datetime.today().strftime('[%H:%M:%S]')
	with open(date, 'a')as output:
		print(time, source, data, file=output)

def get_list_content(address, secret):
	'''
	Ask remote player for current playlist, also used to check if player is online (like ping)
	
	in: address of remote machine, secret
	out: playlist as list type
	'''
	secret = secret.get()
	p = subprocess.check_output([interpreter, path_to_client, address, secret,\
								 "get_list_content"], stdin=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True, creationflags=subprocess.CREATE_NO_WINDOW)
	p = p.decode('utf-8').split(' ')
	if p[0] == 'None':
		p = []
	return(p)

#operations on update content
def transfer_file(address, secret, files):
	'''
	transfer files to temp folder on remote player for next refresh
	files transfers through the same socket as the commands via client.py
	input file is read in chunks of 1024 bytes, then send, then checksum checked
	and chunk repeated if necessary(there is no repeats in good connection).
	There is final check after whole file is transfered
	do NOT call this function directly, only as part of update_content function or if you
	understand what you are doing

	in: address of remote machine, secret, list of files to transfer
	out: send files and return message on complete
	'''
	put_message('\ttransfer started...')
	secret = secret.get()
	with subprocess.Popen([interpreter, path_to_client, address, secret,\
								 "send_file"] + files, close_fds=True, creationflags=subprocess.CREATE_NO_WINDOW,\
								  stdout=subprocess.PIPE, bufsize=1, universal_newlines=True) as p:
		for line in p.stdout:
			put_message('\t%s' % line.strip())
	if p.returncode != 0:
		raise subprocess.CalledProcessError(p.returncode, p.args)

	p = subprocess.check_output([interpreter, path_to_client, address, secret,\
								 "get_list_temp"],close_fds=True, stdin=subprocess.PIPE, stderr=subprocess.PIPE,  creationflags=subprocess.CREATE_NO_WINDOW)
	p = p.decode('utf-8').split(' ')
	list_temp = {}
	for i in p:
		i = i.split('|')
		list_temp[i[0]] = i[1]
	repeat_send = []
	for file in files:
		if os.path.getsize(path_to_content + file) != int(list_temp[file]):
			repeat_send.append(file)
	if not repeat_send:
		return('files transfered')
	else:
		return('files were damaged ', repeat_send)
	del p 
	del repeat_send
	del list_temp

def remove_file(address, secret, files):
	'''
	remove files from content folder on remote player,
	use only as part of update_content after stop_player or player can close with error
	you can use it directly if you understand what you are doing
	
	in: address of remote machine, secret, list of files to remove
	out: delete files and return message on complete
	'''
	secret = secret.get()
	commands = 'remove_file'
	for i in files:
		commands += ' '+ i
	p = subprocess.check_output([interpreter, path_to_client, address, secret, commands],close_fds=True, stdin=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW)
	p = p.decode('utf-8')
	return(p)
	del commands
	del p

def stop_player(address, secret):
	'''
	stop remote player by killing player process

	in: address of remote machine, secret
	out: stop player and return message on complete
	'''
	secret = secret.get()
	p = subprocess.check_output([interpreter, path_to_client, address, secret, 'stop_player'],close_fds=True, stdin=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW)
	p = p.decode('utf-8')
	put_message('\t%s' % p)
	del p

def start_player(address, secret):
	'''
	start remote player, there is a delay for start_player to let player finish stopping

	in: address of remote machine, secret
	out: start player and return message on complete
	'''
	sleep(2)
	secret = secret.get()
	p = subprocess.check_output([interpreter, path_to_client, address, secret, 'start_player'],close_fds=True, stdin=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW)
	p = p.decode('utf-8')
	put_message('\t%s' % p)
	del p

def refresh_content(address, secret,):
	'''
	move files from temp to content folder on remote player
	do NOT call this function directly, only as part of update_content function or if you
	understand what you are doing

	in: address of remote machine, secret
	out: refresh content and return message on complete
	'''
	secret = secret.get()
	p = subprocess.check_output([interpreter, path_to_client, address, secret, 'refresh_content'],close_fds=True, stdin=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW)
	p = p.decode('utf-8')
	return(p)

def update_content(address, secret, upload_queue, delete_queue):
	'''
	update content on remote player which include
		- trfansfer files if there is some new files
		- stop player
		- delete old unnecessary files
		- move new files from temp folder to content folder 
		-start player
	transfer is made while player running, player then stops to delete files and refresh content
	then player starts
	If there is nothing to send and nothing to delete then player won't be stopped
	and 'content is up-to-date' message is shown

	in: address of remote machine, secret, list of files to upload, list of files to delete
	out: update content and return message on complete
	'''
	if (not upload_queue) and (not delete_queue):
		put_message('\tcontent is up-to-date')
	else:
		if upload_queue:
			transfer = transfer_file(address, secret, upload_queue)
			print_to_log(transfer)
			put_message('\t%s' % transfer)
		if delete_queue:
			stop_player(address, secret)
			remove = remove_file(address, secret, delete_queue)
			put_message('\t%s' % remove)
		else:
			stop_player(address, secret,)
		if upload_queue:
			refresh = refresh_content(address, secret)
			put_message('\t%s' % refresh)
		start_player(address, secret,)
	
#operations on GUI and other local stuff
def center_window(name, parent=None):
	'''
	center window either on the screen or relative to the parent element

	in: window name and (optionally) parent name
	out: center passed window
	'''
	name.update()
	if parent:
		position_x = int(parent.winfo_x() + parent.winfo_width()/2 - name.winfo_reqwidth()/2)
		position_y = int(parent.winfo_y() + parent.winfo_height()/2 - name.winfo_reqheight()/2)
	else:
		position_x = int(name.winfo_screenwidth()/2 - name.winfo_reqwidth()/2)
		position_y = int(name.winfo_screenheight()/2 - name.winfo_reqheight()/2)
	name.geometry("+%d+%d" % (position_x, position_y))

def get_info_db(sql, val=()):
	'''
	get information from database with passed sql query and (optionally) additional values

	in: sql with (optionally) additional values
	out: information from database
	'''
	conn = sqlite3.connect(path_to_db)
	cursor = conn.cursor()
	cursor.execute(sql, val)
	out = cursor.fetchall()
	cursor.close()
	return out
def pure(data):
	'''
	convert data from any iterable type into list

	in: data of iterable type
	out: list
	'''
	out = []
	for elem in data:
		for i in elem:
			out.append(i)
	return out
class Work_field():
	'''
	common class for work field, creates label and frame with listbox and scroll,
	warning window, list of currently chosen items, reload and delete buttons
	'''
	def __init__(self, name, x, y):
		'''
		work field constructor to create label and field with listbox and scroll, reload and delete buttons.
		NOT for direct use, used only in subclasses

		in: name of subclass, coordinates of upper left corner of label
		out: creates label and field with listbox and scroll, reload and delete buttons.
		'''
		self.chosen_items = []
		self.label = Label(main_canvas, text=name.title(), font=(None, 14))
		self.browser = Frame(main_canvas, style='WF.TFrame')
		self.scrollbar = Scrollbar(self.browser)
		self.show = Listbox(self.browser, width=50, highlightthickness=0, bd=0, exportselection=0, yscrollcommand=self.scrollbar.set, selectmode=MULTIPLE)
		main_canvas.create_window(x, y, anchor=NW, window=self.label, tag=self)
		main_canvas.create_window(x, y+30, anchor=NW, width=200, height=350, window=self.browser, tag=self)
		self.scrollbar.pack(side=RIGHT, fill=Y, padx=2, pady=2)
		self.show.pack(side=LEFT, fill=BOTH, padx=10, pady=5)
		self.scrollbar.config(command=self.show.yview)
		self.show.bind('<<ListboxSelect>>', self.make_chosen_list)
		self.reload_logo = PhotoImage(data=reload_logo)
		self.reload_button = Button(main_canvas, image=self.reload_logo, command=self.reload)
		Hovertip(self.reload_button, 'Refresh list')
		main_canvas.create_window(x+225, y+140, anchor=NE, window=self.reload_button, tag=self)
		self.trash_logo = PhotoImage(data=trash_logo)
		self.delete_button = Button(main_canvas, image=self.trash_logo, state=DISABLED, command=self.delete_item)
		Hovertip(self.delete_button, 'Delete chosen items')
		main_canvas.create_window(x+225, y+201, anchor=NE, window=self.delete_button, tag=self)

	def make_chosen_list(self, event):
		'''
		make list of currently chosen items in listbox on every new selection event

		in: event of new selection in listbox
		out: list of currently chosen items saved in attribute
		'''
		self.chosen_items = ([self.show.get(id) for id in self.show.curselection()])

	def warning_window(self):
		'''
		create warning window for any purpose, text to label added further when function is called,
		when 'ok' is pressed confirm_operation is called.
		while warning window exists root window is locked
		NOT for using directly, use it only in throw_warning wrapper function
		
		in: self
		out: new warning window
		'''
		self.warning = Toplevel(root)
		self.warning.title('Warning')
		self.warning_logo = PhotoImage(data=warning_logo)	
		self.warning.tk.call('wm', 'iconphoto', self.warning._w, self.warning_logo)
		self.warning.resizable(False, False)
		self.warning.grab_set()
		self.warning.focus_set()
		self.warning_frame = Frame(self.warning)
		self.warning_frame.pack(padx=50)
		self.warning_text = Label(self.warning_frame, font=(None, 10), wraplength=500)
		self.warning_text.pack(padx=20, pady=10)
		self.warning_confirm = False
		self.warning_button = Button(self.warning_frame, text='OK', width=10, command=self.confirm_operation)
		self.warning_button.pack(pady=10)

	def confirm_operation(self):
		'''
		This function is invoked when 'ok' button in warning window is pressed,
		confirm atttribute is set 'True' and warning window is destroyed

		in: self
		out: confirm atttribute is set 'True' and warning window is destroyed
		'''
		self.warning_confirm = True
		self.warning.destroy()

	def throw_warning(self, text):
		'''
		Wrapper function for warning_window, if it is used for throwing traceback callback 
		then text of traceback is added for specified text,
		otherway only specified text is showed

		in: text of warning
		out: warning window with specified text and (if exists) traceback message
		'''
		self.warning_window()
		if 'NoneType: None' not in traceback.format_exc():
			text += '\n%s' % traceback.format_exc()
		self.warning_text.configure(text=text)
		center_window(self.warning, root)
		root.wait_window(self.warning)

	def click_tabbed(self, root, event):
		'''
		make tabbed element be pressed by 'enter' button from keyboard

		in: parent element, press event
		out: read 'enter' press
		'''
		widget = root.focus_get()
		if widget != root:
			widget.invoke()

	def wrap_delete(method):
		'''
		decorator for delete method of work fields, adds try/except construction
		to delete function that is specific for different work fields

		in: delete function
		out: decorated delete function
		'''
		def wrapper(self):
			'''
			inner function of wrap_delete decorator
			'''
			self.throw_warning('Delete chosen items?')
			if self.warning_confirm:
				try:
					method(self)
				except Exception:
					self.throw_warning('Failed to delete items:')
		return wrapper


class Players_WF(Work_field):
	'''
	Work field that displays managed players and groups, reload, delete and add buttons.
	Available functions:
		- add new player (requires unique name, ip address)
		- add new group (requires unique name)
		- delete any group or player from database
		- reload list of groups and players
		- choose any players and/or groups for further work with created list of items:
			* update content, start, stop, restart	
	'''
	def __init__(self, name, x, y):
		'''
		Consctructor of players work field class, inherits __init__ from Work_field class

		in: name, position of upper left corner of label
		out: creates label and field with listbox and scroll, reload and delete buttons
		'''
		Work_field.__init__(self, name, x, y)
		self.add_logo = PhotoImage(data=add_logo)	
		self.add_button = Button(main_canvas, image=self.add_logo, command=self.add_item)
		Hovertip(self.add_button, 'Add player/group')
		main_canvas.create_window(x+225, y+175, anchor=NE, window=self.add_button, tag='self')

	def make_chosen_list(self, event):
		'''
		Make list of currently chosen items, then change look of field after analyzing this list,
		and pass complete list of chosen players and groups to the variable for next using

		in: event of new selection in listbox
		out: changes in look, list of players_to_pass (chosen players and groups)
		'''
		global players_to_pass
		def switch_label(text_group, text_player):
			'''
			Helper function to change text in headers for groups and players

			in: text to put in header of groups, text to put in header of players
			out:change text in headers
			'''
			self.show.delete(0)
			self.show.insert(0, text_group)
			self.show.itemconfig(0, bg='#ff9900')
			self.show.delete(self.cap_pos)
			self.show.insert(self.cap_pos, text_player)
			self.show.itemconfig(self.cap_pos, bg='#ff9900')
		Work_field.make_chosen_list(self, event)
		if self.chosen_items == []:
			self.reload()
		else:
			switch_label('Cancel choosing', 'Cancel choosing')
			if 'Choose all groups'in self.chosen_items:
				self.show.selection_clear(0, END)
				self.show.selection_set(1, self.cap_pos-1)
				switch_label('Cancel choosing', 'Choose all players')
			if 'Choose all players'in self.chosen_items:
				self.show.selection_clear(0, END)
				self.show.selection_set(self.cap_pos+1, END)
				switch_label('Choose all groups', 'Cancel choosing')
			if 'Cancel choosing' in self.chosen_items:
				self.reload()
		Work_field.make_chosen_list(self, event)
		if self.chosen_items:
			self.delete_button.config(state='normal')
		players_to_pass = self.chosen_items

	def get_names(self, table):
		'''
		get content of name column in specified table

		in: table name
		out: tuple of content of name column in table
		'''
		sql = "SELECT name FROM %s" % table
		return get_info_db(sql)

	def get_addresses(self, table):
		'''
		get content of address column in specified table

		in: table name
		out: tuple of content of address column in table
		'''
		sql = "SELECT address FROM %s" % table
		return get_info_db(sql)

	def reload(self):
		'''
		delete all eitems in listbox, query players and groups names from database
		and insert them in viewfield.
		also delete all info from players_to_pass

		in: self
		out: delete old info and insert new on groups and players  
		'''
		global players_to_pass
		self.delete_button.config(state='disabled')
		self.show.delete(0, END)
		try:
			groups = pure(self.get_names('groups'))
			players = pure(self.get_names('players'))
		except Exception as error:
			self.throw_warning('Failed to reload list: %s' % error)
		self.show.insert(0, 'Choose all groups')
		self.show.itemconfig(0, bg='#ff9900')
		for i in groups:
			i += '_group'
			self.show.insert(END, i)
		self.cap_pos = len(groups)+1
		self.show.insert(self.cap_pos, 'Choose all players')
		self.show.itemconfig(self.cap_pos, bg='#ff9900')
		for i in players:
			i += '_player'
			self.show.insert(END, i)
		players_to_pass = []

	def add_item(self):
		'''
		create add dialog window and define necessary functions to add player or group in database

		in: self
		out: add dialog window
		'''
		def check_new_group(name, members=[], event=None):
			'''
			backend function for add group method, checks that new group 
			name is unique and do NOT contain
			word 'group', because tnen new table is created in database 
			with name like 'name_group' and all groups are displayed in 
			work field in that same manner 'name_group'.
			this restriction is made just for clearence of view and readability, 
			you can disable it if you understand what you are doing.
			empty group name is not allowed.
			if checks are passed then new entry is made in table 'groups' in db
			and new table 'name_group' is created to contain names of players-members (if they were passed).
			if members were not passed you can add players to group after in process of adding new player 
			there is also check after creation that all was done good

			in: group name, (optionally) members
			out: new entry in 'groups' table and new table for new group
			'''
			name = name.strip()
			add_canvas.delete('label_error')
			stop_word='group'
			groups = pure(self.get_names('groups'))
			label_error = Label(add_canvas, style='Red.TLabel')
			add_canvas.create_window(150, 70, window=label_error, tag='label_error')
			if stop_word in name:
				label_error.configure(text="Don't use word %s in name!" % stop_word)
			elif name in groups:
				label_error.configure(text="Name %s is already in use!" % name)
			elif not name:
				label_error.configure(text="Name shouldn't be empty!")
			else:
				try:
					conn = sqlite3.connect(path_to_db)
					cursor = conn.cursor()
					sql = "INSERT into groups VALUES (?)"
					cursor.execute(sql, (name,))
					name_g = name + '_group'
					sql = "CREATE TABLE %s (name text)" % name_g
					cursor.execute(sql)
					if members:
						for i in members:
							sql = "INSERT into %s VALUES (?)" % name_g
							cursor.execute(sql, (i,))
					conn.commit()
					cursor.close()
				except Exception:
					self.throw_warning('Failed to add group:')
				else:
					add_canvas.delete('add_group')
					add_dialog.unbind('<Return>')
					add_canvas.configure(width=200, height=100)
					info = Label(add_canvas)
					add_canvas.create_window(100, 20, window=info)
					quit = Button(add_canvas, text='OK', command=add_dialog.destroy)
					add_canvas.create_window(100, 60, window=quit)
					add_dialog.bind('<Return>', lambda event: self.click_tabbed(add_dialog, event))
					try:
						sql = "SELECT name from sqlite_master WHERE type='table' AND name='%s'" % name_g
						result = get_info_db(sql)
						if result:
							sql = "SELECT * FROM groups where name='%s'" % name
							result = get_info_db(sql)
							if result:
								info.configure(text='Group added successfuly.')
								center_window(add_dialog, root)
								quit.focus_set()
							else:
								info.configure(text='Group not added, check database')
								center_window(add_dialog, root)
								quit.focus_set()
						else:
							info.configure(text='Group not added, check database')
							center_window(add_dialog, root)
							quit.focus_set()
					except Exception:
						self.throw_warning('Failed to found new group:')
						info.configure(text='Group not added, check database')
						center_window(add_dialog, root)
						quit.focus_set()
				self.reload()

		def check_new_player(name, address, members=[], event=None):
			'''
			backend function for add player method, checks that new player 
			name is unique and do NOT contain
			word 'player', because tnen new table is created in database 
			with name like 'name_player' and all players are displayed in 
			work field in that same manner 'name_player'.
			this restriction is made just for clearence of view and readability, 
			you can disable it if you understand what you are doing.
			empty player name is not allowed.
			address is also checked to be unique and to follow the pattern of 4 numbers in range 1-254 separatef by dots.
			if checks are passed then new entry is made in table 'players' in db
			and new table 'name_player' is created to contain names of frozen videos.
			if members were passed then player becomes member of passed in groups.
			if members were not passed you can add players to group after in process of adding new group 
			there is also check after creation that all was done good

			in: player name, player, address, (optionally) members
			out: new entry in 'players' table and new table for new player
			'''
			name = name.strip()
			address = address.strip()
			add_canvas.delete('label_error')
			stop_word='player'
			players = pure(self.get_names('players'))
			addresses = pure(self.get_addresses('players'))
			label_error = Label(add_canvas, style='Red.TLabel')
			add_canvas.create_window(150, 115, window=label_error, tag='label_error')
			if stop_word in name:
				label_error.configure(text="Don't use word %s in name!" % stop_word)
			elif name in players:
				label_error.configure(text="Name %s is already in use!" % name)
			elif not name:
				label_error.configure(text="Name shouldn't be empty!")
			elif not fullmatch(r'[0-9]{,3}\.[0-9]{,3}\.[0-9]{,3}\.[0-9]{,3}', address):
				label_error.configure(text="Address should look like xxx.xxx.xxx.xxx!")
			elif address in addresses:
				label_error.configure(text="Address %s is already in use!" % address)
			else:
				try:
					conn = sqlite3.connect(path_to_db)
					cursor = conn.cursor()
					sql = "INSERT into players VALUES (?,?)"
					cursor.execute(sql, (name, address))
					name_p = name + '_player'
					sql = "CREATE TABLE %s (name text)" % name_p
					cursor.execute(sql)
					if members:
						for i in members:
							i += '_group'
							sql = "INSERT into %s VALUES (?)" % i
							cursor.execute(sql, (name,))
					conn.commit()
					cursor.close()
				except Exception:
					self.throw_warning('Failed to add player:')
				else:
					add_canvas.delete('add_player')
					add_dialog.unbind('<Return>')
					add_canvas.configure(width=200, height=100)
					info = Label(add_canvas)
					add_canvas.create_window(100, 20, window=info)
					quit = Button(add_canvas, text='OK', command=add_dialog.destroy)
					add_canvas.create_window(100, 60, window=quit)
					add_dialog.bind('<Return>', lambda event: self.click_tabbed(add_dialog, event))
					try:
						sql = "SELECT name from sqlite_master WHERE type='table' AND name='%s'" % name_p
						result = get_info_db(sql)
						if result:
							sql = "SELECT * FROM players where name='%s'" % name
							result = get_info_db(sql)
							if result:
								info.configure(text='Player added successfuly.')
								center_window(add_dialog, root)
								quit.focus_set()
							else:
								info.configure(text='Player not added, check database')
								center_window(add_dialog, root)
								quit.focus_set()
						else:
							info.configure(text='Player not added, check database')
							center_window(add_dialog, root)
							quit.focus_set()
					except Exception as error:
						self.throw_warning('Failed to found new player:')
						info.configure(text='Player not added, check database')
						center_window(add_dialog, root)
						quit.focus_set()
				self.reload()

		def add_item_group():
			'''
			frontend function of add group method, creates window, name field and optional
			members field.
			the form takes info on new group from user and sends it to backend function check_new_group

			in: nothing
			out: creates add group dialog window
			'''
			members = []
			def make_members(event):
				'''
				helper function to get list of members from user's choose in listbox

				in: event of new selection in listbox
				out: list of members
				'''
				nonlocal members
				members = ([listbox.get(id) for id in listbox.curselection()])
			add_canvas.delete('add_intro')
			add_canvas.configure(width=300, height=600)
			center_window(add_dialog, root)
			players = pure(self.get_names('players'))
			group_name = StringVar()
			label_group = Label(add_canvas, text='Group name:')
			add_canvas.create_window(150, 20, window=label_group, tag='add_group')
			entry = Entry(add_canvas, textvariable=group_name)
			entry.focus_set()
			add_canvas.create_window(150, 40, window=entry, tag='add_group')
			label_members = Label(add_canvas, text='Select members of group(optional):')
			add_canvas.create_window(150, 100, window=label_members, tag='add_group')
			frame = Frame(add_canvas)
			add_canvas.create_window(150, 120, anchor=N, window=frame, tag='add_group')
			scrollbar = Scrollbar(frame)
			listbox = Listbox(frame, height=25, highlightthickness=0, bd=0, exportselection=0, \
				yscrollcommand=scrollbar.set, selectmode=MULTIPLE)
			listbox.pack(side=LEFT, fill=BOTH, padx=10, pady=5)
			scrollbar.pack(side=RIGHT, fill=Y, padx=2, pady=2)
			scrollbar.config(command=listbox.yview)
			listbox.bind('<<ListboxSelect>>', make_members)
			for i in players:
				listbox.insert(END, i)
			button = Button(add_canvas, text='Submit', command=lambda: check_new_group(group_name.get(), members))
			add_canvas.create_window(150, 570, window=button, tag='add_group')
			add_dialog.bind('<Return>', lambda event: check_new_group(group_name.get(), members))

		def add_item_player():
			'''
			frontend function of add player method, creates window, name field, address field and optional
			members field.
			the form takes info on new player from user and sends it to backend function check_new_player

			in: nothing
			out: creates add player dialog window
			'''
			members = []
			def make_members(event):
				'''
				helper function to get list of members from user's choose in listbox

				in: event of new selection in listbox
				out: list of members
				'''
				nonlocal members
				members = ([listbox.get(id) for id in listbox.curselection()])
			add_canvas.delete('add_intro')
			add_canvas.configure(width=300, height=600)
			center_window(add_dialog, root)
			groups = pure(self.get_names('groups'))
			player_name = StringVar()
			player_address = StringVar()
			label_player = Label(add_canvas, text='Player name:')
			add_canvas.create_window(150, 20, window=label_player, tag='add_player')
			entry_name = Entry(add_canvas, textvariable=player_name)
			add_canvas.create_window(150, 40, window=entry_name, tag='add_player')
			label_address = Label(add_canvas, text='Player address:')
			add_canvas.create_window(150, 60, window=label_address, tag='add_player')
			entry_address = Entry(add_canvas, textvariable=player_address)
			add_canvas.create_window(150, 80, window=entry_address, tag='add_player')
			label_members = Label(add_canvas, text='Select groups to be part of(optional):')
			add_canvas.create_window(150, 150, window=label_members, tag='add_player')
			frame = Frame(add_canvas)
			add_canvas.create_window(150, 170, anchor=N, window=frame, tag='add_player')
			scrollbar = Scrollbar(frame)
			listbox = Listbox(frame, height=20, highlightthickness=0, bd=0, exportselection=0, \
				yscrollcommand=scrollbar.set, selectmode=MULTIPLE)
			listbox.pack(side=LEFT, fill=BOTH, padx=10, pady=5)
			scrollbar.pack(side=RIGHT, fill=Y, padx=2, pady=2)
			scrollbar.config(command=listbox.yview)
			listbox.bind('<<ListboxSelect>>', make_members)
			for i in groups:
				listbox.insert(END, i)
			button = Button(add_canvas, text='Submit', command=lambda: check_new_player(player_name.get(), player_address.get(), members))
			add_canvas.create_window(150, 570, window=button, tag='add_player')
			add_dialog.bind('<Return>', lambda event: check_new_player(player_name.get(), player_address.get(), members))

		add_dialog = Toplevel(root)
		add_dialog.title('Add item')
		add_dialog_logo = PhotoImage(data=add_logo)	
		add_dialog.tk.call('wm', 'iconphoto', add_dialog._w, add_dialog_logo)
		add_dialog.resizable(False, False)
		add_dialog.grab_set()
		add_dialog.focus_set()
		center_window(add_dialog, root)
		add_canvas = Canvas(add_dialog, width=200, height=100, highlightthickness=0)
		add_canvas.pack()
		add_dialog_btngr = Button(add_canvas, text='Add group', command=add_item_group)
		add_canvas.create_window(100, 30, window=add_dialog_btngr, tag='add_intro')
		add_dialog_btnpl = Button(add_canvas, text='Add player', command=add_item_player)
		add_canvas.create_window(100, 60, window=add_dialog_btnpl, tag='add_intro')

	@Work_field.wrap_delete
	def delete_item(self):
		'''
		delete chosen groups or/and players from database, 
		function is wrapped in try/except decorator

		in: list of currently chsen items
		out: deletets entries and tables of selected items
		'''
		for i in self.chosen_items:
			if i.endswith('_group'):
				conn = sqlite3.connect(path_to_db)
				cursor = conn.cursor()
				sql = "DELETE FROM groups where name=?"
				im = i[:-len('_group')]
				cursor.execute(sql, (im,))
				sql = "DROP TABLE IF EXISTS %s" % i
				cursor.execute(sql)
				conn.commit()
				cursor.close()
			if i.endswith('_player'):
				groups = pure(self.get_names('groups'))
				conn = sqlite3.connect(path_to_db)
				cursor = conn.cursor()
				sql = "DELETE FROM players where name = ?"
				im = i[:-len('_player')]
				cursor.execute(sql, (im,))
				sql = "DROP TABLE IF EXISTS %s" % i
				cursor.execute(sql)
				for group in groups:
					group_g = group + '_group'
					sql = "SELECT name FROM %s WHERE name=?" % group_g
					cursor.execute(sql, (im,))
					result = pure(cursor.fetchall())
					if result:
						sql = "DELETE FROM %s where name = ?" % group_g
						cursor.execute(sql, (im, ))
				conn.commit()
				cursor.close()
		self.reload()


class Local_WF(Work_field):

	def __init__(self, name, x, y):
		Work_field.__init__(self, name, x, y)
		self.play_logo = PhotoImage(data=play_logo)	
		self.play_button = Button(main_canvas, state=DISABLED, image=self.play_logo, command=self.play_item)
		Hovertip(self.play_button, 'Play chosen items')
		main_canvas.create_window(x+225, y+175, anchor=NE, window=self.play_button, tag=self)

	def reload(self):

		global videos_to_pass
		self.delete_button.config(state='disabled')
		self.play_button.config(state='disabled')
		self.show.delete(0, END)
		self.show.insert(0, 'Choose all videos')
		self.show.itemconfig(0, bg='#ff9900')
		try:
			for i in sorted(os.listdir(path_to_content)):
				if 'mp4' in i:
					self.show.insert(END, i)
		except Exception:
			self.throw_warning('Failed to reload list:')
		videos_to_pass = []

	def make_chosen_list(self, event):

		global videos_to_pass
		Work_field.make_chosen_list(self, event)
		if self.chosen_items == []:
			self.reload()
		else:
			self.show.delete(0)
			self.show.insert(0, 'Cancel choosing')
			self.show.itemconfig(0, bg='#ff9900')
			if self.chosen_items[0] == 'Choose all videos':
				self.show.selection_clear(0, END)
				self.show.selection_set(1, END)
				self.show.delete(0)
				self.show.insert(0, 'Cancel choosing')
				self.show.itemconfig(0, bg='#ff9900')
			if self.chosen_items[0] == 'Cancel choosing':
				self.reload()
		Work_field.make_chosen_list(self, event)
		if self.chosen_items:
			self.delete_button.config(state='normal')
			self.play_button.config(state='normal')
		videos_to_pass = self.chosen_items

	@Work_field.wrap_delete
	def delete_item(self):

		for i in self.chosen_items:
			i = path_to_content + i
			os.remove(i)
		self.reload()

	def play_item(self):

		playlist = []
		try:
			for i in self.chosen_items:
				i = path_to_content + i
				playlist.append(i)
			subprocess.Popen([interpreter, path_to_player] + playlist,close_fds=True,  creationflags=subprocess.CREATE_NO_WINDOW)
		except Exception:
			self.throw_warning('Failed to play items:')


class Remote_WF(Work_field):

	def __init__(self, name, x, y):

		Work_field.__init__(self, name, x, y)
		self.freeze_logo = PhotoImage(data=freeze_logo)	
		self.freeze_button = Button(main_canvas, state=DISABLED, image=self.freeze_logo, command=self.freeze_item)
		Hovertip(self.freeze_button, 'Freeze/unfreeze chosen items')
		main_canvas.create_window(x+225, y+175, anchor=NE, window=self.freeze_button, tag=self)

	def reload(self, mute=False):

		global players_complete
		players_complete = []
		self.show.bind('<<ListboxSelect>>', self.make_chosen_list)
		def get_address(name):

			sql = "SELECT address FROM players WHERE name=?"
			address = pure(get_info_db(sql, (name,)))[0]
			return address
		def get_groups(name):

			groups = Players_WF.get_names(self, 'groups')
			partof = []
			for group in groups:
				sql = "SELECT name FROM groups WHERE name=?"
				result = pure(get_info_db(sql, (name,)))
				if result:
					partof.append(group)
			return partof
		def make_players_complete(gp_list):

			global players_complete
			for i in gp_list:
				if '_group' in i:
					sql = "SELECT name FROM %s" % i
					result = pure(get_info_db(sql))
					for n in result:
						if n not in players_complete:
							players_complete.append(n)
				if '_player' in i:
					i = i[:-len('_player')]
					if i not in players_complete:
						players_complete.append(i)
			return players_complete
		self.delete_button.config(state='disabled')
		self.freeze_button.config(state='disabled')
		if len(players_to_pass) == 0:
			self.show.delete(0, END)
			self.show.insert(0, 'Choose player or group in')
			self.show.insert(1, 'right column and reload')
			self.show.insert(2, 'to get remote playlist')
			self.show.itemconfig(0, bg='#ff9900')
			self.show.itemconfig(1, bg='#ff9900')
			self.show.itemconfig(2, bg='#ff9900')
			players_complete = []
		elif (len(players_to_pass) == 1) and ('_player' in players_to_pass[0]):
			try:
				name = players_to_pass[0][:-len('_player')]
				address = get_address(name)
				pending = Label(main_canvas, style='Pending.TLabel', text='Pending operations, please wait...')
				main_canvas.create_window(400, 300, window=pending, tag='pending')
				root.update()
				p = get_list_content(address, secret)
				if 'unreachable' in p:
					if not mute:
						put_message('%s: server offline' % name, tag='error')
					main_canvas.delete('pending')
				else:
					if not mute:
						put_message('%s: server online' % name)
					remote_playlist = sorted(get_list_content(address, secret))
					main_canvas.delete('pending')
					self.show.delete(0, END)
					self.header = '%s %s' % (name, address)
					self.show.insert(0, self.header)
					self.show.itemconfig(0, bg='#ff9900')
					for i in remote_playlist:
						if i.strip():
							self.show.insert(END, i)
					sql = "SELECT name FROM %s" % players_to_pass[0]
					result = pure(get_info_db(sql))
					self.freezed_videos = []
					for i in result:
						if i.strip() in remote_playlist:
							item_id = remote_playlist.index(i) +1
							self.show.itemconfig(item_id, bg='#cccccc')
							self.freezed_videos.append(i)
					if not mute:
						put_message('\tplaylist loaded')
			except Exception:
				self.throw_warning('Failed to get playlist:' )
				main_canvas.delete('pending')
			players_complete.append(name)
		else:
			self.show.unbind('<<ListboxSelect>>')
			self.show.delete(0, END)
			players_complete = make_players_complete(players_to_pass)
			for name in players_complete:
				address = address = get_address(name)
				self.header = '%s %s' % (name, address)
				self.show.insert(END, self.header)
				self.show.itemconfig(END, bg='#ff9900')

	def make_chosen_list(self, event):

		def switch_label(label):
			'''
			helper function to switch label 
			'''
			self.show.delete(0)
			self.show.insert(0, label)
			self.show.itemconfig(0, bg='#ff9900')

		def switch_button(state):
			'''
			helper function to switch button state
			'''
			self.delete_button.config(state=state)
			self.freeze_button.config(state=state)

		Work_field.make_chosen_list(self, event)
		if self.chosen_items == []:
			switch_button('disabled')
			switch_label(self.header)
		elif ('Choose player or group in' in self.chosen_items) or ('right column and reload' in self.chosen_items) or ('to get remote playlist' in self.chosen_items) :
			switch_button('disabled')
			self.show.selection_clear(0, END)
		else:
			switch_label('Cancel choosing')
			if self.chosen_items[0] == 'Cancel choosing':
				switch_label(self.header)
				switch_button('disabled')
				self.show.selection_clear(0, END)
			elif '.mp4' not in self.chosen_items[0]:
				if self.show.get(1):
					self.show.selection_clear(0, END)
					self.show.selection_set(1, END)
					switch_label('Cancel choosing')
					switch_button('normal')
			else:
				switch_button('normal')
		Work_field.make_chosen_list(self, event)

	@Work_field.wrap_delete
	def delete_item(self):
		'''
		delete chosen videos from remote player, 
		function is wrapped in try/except decorator

		in: list of currently chsen items
		out: deletets videos from remote player
		'''
		delete_list = []
		for i in self.chosen_items:
			if i not in self.freezed_videos:
				delete_list.append(i)
			if i in self.freezed_videos:
				self.throw_warning("Can't delete %s. Item is freezed" % i)
		if delete_list:
			address = self.header.split(' ')[1]
			stop_player(address, secret)
			remove = remove_file(address, secret, delete_list)
			put_message('\t%s' % remove)
			start_player(address, secret)
		self.reload()

	def freeze_item(self):
		'''
		freeze item in remote playlist to exclude it from any update: 
		it can't be deleted and will always be in playlist, this state saves in database in 'name_player' table
		and is checked on playlist reload

		in: currently chosen items in remote content field
		out: freeze/unfreeze items
		'''
		for i in self.chosen_items:
			name = self.header.split(' ')[0] + '_player'
			conn = sqlite3.connect(path_to_db)
			cursor = conn.cursor()
			if i in self.freezed_videos:
				self.freezed_videos.remove(i)
				sql = "DELETE FROM %s where name = ?" % name
				cursor.execute(sql, (i,))
				presented_list = self.show.get(0, END)
				item_id = presented_list.index(i)
				self.show.itemconfig(item_id, bg='#ffffff')
			else:
				self.freezed_videos.append(i)
				sql = "INSERT into %s VALUES (?)" % name
				cursor.execute(sql, (i,))
				presented_list = self.show.get(0, END)
				item_id = presented_list.index(i)
				self.show.itemconfig(item_id, bg='#cccccc')
			conn.commit()
			cursor.close()

def pre_update_content(secret):
	'''
	defines operations to be made before update_content is called
	checks for players or groups to be chosen, checks for local playlist to be chosen, throws warning, checks if player online,
	updates content in separate thread

	in: secret
	out: updates content on chosen players
	'''
	if not (players_to_pass and videos_to_pass):
		remote_content.throw_warning('Choose videos and players to start updating.')
	else:
		remote_content.throw_warning('Update content?')
		if remote_content.warning_confirm:
			try:
				def update_thread():
					'''
					wrapper function
					update content in separate thread to avoid freezing of root window

					in: nothing
					out: runs update_content in separate thread
					'''
					if len(players_complete) ==1:
						remote_content.reload(mute=True)
					else:
						remote_content.reload()
					pending = Label(main_canvas, text='Pending operations, please wait...', font=(None, 14))
					main_canvas.create_window(400, 300, window=pending, tag='pending')
					pending.grab_set()
					root.update()
					for player in players_complete:
						player_p = player + '_player'
						playlist_complete = []
						delete_queue = []
						upload_queue = []
						sql = "SELECT address FROM players WHERE name=?"
						address = pure(get_info_db(sql, (player,)))[0]
						print_to_log('pending update content on %s, %s' % (player, address))
						p = get_list_content(address, secret)
						if 'unreachable' in p:
							put_message('%s: server offline' % player, tag='error')
							if len(players_complete) ==1:
								main_canvas.delete('pending')
						else:
							put_message('%s: server online' % player)
							remote_playlist = get_list_content(address, secret)
							sql = "SELECT name FROM %s" % player_p
							freezed_videos = pure(get_info_db(sql))
							if remote_playlist:
								for i in remote_playlist:
									if i not in freezed_videos:
										playlist_complete.append(i)
								for i in playlist_complete:
									if i not in videos_to_pass:
										delete_queue.append(i)
								for i in videos_to_pass:
									if i not in remote_playlist:
										upload_queue.append(i)
							else:
								upload_queue = videos_to_pass
								delete_queue = []
							update_content(address, secret, upload_queue, delete_queue)
							print_to_log('content updated on %s, %s' % (player, address))
					pending.grab_release()
					main_canvas.delete('pending')
					remote_content.reload(mute=True)
				threading.Thread(target=update_thread).start()
			except Exception:
				remote_content.throw_warning('Failed to update content:')
				print_to_log('Failed to update content on %s, %s:\n%s' % (player, address, traceback.format_exc()))
				main_canvas.delete('pending')

def pre_stop_player(secret):
	'''
	defines operations to be made before stop_player is called
	checks for players or groups to be chosen, throws warning, checks if player online,
	stops players

	in: secret
	out: stops chosen players
	'''
	if not players_to_pass:
		remote_content.throw_warning('Choose players to stop.')
	else:
		remote_content.throw_warning('Stop players?')
		if remote_content.warning_confirm:
			try:
				if len(players_complete) ==1:
					remote_content.reload(mute=True)
				else:
					remote_content.reload()
				for player in players_complete:
					player_p = player + '_player'
					sql = "SELECT address FROM players WHERE name=?"
					address = pure(get_info_db(sql, (player,)))[0]
					print_to_log('pending stop player %s, %s' % (player, address))
					pending = Label(main_canvas, text='Pending operations, please wait...', font=(None, 14))
					main_canvas.create_window(400, 300, window=pending, tag='pending')
					root.update()
					p = get_list_content(address, secret)
					if 'unreachable' in p:
						put_message('%s: server offline' % player, tag='error')
						main_canvas.delete('pending')
					else:
						put_message('%s: server online' % player)
						stop_player(address, secret)
						main_canvas.delete('pending')
						print_to_log('player %s, %s stopped' % (player, address))
			except Exception:
				remote_content.throw_warning('Failed to stop player:')
				print_to_log('Failed to stop player %s, %s:\n%s' % (player, address, traceback.format_exc()))
				main_canvas.delete('pending')

def pre_start_player(secret):
	'''
	defines operations to be made before start_player is called
	checks for players or groups to be chosen, throws warning, checks if player online,
	starts players
	if player is already running throws message in text field

	in: secret
	out: starts chosen players
	'''
	if not players_to_pass:
		remote_content.throw_warning('Choose players to start.')
	else:
		remote_content.throw_warning('Start players?')
		if remote_content.warning_confirm:
			try:
				if len(players_complete) ==1:
					remote_content.reload(mute=True)
				else:
					remote_content.reload()
				for player in players_complete:
					player_p = player + '_player'
					sql = "SELECT address FROM players WHERE name=?"
					address = pure(get_info_db(sql, (player,)))[0]
					print_to_log('pending start player %s, %s' % (player, address))
					pending = Label(main_canvas, text='Pending operations, please wait...', font=(None, 14))
					main_canvas.create_window(400, 300, window=pending, tag='pending')
					root.update()
					p = get_list_content(address, secret)
					if 'unreachable' in p:
						put_message('%s: server offline' % player, tag='error')
						main_canvas.delete('pending')
					else:
						put_message('%s: server online' % player)
						start_player(address, secret)
						main_canvas.delete('pending')
						print_to_log('player %s, %s started' % (player, address))
			except Exception:
				remote_content.throw_warning('Failed to start player:')
				print_to_log('Failed to start player %s, %s:\n%s' % (player, address, traceback.format_exc()))
				main_canvas.delete('pending')

def pre_restart_player(secret):
	'''
	defines operations to be made before stop_player and start_player are called
	checks for players or groups to be chosen, throws warning, checks if player online,
	restarts players

	in: secret
	out: restarts chosen players
	'''
	if not players_to_pass:
		remote_content.throw_warning('Choose players to restart.')
	else:
		remote_content.throw_warning('Restart players?')
		if remote_content.warning_confirm:
			try:
				remote_content.reload()
				for player in players_complete:
					player_p = player + '_player'
					sql = "SELECT address FROM players WHERE name=?"
					address = pure(get_info_db(sql, (player,)))[0]
					print_to_log('pending restart player %s, %s' % (player, address))
					pending = Label(main_canvas, text='Pending operations, please wait...', font=(None, 14))
					main_canvas.create_window(400, 300, window=pending, tag='pending')
					root.update()
					p = get_list_content(address, secret)
					if 'unreachable' in p:
						put_message('%s: server offline' % player, tag='error')
						main_canvas.delete('pending')
					else:
						put_message('%s: server online' % player)
						stop_player(address, secret)
						start_player(address, secret)
						main_canvas.delete('pending')
						print_to_log('player %s, %s restarted' % (player, address))
			except Exception:
				remote_content.throw_warning('Failed to restart player:')
				print_to_log('Failed to restart player %s, %s:\n%s' % (player, address, traceback.format_exc()))
				main_canvas.delete('pending')

def main_board():
	'''
	creates main board of program with work fields, buttons and text field

	in: nothing
	out: creates main board of program
	'''
	global remote_content, put_message
	root.protocol("WM_DELETE_WINDOW", on_closing)
	main_canvas.delete('login')
	main_canvas.config(width=850, height=650)
	root.title('RMVID')
	root.unbind('<Return>')

	def open_content():
		'''
		open folder with local content via explorer in iew process, don't wait for it to finish

		in: nothing
		out: opens content folder
		'''
		try:
			subprocess.Popen(['explorer', path_to_content],close_fds=True,  creationflags=subprocess.CREATE_NO_WINDOW)
		except:
			remote_content.throw_warning('Failed to open content folder:')
			print_to_log('Failed to content folder:\n%s' % traceback.format_exc())

	def open_converter():
		'''
		open converter.py from tools in new process, don't wait for it to finish

		in: nothing
		out: opens converter.py
		'''
		try:
			subprocess.Popen([interpreter, path_to_converter],close_fds=True,  creationflags=subprocess.CREATE_NO_WINDOW)
		except:
			remote_content.throw_warning('Failed to open converter:')
			print_to_log('Failed to open converter:\n%s' % traceback.format_exc())

	menubar = Menu(root)
	menubar.add_command(label='Open content folder', command=open_content)
	menubar.add_command(label="Converter", command=open_converter)
	root.config(menu=menubar)
	
	update_button = Button(main_canvas, text='Update', command= lambda: pre_update_content(secret))
	main_canvas.create_window(10, 420, anchor=NW, window=update_button, tag='update')
	stop_button = Button(main_canvas, text='Stop player', command= lambda: pre_stop_player(secret))
	main_canvas.create_window(90, 420, anchor=NW, window=stop_button, tag='stop_player')
	start_button = Button(main_canvas, text='Start player', command= lambda: pre_start_player(secret))
	main_canvas.create_window(170, 420, anchor=NW, window=start_button, tag='start_player')
	restart_button = Button(main_canvas, text='Restart player', command= lambda: pre_restart_player(secret))
	main_canvas.create_window(250, 420, anchor=NW, window=restart_button, tag='restart_player')

	message_window = Frame(main_canvas)
	message_scrollbar = Scrollbar(message_window)
	message_text = Text(message_window, state="disabled", highlightthickness=0, bd=0, yscrollcommand=message_scrollbar.set)
	main_canvas.create_window(10, 450, anchor=NW, window=message_window,  width=830, height=190)
	message_scrollbar.pack(side=RIGHT, fill=Y, padx=2, pady=2)
	message_text.pack(side=LEFT, fill=BOTH, padx=10, pady=5, expand=True)
	message_scrollbar.config(command=message_text.yview)
	message_text.tag_config('error', background='#ff3300')

	def put_message(text, tag=False):
		'''
		insert message into message_text field,
		try/except is left for future improvements
		text field is disabled while there is no input from program, user can't type here directly

		in: text
		out: puts text in message_field
		'''
		time = datetime.today().strftime('[%H:%M:%S]')
		message_text.configure(state='normal')
		text = time + '\t' + text +'\n'
		if tag:
			message_text.insert(END, text, tag)
		else:
			message_text.insert(END, text)

		message_text.configure(state='disabled')
		message_text.see(END)
		root.update()

	local_content = Local_WF('local content', 20, 20)
	remote_content = Remote_WF('remote content', 300, 20)
	players_groups = Players_WF('players & groups', 580, 20)
	local_content.reload()
	players_groups.reload()
	remote_content.reload()

	root.update()
	center_window(root)

def login_user(event=None):
	'''
	backend function for login user method, checks password, grantes/denies access to main program

	in: gets value of password from variable
	out: prompts for password until correct is passed
	'''
	main_canvas.delete('login_wrong')
	secret_pass = secret.get()
	if hashlib.md5((secret_pass + client_address + secret_pass).encode('utf-8')).hexdigest() == video_quality:
		main_board()
		print_to_log('access granted')
	else:
		main_canvas.create_text(100, 90, text='Wrong password', tag='login login_wrong', font=(None, 10))
		login_input.delete(0, END)
		print_to_log('access denied')

def login_window():
	'''
	frontend function for login user method, creates window with password input.
	can be omitted by commenting it out in main program but then you have to call main_board,
	but further control of players will be imposiible,
	of course you should understand what you are doing

	in: nothing
	out: creates login window
	'''
	global login_input
	main_canvas.create_text(100, 15, text='Password: ', tag='login', font=(None, 10))
	login_input = Entry(main_canvas, show='*', textvariable=secret)
	login_input_window = main_canvas.create_window(100, 35, window=login_input, tag='login')
	login_button = Button(main_canvas, text='Enter', command=login_user)
	login_button_window = main_canvas.create_window(100, 65, width=60, window=login_button, tag='login')
	login_input.focus_set()
	root.bind('<Return>', login_user)
	root.protocol("WM_DELETE_WINDOW", root.destroy)

def on_closing():
	'''
	callback for os closing window event defined by root.protocol, works only after login passed,
	login window closes without warning
	
	in: user tries to close window via os window manager
	out: thrown warning window
	'''
	remote_content.throw_warning('Do you really want to quit?')
	if remote_content.warning_confirm:
		root.destroy()

players_to_pass = []
players_complete = []
videos_to_pass = []

root = Tk()
#styles
Style().configure("WF.TFrame", background='white', relief=GROOVE)
Style().configure("Red.TLabel", foreground='red')
Style().configure("Pending.TLabel", font=(None, 14))
center_window(root)
secret = StringVar()
root.title('Login')
main_logo = PhotoImage(data=main_logo)
root.tk.call('wm', 'iconphoto', root._w, main_logo)
root.resizable(False, False)
main_canvas = Canvas(root, width=200, height=100, highlightthickness=0)
main_canvas.pack()
login_window()
print_to_log('rmvid started')
root.mainloop()