import sys
import os
import subprocess
import hashlib
import getpass


_platform = sys.builtin_module_names
if 'posix' in _platform:
	platform = 'posix'
	slash = '/'
	config = '.config'
	encoding = 'utf-8'
	search_word = 'inet '
	separator = ' '
	find_ip = subprocess.check_output(['ip', 'addr']).decode(encoding).lower()

elif 'nt' in _platform:
	print('wrong installer! choose installer for win')
	sys.exit()


cur_dir = os.path.dirname(os.path.realpath(__file__)) + slash
work_dir = '/opt/rmvid-server/'
path_to_config = work_dir + config

if os.path.exists(path_to_config):
	print('Found config file. Run /opt/rmvid-server/uninstall.sh first')
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
	line = line[5].split(slash)
	line = line[0]
	ip_clean.append(line)

for i in ip_clean:
	print('[%s]' % i, end=' ')
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
	print('do not leave secret empty')

video_quality = hashlib.md5((secret + address + secret).encode('utf-8')).hexdigest()
if not os.path.exists(work_dir):
	os.mkdir(work_dir)
with open(path_to_config, 'w') as config:
	path = work_dir + 'content' + slash
	if not os.path.exists(path):
		os.mkdir(path)
	print('#path to content folder\npath_to_content=%s\n' % path, file=config)
	path = work_dir + 'log' + slash
	if not os.path.exists(path):
		os.mkdir(path)
	print('#path to log folder\npath_to_log=%s\n' % path, file=config)
	path = work_dir + 'temp' + slash
	if not os.path.exists(path):
		os.mkdir(path)
	print('#path to temp\npath_to_temp=%s\n' % path, file=config)
	
	path = work_dir + 'server.py'
	print('#path to server.py\npath_to_server=%s\n' % path, file=config)
	path = work_dir + 'ccenter.py'
	print('#path to ccenter.py\npath_to_ccenter=%s\n' % path, file=config)
	print('#address\naddress=%s\n' % address, file=config)
	print('#player\nplayer=mpv\n', file=config)
	print('#video_quality\nvideo_quality=%s\n' % video_quality, file=config)

path = cur_dir + 'app/*'
os.system('cp %s %s' % (path, work_dir))

