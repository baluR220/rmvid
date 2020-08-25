import socket
import sys
import hashlib
import os
from datetime import datetime
import traceback


if len(sys.argv) < 4:
	print('you should pass at least 3 arguments: ip, port and command')
	sys.exit()

server_address = sys.argv[1]
secret = sys.argv[2]
data = sys.argv[3:]
port = 13789
source = '[client]'
greet = '[rmvid client connection]'
auth = hashlib.md5((secret + server_address + secret).encode('utf-8')).hexdigest()

_platform = sys.builtin_module_names
if 'posix' in _platform:
	print('wrong client! choose client for linux')
	sys.exit()
elif 'nt' in _platform:
	slash = '\\' 
	config = 'config'
	platform = 'nt'

work_dir = os.path.dirname(os.path.realpath(__file__)) + slash
path_to_config = work_dir + config

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
path_to_log = options['path_to_log']
client_address = options['address']

def print_to_log(data):
	date = path_to_log + datetime.today().strftime('%Y.%m.%d')
	time = datetime.today().strftime('[%H:%M:%S]')
	with open(date, 'a')as output:
		print(time, source, data, file=output)

def nice(data):
	nice_data = ''
	count = 0
	for i in server_address:
		count += ord(i)
	count = count % 100
	for i in data:
		nice_data += chr(ord(i)^count)
	return nice_data

def send_file(conn, data):
	if len(data) < 2:
		print_to_log('not enough info to send file %s, exiting' % data)
		conn.close()
		sys.exit()
	load_config()
	path_to_content = options['path_to_content']
	for i in data[1:]:
		print_to_log('%s sending file %s to %s' % (client_address, i, server_address))
		file_name = i
		file_path = path_to_content + slash + file_name
		file_size = str(os.path.getsize(file_path))
		file_info = file_name + '|' + file_size
		size_send = 0
		conn.send(nice('send_file').encode('utf-8'))
		redata = nice(conn.recv(1024).decode('utf-8'))
		print_to_log('%s %s' % (server_address, redata))
		udata = nice(file_info).encode('utf-8')
		conn.send(udata)
		redata = nice(conn.recv(1024).decode('utf-8'))
		print_to_log('%s %s' % (server_address, redata))
		print(file_name)
		if redata == 'ready':
			with open(file_path, 'rb') as file:
				chunk = True
				while chunk:
					chunk = file.read(1024)
					if not chunk:
						break
					chunk_summ = nice(hashlib.md5(chunk).hexdigest()).encode('utf-8')
					while True:
						size_send += 1024
						progress = (size_send / int(file_size))*100
						conn.send(chunk_summ)
						redata = nice(conn.recv(1024).decode('utf-8'))
						conn.sendall(chunk)
						redata = nice(conn.recv(1024).decode('utf-8'))
						if redata == 'clean':
							del chunk_summ
							break
						elif redata == 'dirty':
							continue
						else:
							print_to_log('error: no answer on chunk send %s, exiting' % server_address)
							sys.exit()
			udata = nice('EOF').encode('utf-8')
			conn.send(udata)
			redata = nice(conn.recv(1024).decode('utf-8'))
			if redata == 'size ok':
				print_to_log('%s sending %s to %s succeed' % (client_address, i, server_address))
			elif redata == 'size wrong':
				print_to_log('%s sending %s to %s failed, wrong size' % (client_address, i, server_address))
			else:
				print_to_log('error: %s %s' % (redata, server_address))
	udata = nice('exit').encode('utf-8')
	conn.send(udata)
	redata = nice(conn.recv(1024).decode('utf-8'))
	print_to_log('%s %s' % (redata, server_address))

def send_message(conn, data):
	print_to_log('%s sending message to %s: %s' % (client_address, server_address, data))
	while data[0]:
		if data[-1] != 'exit':
			data.append('exit')
		udata = nice(data[0]).encode('utf-8')
		conn.send(udata)
		redata = nice(conn.recv(1024).decode('utf-8'))
		if redata == 'end of session':
			print_to_log('%s %s' % (redata, server_address))
		else:
			print(redata.strip(), end='')
		if data[0] == 'exit':
			break
		data = data[1:]

def connection():
	conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	conn.settimeout(5)
	conn.connect((server_address, port))
	conn.send(nice(greet).encode('utf-8'))
	redata = nice(conn.recv(1024).decode('utf-8'))
	print_to_log('%s %s' % (redata, server_address))
	return conn


print_to_log('%s client invocked' % client_address)
try:
	conn = connection()
	conn.send(nice(auth).encode('utf-8'))
	answer = nice(conn.recv(1024).decode('utf-8'))
	if answer == 'decline':
		print_to_log('%s authentication failed, exiting' % server_address)
	elif answer == 'accept':
		print_to_log('%s authentication passed' % server_address)
		if data[0] == 'send_file':
			send_file(conn, data)
		else:
			send_message(conn, data)

except:
	print_to_log('rmvid server %s is unreachable, exiting.\n%s' % (server_address, traceback.format_exc()))
	print('rmvid server %s is unreachable' % server_address, end='')
	sys.exit()

conn.close()
print_to_log('%s client worked out, closed gracefully' % client_address)

