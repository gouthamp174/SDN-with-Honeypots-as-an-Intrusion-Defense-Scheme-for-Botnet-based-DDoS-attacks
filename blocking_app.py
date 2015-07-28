from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.util import dpid_to_str
import time

log = core.getLogger()

_flood_delay = 0

class LearningSwitch (object):

  def __init__ (self, connection):
    # Connecting L2 Switches to POX.
    self.connection = connection

    # Our table - Flow Table and Blacklist Table
    self.macToPort = {}
    self.blacklist = {}

    # Listening to PacketIn messages for connections
    connection.addListeners(self)

    self.hold_down_expired = _flood_delay == 0

#Handle PacketIn messages from the switch to implement DDoS Mitigation policy.
  def _handle_PacketIn (self, event):

    packet = event.parsed

    #Flooding Action
    def flood (message = None):
      msg = of.ofp_packet_out()
      if time.time() - self.connection.connect_time >= _flood_delay:

        if self.hold_down_expired is False:
          self.hold_down_expired = True
          log.info("%s: Flood hold-down expired -- flooding",
              dpid_to_str(event.dpid))

        if message is not None: log.debug(message)
        msg.actions.append(of.ofp_action_output(port = of.OFPP_FLOOD))
      else:
        pass

      msg.data = event.ofp
      msg.in_port = event.port
      self.connection.send(msg)

    #Drops this packet and optionally installs a flow to continue dropping similar ones for a while
    def drop (duration = None):
      if duration is not None:
        if not isinstance(duration, tuple):
          duration = (duration,duration)
        msg = of.ofp_flow_mod()
        msg.match = of.ofp_match.from_packet(packet)
        msg.idle_timeout = duration[0]
        msg.hard_timeout = duration[1]
        msg.buffer_id = event.ofp.buffer_id
        self.connection.send(msg)
      elif event.ofp.buffer_id is not None:
        msg = of.ofp_packet_out()
        msg.buffer_id = event.ofp.buffer_id
        msg.in_port = event.port
        self.connection.send(msg)

    #Drop packets from sources which were blacklisted earlier
    def drop_bl():
	port = self.macToPort[packet.dst]
	msg = of.ofp_flow_mod()
	msg.match = of.ofp_match.from_packet(packet,event.port)
	msg.command = of.OFPFC_MODIFY
	msg.idle_timeout = 120
	msg.hard_timeout = 120
	msg.buffed_id = event.ofp.buffer_id
	msg.actions.append(of.ofp_action_output(port = of.OFPP_NONE))
	msg.out_port = port
	log.debug("Dropping packets for blacklisted flow- %s.%i -> %s.%i\n" %(packet.src, event.port, packet.dst, port))
	self.connection.send(msg)

    #Delete flow tables for the newly blacklisted sources
    def delete_bl():
	port = self.macToPort[packet.dst]
	msg = of.ofp_flow_mod()
	msg.match = of.ofp_match.from_packet(packet,event.port)
	msg.command = of.OFPFC_DELETE_STRICT
	msg.out_port = port
	log.debug("Deleting flow for %s.%i -> %s.%i\n" %(packet.src, event.port, packet.dst, port))
	self.connection.send(msg)
	self.blacklist[(packet.src,packet.dst)][0] = 0

    #Install flow table entries within the switches
    def install():
	port = self.macToPort[packet.dst]
	log.debug("Installing flow for %s.%i -> %s.%i\n" %
	          (packet.src, event.port, packet.dst, port))
	msg = of.ofp_flow_mod()
	msg.match = of.ofp_match.from_packet(packet, event.port)
	msg.idle_timeout = 10
	msg.hard_timeout = 30
	msg.actions.append(of.ofp_action_output(port = port))
	msg.data = event.ofp # 6a
	self.connection.send(msg)
	self.blacklist[(packet.src,packet.dst)][0] += 1

    #Check sources present in blacklist
    def blacklist_check(src_mac,src_dst):
	if self.blacklist[(src_mac,src_dst)][1] == "B":
		print "The flow %s -> %s is blacklisted. Access denied."%(src_mac, src_dst)
		#actions to be taken when the src is already blacklisted
		drop_bl()
	else:
		log.debug("The flow %s -> %s is not blacklisted. Flow-Count = %i. Checking the flow..." %(packet.src, src_dst,self.blacklist[(src_mac,src_dst)][0]))
		count_check((src_mac,src_dst))

    #Measure the flow table entries for each source and determine blacklist status 
    def count_check(key):
	t1 = self.blacklist[key][0]
	t2 = 35
	t3 = 40
	#print "\n Warning Threshold = %i, Dropping Threshold = %i"%(t2,t3)
	if t1>=t2 and t1<t3:
		print "Warning. The High inflow of packets from %s -> %s"%(packet.src,packet.dst)
		install()
	elif t1>=t3:
		print "Attention: DDoS attack from %s -> %s "%(packet.src,packet.dst)
		self.blacklist[key][1] = "B"
		#print "New source added to Black Listed sources:",self.blacklist
		#actions to be taken when the src is blacklisted
		delete_bl()
	else:
		print "Genuine Source... Relax"
		install()

    #Start of the program
    if packet.src not in self.macToPort:
    	self.macToPort[packet.src] = event.port

    if (packet.src,packet.dst) not in self.blacklist.keys():
	self.blacklist[(packet.src,packet.dst)] = [0,"NB"]

    if packet.dst.is_multicast:
      flood()
    else:
      if packet.dst not in self.macToPort:
	flood("Port for %s unknown -- flooding" % (packet.dst,))
      else:
	port = self.macToPort[packet.dst]

	if port == event.port:
	  
	  log.warning("Same port for packet from %s -> %s on %s.%s.  Drop."
	      % (packet.src, packet.dst, dpid_to_str(event.dpid), port))
	  drop(10)
	  return
	
	blacklist_check(packet.src,packet.dst)


#DDoS Class
class ddos209 (object):
  
  #Waits for OpenFlow switches to connect and makes them learning switches.

  def __init__ (self):
    core.openflow.addListeners(self)

  def _handle_ConnectionUp (self, event):
    log.debug("Connection %s" % (event.connection,))
    LearningSwitch(event.connection)


def launch (hold_down=_flood_delay):
  
  #Starts an L2 learning switch.

  try:
    global _flood_delay
    _flood_delay = int(str(hold_down), 10)
    assert _flood_delay >= 0
  except:
    raise RuntimeError("Expected hold-down to be a number")

  core.registerNew(ddos209)
