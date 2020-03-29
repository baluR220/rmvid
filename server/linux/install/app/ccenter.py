import sys
import os
from datetime import datetime
import subprocess


_platform = sys.builtin_module_names

if 'posix' in _platform:
	platform = 'posix'
	slash = '/'
	config = '.config'
elif 'nt' in _platform:
	print('wrong installer! choose installer for win')
	sys.exit()

work_dir = os.path.dirname(os.path.realpath(__file__)) + slash
path_to_config = work_dir + config

with open(path_to_config) as config:
	options = {}
	for line in config:
		line = line.strip()
		if not(line.startswith('#') or  line == '') :
			key, val = line.split('=')
			options[key] = val

path_to_log = options['path_to_log']
path_to_content = options['path_to_content']
path_to_temp = options['path_to_temp']
player = options['player']
source = '[ccenter]'

def print_to_log(data):
	date = path_to_log + datetime.today().strftime('%Y.%m.%d')
	time = datetime.today().strftime('[%H:%M:%S]')
	with open(date, 'a')as output:
		print(time, source, data, file=output)

def stop_player():
	os.system('killall %s' % player)
	print_to_log('player stopped')
	return('player stopped')

def start_player():
	p  = subprocess.check_output(['ps','-A']).decode('utf-8')
	if 'mpv' in p:
		print_to_log('failed to start player, player is already running')
		return('failed to start player, player is already running')
	else:
		os.system('%s --really-quiet --mute=yes --no-stop-screensaver --loop-playlist --fullscreen %s*.mp4 > /dev/null 2>&1 &' % (player, path_to_content))
		print_to_log('player started')
		return('player started')

def get_list(path, size=False):
	file_list_raw = os.listdir(path)
	if file_list_raw:
		if size:
			file_dict = ''
			for i in file_list_raw:
				file_dict += i +  '|' + str(os.path.getsize(path + i)) + ' '
			print_to_log('dict of temp returned')
			return file_dict
		else:
			file_list = ''
			for i in file_list_raw:
				file_list += i + ' '
			print_to_log('list of content returned')
			return file_list
	else:
		return None
def remove_file(data):
	delete_queue = data[:]
	for i in data:
		os.remove(path_to_content + i)
	print_to_log('files removed: %s' % delete_queue)
	return('files removed')

def refresh_content():
	if platform == 'posix':
		os.system('mv %s* %s' % (path_to_temp, path_to_content))
	elif platform == 'nt':
		os.system('move %s* %s' % (path_to_temp, path_to_content))
	print_to_log('content refreshed')
	return('content refreshed')

def digest_data(data):
	data = data.split(' ')
	if data[0] =='get_list_content':
		print(get_list(path_to_content), end='')
	elif data[0] =='get_list_temp':
		print(get_list(path_to_temp, size=True), end='')
	elif data[0] =='remove_file':
		print(remove_file(data[1:]), end='')
	elif data[0] =='refresh_content':
		print(refresh_content(), end='')
	elif data[0] =='stop_player':
		print(stop_player(), end='')
	elif data[0] =='start_player':
		print(start_player(), end='')
	else:
		print_to_log('wrong command: %s' % data)
		print('wrong command')

digest_data(sys.argv[1])
