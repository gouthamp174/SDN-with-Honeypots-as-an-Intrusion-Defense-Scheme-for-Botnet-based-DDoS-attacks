##server code for EE209 DDoS project
import time, os, sys, string, threading, math
from socket import *  #importing the socket library for network connections

class Server():
  def __init__(self, host, port):
    self.host = host
    self.port = port

    self.num_connections = 0
    self.num_connects_last_interval = 0
    self.avg_connects_per_interval = 0
    self.num_intervals = -1
    self.ddos_detected = 0

    #Creating socket object
    self.serv = socket(AF_INET,SOCK_STREAM)

    #bind socket to address
    self.serv.bind((self.host, self.port))
    self.serv.listen(5)
    print 'Server up and running! Listening for incomming connections...'

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
    if self.num_connects_last_interval > 5 + error and self.ddos_detected == 0:
      print "DDOS WARNING"
      self.ddos_detected = 1
    elif self.num_connects_last_interval > self.avg_connects_per_interval + error and self.ddos_detected > 0:
      print "DDOS DETECTED! ERROR:", self.ddos_detected
      self.ddos_detected += 1
    elif self.num_connects_last_interval < self.avg_connects_per_interval + error and self.ddos_detected > 1:
      print "ALERT!!! ALERT!!! SERVER UNDER ATTACK..."
      print "SERVER SHUTTING DOWN..."
      self.ddos_detected = 0
      self.avg_connects_per_interval = 0
      self.num_intervals = -1
      os._exit(1)
    else:
      self.ddos_detected = 0
    print "error bound:", error

  def acceptConnections(self):
    conn, addr = self.serv.accept() ## accept incoming connection
    data = conn.recv(1024)
    print "Message From " + addr[0] + " : " + data
    print 'Connected by ', addr, 'Number of connections: ', self.num_connections
    print ">>>>>>>>>>>>>"
    self.num_connects_last_interval += 1
    self.num_connections += 1

    command, path, httpv= data.split()   #strip HTTP request "GET /%s HTTP/1.1\r\n" to get filename
    datapath = "/home/mininet/new_folder"+path
    fd=open(datapath)
    body = fd.read()
    fd.close()
    conn.send(body)
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
