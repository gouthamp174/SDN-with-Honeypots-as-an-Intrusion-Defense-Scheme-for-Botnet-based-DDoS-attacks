##Client code for DDoS Project
import sys
from socket import * 

HOST = '10.0.0.7'
PORT = 8080
ADDR = (HOST,PORT)
BUFSIZE = 2048

message='asdf.txt'

client = socket(AF_INET,SOCK_STREAM)
client.connect((ADDR))

client.send("GET /%s HTTP/1.1\r\n" % message)

data = client.recv(BUFSIZE)
x = data
if "Authenticate" in x:
	print data	
	inp = raw_input()
	client.send("Authenticate yourself by entering the following CAPTCHA: %s" % inp)

	data = client.recv(BUFSIZE)
	if ("Authentication Failed" in data):
		print data
		sys.exit(0)
	else:
		pass			
else:
	pass
data = data.rstrip()
print data

client.close()
