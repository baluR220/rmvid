import socket
import subprocess
import sys
import os
from datetime import datetime
import hashlib
from tracebak import format_exc


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
host_to_listen = ""
port_to_listen = 13789
source = '[server]'
greet = '[rmvid client connection]'

with open(path_to_config) as config:
	options = {}
	for line in config:
		line = line.strip()
		if not(line.startswith('#') or  line == '') :
			key, val = line.split('=')
			options[key] = val

path_to_ccenter = options['path_to_ccenter']
path_to_log = options['path_to_log']
path_to_temp = options['path_to_temp']
address = options['address']
video_quality = options['video_quality']

def nice(data):
	nice_data = ''
	count = 0
	for i in address:
		count += ord(i)
	count = count % 100
	for i in data:
		nice_data += chr(ord(i)^count)
	return nice_data

def print_to_log(data):
	date = path_to_log + datetime.today().strftime('%Y.%m.%d')
	time = datetime.today().strftime('[%H:%M:%S]')
	with open(date, 'a')as output:
		print(time, source, data, file=output)

def connection():
	global addr
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
	sock.bind((host_to_listen, port_to_listen))
	sock.listen(1)
	conn, addr = sock.accept()
	data = conn.recv(1024).decode('utf-8')
	udata = nice(data)
	if udata != greet:
		print_to_log('NOT rmvid client connection. Closing')
		sock.shutdown(socket.SHUT_RDWR)
		sock.close()
	else:
		print_to_log('rmvid client %s connected' % addr[0])
		conn.send(nice('connected to rmvid server').encode('utf-8'))
	
		auth =  nice(conn.recv(1024).decode('utf-8'))
		if auth == video_quality:
			conn.send(nice('accept').encode('utf-8'))
			print_to_log('rmvid client %s authentication passed' % addr[0])
			while True:
				data = conn.recv(1024).decode('utf-8')
				udata = nice(data)
				if udata == 'exit':
					print_to_log('rmvid client %s disconnected' % addr[0])
					conn.send(nice('end of session').encode('utf-8'))
					break
				elif udata == 'send_file':
					conn.send(nice('preparing for transfer').encode('utf-8'))
					data = conn.recv(1024).decode('utf-8')
					udata = nice(data).split('|')
					file_name = udata[0]
					file_path = path_to_temp + file_name
					file_size = int(udata[1])
					if file_name and file_size:
						conn.send(nice('ready').encode('utf-8'))
						with open(file_path, 'wb') as file:
							while True:
								chunk_summ = nice(conn.recv(1024).decode('utf-8'))
								if chunk_summ == 'EOF':
									break
								conn.send(nice('chunk_summ_recvd').encode('utf-8'))
								while True:
									chunk = conn.recv(1024)
									chunk_recv_summ = hashlib.md5(chunk).hexdigest()
									if chunk_recv_summ == chunk_summ:
										conn.send(nice('clean').encode('utf-8'))
										file.write(chunk)
										del chunk
										del chunk_summ
										break
									else:
										conn.send(nice('dirty').encode('utf-8'))
										continue
						if os.path.getsize(file_path) == file_size:
							conn.send(nice('size ok').encode('utf-8'))
						else:
							conn.send(nice('size wrong').encode('utf-8'))
					else:
						conn.send(nice('empty file name and size').encode('utf-8'))
					print_to_log('file transfered from %s: [%s]' % (addr[0], file_name))
					
				else:
					p = subprocess.check_output(['python3', path_to_ccenter, udata]).decode('utf-8')
					p = nice(p).encode('utf-8')
					conn.send(p)
					del p
		else:
			conn.send(nice('decline').encode('utf-8'))
			print_to_log('rmvid client %s authentication failed' % addr[0])
		sock.close()
		del data
		del udata
		del auth
	connection()


print_to_log('rmvid server started')
while True:
	try:
		connection()
	except:
		print_to_log('Error occured while connecting with %s:\n%s' % (addr[0], format_exc()))