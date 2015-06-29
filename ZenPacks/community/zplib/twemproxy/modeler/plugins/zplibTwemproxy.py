""" Model twemproxy device

Use socket connection to connect to <ip addr> <port> combination
Result is in JSON format
"""

# Twisted Imports
from twisted.internet.defer import inlineCallbacks, returnValue

# Zenoss Imports
from Products.DataCollector.plugins.CollectorPlugin import PythonPlugin
from Products.DataCollector.plugins.DataMaps import ObjectMap, RelationshipMap

import socket
import json
import pprint

def netcat(hostname, port, content, log):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    log.info('In netcat. hostname is %s and port is %s \n' % (hostname, port))
    s.connect((hostname, port))
    s.sendall(content)
    s.shutdown(socket.SHUT_WR)
    result=[]

    while 1:
        data = s.recv(1024)
        if data == "":
            break
        #print "Received:", repr(data)
        result.append(data)
    #print "Connection closed."
    s.close()
    return ''.join(result)

class zplibTwemproxy(PythonPlugin):
    """ twemproxy modeler plugin """

    requiredProperties = (
        'zTwemproxyPort',
        )

    deviceProperties = PythonPlugin.deviceProperties + requiredProperties

    @inlineCallbacks
    def collect(self, device, log):
        """Asynchronously collect data from device. Return a deferred."""
        log.info("%s: collecting data", device.id)

	twemproxyPort = getattr(device, 'zTwemproxyPort', None)
	if not twemproxyPort:
	    # If no zTwemproxyPort set then set to default of 22222
	    twemproxyPort = '22222'
	    
	host = device.manageIp
	port = int(twemproxyPort)
	content = ''
	try:
	    s = yield netcat(host, port, content, log)
	    #print ' \n\nResult is %s \n\n' % (s)
	    #print s
	    #j_data=json.loads(s)
	    #pprint.pprint(j_data)
	except Exception, e:
	    log.error(
		"%s: %s", device.id, e)
	    returnValue(None)
	log.info('Response is %s \n' % (s))
	returnValue(s)


    def process(self, device, results, log):
        """Process results. Return iterable of datamaps or None."""

        maps = []
        pools = []
        j_data = json.loads(results)

        serverdict = {}
        devicedata = {}
	for k,v in j_data.iteritems():
	    if isinstance(v, dict):		#got a server pool
		log.info('Pool %s\n' % (k))
                poolName = self.prepId(k)
                serverdictk = {}
		for k1,v1 in v.iteritems():
		    if isinstance(v1, dict):    # got a server
                        serverdictk[k1] = v1
		    else:
			log.info('Server pool attributes -  key is %s and value is %s' % (k1, v1))
                serverdict[poolName] = serverdictk

                pools.append(ObjectMap(data={
                    'id': poolName,
                    'title': poolName,
                    }))
	    else:
                if k in ['version', 'uptime', 'curr_connections']:
                    if k == 'uptime':
                        # uptime in seconds so convert to days
                        v = int(v / 86400)
                    device_attr = 'twemproxy_' + k
                    devicedata[device_attr] = v
		log.info('Twemproxy device attributes - key is %s and value is %s' % (device_attr, v))

        maps.append(ObjectMap(
            modname = 'ZenPacks.community.zplib.twemproxy.TwemproxyDevice',
            data = devicedata ))
            
        maps.append(RelationshipMap(
            relname = 'twemproxyServerPools',
            modname = 'ZenPacks.community.zplib.twemproxy.TwemproxyServerPool',
            objmaps = pools ))
        maps.extend(self.getTwemproxyServerMap(device, serverdict, log))

        return maps

    def getTwemproxyServerMap(self, device, serverdict, log):
        rel_maps = []

        for k, v in serverdict.iteritems():
            compname = 'twemproxyServerPools/%s' % (k)
            object_maps = []
            for k1, v1 in v.iteritems():
		# server key in format '<ip address>:<port>'
		sp = k1.split(':')
		server_addr = sp[0]
		try:
		    servername,serveralias,serveraddresslist = socket.gethostbyaddr(server_addr)
		except:
		    servername = server_addr
		port = sp[1]
                id = self.prepId(servername + '_' + port)
		log.info('Server name is %s Server address is %s Port is %s \n' % (servername, server_addr, port))
		object_maps.append(ObjectMap(data={
                    'id': id,
                    'serverName': servername,
                    'serverAddress': server_addr,
                    'serverPort': port,
                    }))
            rel_maps.append(RelationshipMap(
                compname = compname,
                relname = 'twemproxyServers',
                modname = 'ZenPacks.community.zplib.twemproxy.TwemproxyServer',
                objmaps = object_maps))

        return rel_maps

