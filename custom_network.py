#!/usr/bin/python

from mininet.net import Mininet
from mininet.node import Controller, RemoteController
from mininet.node import Host
from mininet.node import OVSKernelSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink, Intf

def my_network():
    net= Mininet(topo=None, build=False, controller=RemoteController)

    #Add Controller
    info( '***Adding Controller\n' )
    poxController1 = net.addController('c0',controller=RemoteController,ip="192.168.56.101",port=6633)
    #poxController2 = net.addController(name='c2',controller=POX)

    #Add Switches
    info( '***Adding Switches\n' )
    #switch12=net.addSwitch('switch12')
    switch1=net.addSwitch('s1')
    switch2=net.addSwitch('s2')

    #Add Hosts
    info( '***Adding Hosts\n' )
    host1=net.addHost('h1', ip='10.0.0.2/24')
    host2=net.addHost('h2', ip='10.0.0.3/24')
    host3=net.addHost('h3', ip='10.0.0.4/24')
    host4=net.addHost('h4', ip='10.0.0.5/24')
    host5=net.addHost('h5', ip='10.0.0.6/24')
    server=net.addHost('h6', mac='00:00:10:00:00:01', ip='10.0.0.7/24')
    client=net.addHost('h7', ip='10.0.0.8/24')
    ill_client=net.addHost( 'h8', ip ='10.0.0.9/24')

    #Add Links
    info ( '***Creating Links\n' )
    net.addLink(host1,switch1)
    net.addLink(host2,switch1)
    net.addLink(host3,switch1)
    net.addLink(host4,switch1)
    net.addLink(host5,switch1)
    net.addLink(client,switch1)
    net.addLink(ill_client,switch1)
    net.addLink(switch1,switch2)
    net.addLink(server,switch2)

    net.build()

    info( '***Starting network\n' )
    net.start()
    #for controller in net.controllers:	
    	#controller.start()

    #s1.start([poxController1])
    #s2.start([poxController2])
    #net.get('switch12').start([poxController])

    info( '***Entering command prompt\n' )
    CLI(net)

    info( '***Stopping network\n' )
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    my_network()
