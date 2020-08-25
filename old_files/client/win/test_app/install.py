import sys
import os
import subprocess
import hashlib
import getpass
import sqlite3


_platform = sys.builtin_module_names
if 'posix' in _platform:
	print('wrong client! choose client for linux')
	sys.exit()

elif 'nt' in _platform:
	slash = '\\' 
	config = 'config'
	platform = 'nt'
	encoding = 'cp866'
	search_word = 'ipv4'
	separator = ':'
	find_ip = subprocess.check_output(['ipconfig']).decode(encoding).lower()

work_dir = os.path.dirname(os.path.realpath(__file__)) + slash
path_to_config = work_dir + config

if os.path.exists(path_to_config):
	print('old config is found. exiting')
	sys.exit()

#ip address
ip_raw = []
ip_clean=[]
find_ip = find_ip.split('\n')
for line in find_ip:
	if search_word in line:
		ip_raw.append(line)
for line in ip_raw:
	line = line.split(separator)
	line = line[1].strip()
	ip_clean.append(line)

for i in ip_clean:
	print('%s' % i, end=' ')
while True:
	address = input('\nspecify your ip addres: ')
	if address in ip_clean:
		break
	print('wrong address, try again')

#video quality
while True:
	secret = getpass.getpass(prompt='specify secret: ')
	if secret:
		break
	else:
		print('Do not leave secret empty! try again\n')
video_quality = hashlib.md5((secret + address + secret).encode('utf-8')).hexdigest()

with open(path_to_config, 'w') as config:
	path = work_dir + 'content' + slash
	if not os.path.exists(path):
		os.mkdir(path)
	print('#path to content folder\npath_to_content=%s\n' % path, file=config)
	path = work_dir + 'log' + slash
	if not os.path.exists(path):
		os.mkdir(path)
	print('#path to log folder\npath_to_log=%s\n' % path, file=config)
	path = work_dir + 'players' + slash
	if not os.path.exists(path):
		os.mkdir(path)
	print('#path to groups\npath_to_groups=%s\n' % path, file=config)
	
	path = work_dir + 'tools' + slash
	print('#path to tools\npath_to_tools=%s\n' % path, file=config)
	path = work_dir + 'client.py'
	print('#path to client.py\npath_to_client=%s\n' % path, file=config)
	print('#address\naddress=%s\n' % address, file=config)
	print('#video_quality\nvideo_quality=%s\n' % video_quality, file=config)

if not os.path.exists(path_to_config):
	print('config file not found, run config_make first')
	sys.exit()

with open(path_to_config) as config:
	options = {}
	for line in config:
		line = line.strip()
		if not(line.startswith('#') or  line == '') :
			key, val = line.split('=')
			options[key] = val

path_to_groups = options['path_to_groups']
path_to_db = path_to_groups + slash + 'rmvid.db'

if  os.path.exists(path_to_db):
	print('db file found, new one is not created')
else:
	conn = sqlite3.connect(path_to_db)
	cursor = conn.cursor()

	cursor.execute("""CREATE TABLE groups
		(name text)
		""")
	cursor.execute("""CREATE TABLE players
		(name text, address text)
		""")
	conn.commit()
	print('database created')
input('RMVID client installed. Press Enter to exit')