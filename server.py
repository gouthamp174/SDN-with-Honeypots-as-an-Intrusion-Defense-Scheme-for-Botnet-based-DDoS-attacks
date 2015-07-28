##server code for EE209 DDoS project
import time, os, sys, string, threading, math, random
from socket import *  #importing the socket library for network connections

class Server():
  def __init__(self, host, port):
    self.host = host
    self.port = port

    self.h_tokens = ["/cc.txt","/accounts.txt","/classified.txt"]
    self.blacklist = {}

    self.num_connections = 1
    self.num_connects_last_interval = 0
    self.avg_connects_per_interval = 0
    self.num_intervals = -1
    self.ddos_detected = 0
    self.captcha_mode = 0
    self.ddos_count = 0

    #Creating socket object
    self.serv = socket(AF_INET,SOCK_STREAM)

    #bind socket to address
    self.serv.bind((self.host, self.port))
    self.serv.listen(5)
    print 'Server up and running! Listening for incoming connections...'

  def collectData(self):
    threading.Timer(2.0, self.collectData).start()
    self.num_intervals += 1
    if self.num_intervals >= 1:
      print "num connections in last interval", self.num_connects_last_interval
      self.avg_connects_per_interval = ((self.avg_connects_per_interval * (self.num_intervals-1)) + self.num_connects_last_interval) / self.num_intervals
      print "avg connections per interval", self.avg_connects_per_interval
      errorBound = self.avg_connects_per_interval * self.marginOfError(self.num_intervals, 1.96) #95% conf level
      self.checkBound(errorBound)
    self.num_connects_last_interval = 0

  def marginOfError(self, sampleSize, critValue):
    margin = critValue/(2 * math.sqrt(sampleSize))
    return margin

  def checkBound(self, error):
    if self.num_connects_last_interval > 5 and self.ddos_detected == 0:
      print "DDoS ATTACK WARNING...\n<CAPTCHA MODE ENABLED>"
      self.ddos_detected = 1
      self.captcha_mode = 1
      self.ddos_count += 1
    elif self.num_connects_last_interval > 100 and self.ddos_detected > 0:
      print "DDoS ATTACK DETECTED! ERROR...\n<CAPTCHA MODE ENABLED>"
      self.ddos_detected += 1
      self.captcha_mode = 1
      self.ddos_count += 1
    elif self.num_connects_last_interval < self.avg_connects_per_interval + error and self.ddos_detected > 1:
      print "ALERT!!! ALERT!!! SERVER UNDER ATTACK..."
      self.ddos_detected = 0
      self.avg_connects_per_interval = 0
      self.num_intervals = -1
      self.captcha_mode = 0
    else:
      self.ddos_detected = 0
      if self.ddos_count > 0:
      	self.captcha_mode = 1
      else:
	self.captcha_mode = 0
    print "\n"

  def rdm(self):
	r = ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(8)])
	return r

  def acceptConnections(self):
    conn, addr = self.serv.accept() ## accept incoming connection
	
    #start of the program
    data = conn.recv(1024)
    print "Message From " + addr[0] + " : " + data
    print 'Connected by ', addr, 'Number of connections: ', self.num_connections
    print ">>>>>>>>>>>>>"
    self.num_connects_last_interval += 1
    self.num_connections += 1
    
    if addr[0] not in self.blacklist.keys():	
    	command, path, httpv= data.split()   #strip HTTP request "GET /%s HTTP/1.1\r\n" to get filename
		
    	if path in self.h_tokens:
		self.blacklist[addr[0]] = 1
		print "Source ",addr[0]," was added to the blacklist."
		print self.blacklist
    	else:
		pass

    	datapath = "/home/mininet/new_folder"+path
		
       	if self.captcha_mode == 1:
		print "VALIDATION IN PROCESS..."
		captcha = self.rdm()
		self.msg = "Authenticate yourself by entering the following CAPTCHA: "+captcha
		conn.send(self.msg)
		
		data = conn.recv(1024)
		if  data == self.msg:
			print "USER AUTHENTICATED."
			fd=open(datapath)
			self.msg = fd.read()
			fd.close()
			conn.send(self.msg)
		else:
			print "USER NOT AUTHENTICATED."
			self.msg = "Authentication Failed. Please try again."
			conn.send(self.msg)
    	else:
		fd=open(datapath)
		body = fd.read()
		self.msg = "GET "+path+" HTTP/1.1\r\nDatacode 200\r\n"
		fd.close()
		conn.send(body)
		#conn.send(body)
    else:
	self.blacklist[addr[0]] += 1
	print "Source ",addr[0]," was already blacklisted."
	print self.blacklist
	
	command, path, httpv= data.split()   #strip HTTP request "GET /%s HTTP/1.1\r\n" to get filename

	if path in self.h_tokens:
		datapath = "/home/mininet/new_folder"+path
		
       		if self.captcha_mode == 1:
			print "VALIDATION IN PROCESS..."
			captcha = self.rdm()
			self.msg = "Authenticate yourself by entering the following CAPTCHA: "+captcha
			conn.send(self.msg)
			
			data = conn.recv(1024)
			if  data == self.msg:
				print "USER AUTHENTICATED."
				fd=open(datapath)
				self.msg = fd.read()
				fd.close()
				conn.send(self.msg)
			else:
				print "USER NOT AUTHENTICATED."
				self.msg = "Authentication Failed. Please try again."
				conn.send(self.msg)
    		else:
			fd=open(datapath)
			body = fd.read()
			self.msg = "GET "+path+" HTTP/1.1\r\nDatacode 200\r\n"
			fd.close()
			conn.send(body)
			#conn.send(body) 
	else:
		conn.send("404 File Not Found")

		
#'THIS MESSAGE WAS SENT FROM THE SERVER'
#    conn.close()
##Setting up variables
HOST = '10.0.0.7'
PORT = 8080
ADDR = (HOST,PORT)
BUFSIZE = 2048

if __name__ == '__main__':
  victimServer = Server(HOST, PORT)

  victimServer.collectData()

  while 1:
    victimServer.acceptConnections()
