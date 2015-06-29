# Setup logging
import logging
log = logging.getLogger('zen.zplibTwemproxy')

# PythonCollector Imports
from ZenPacks.zenoss.PythonCollector.datasources.PythonDataSource import PythonDataSourcePlugin

# Twisted Imports
from twisted.internet.defer import inlineCallbacks, returnValue

import socket
import json
import pprint

class zplibTwemproxyDeviceData(PythonDataSourcePlugin):
    """ Twemproxy Device data source plugin """

    # List of device attributes you might need to do collection.
    proxy_attributes = (
        'zTwemproxyPort',
        )

    @classmethod
    def config_key(cls, datasource, context):
        # One call will get data for device and components
        #   so don't include context.id in the config_key return

	return (
	    context.device().id,
	    datasource.getCycleTime(context),
	    'zplibTwemproxyDeviceData',
	    )
    @classmethod
    def params(cls, datasource, context):
        # Don't need any params - zProperties passed as proxy_attributes
        return

    @inlineCallbacks
    def collect(self, config):

        # Define netcat procedure to actually get data
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

        data = self.new_data()

        # Only need to run netcat once for all datasources on this host
        ds0 = config.datasources[0]
	if not ds0.zTwemproxyPort:
	    # If no zTwemproxyPort then set to 22222
	    ds0.zTwemproxyPort = '22222'

	host = ds0.manageIp
	port = int(ds0.zTwemproxyPort)
	content = ''
	#log.info('In for datasource loop. ds0 is %s, host is %s, port is %s \n' % (ds0, host, port))
	try:
	    s = yield netcat(host, port, content, log)
	except Exception, e:
	    log.error( "%s: %s", device.id, e)
	    #continue
	j_data = json.loads(s)

        for datasource in config.datasources:
       	    for k,v in j_data.iteritems():
		if isinstance(v, dict):             #got a server pool
		    #log.info('Pool is %s  datasource id is %s \n' % (k, datasource.datasource))
		    poolName = k
		    for k1,v1 in v.iteritems():
			if isinstance(v1, dict):    # got a server

                            # Next line just short-circuits for debugging
                            #continue

                            sp = k1.split(':')
			    server_addr = sp[0]
			    try:
				servername,serveralias,serveraddresslist = socket.gethostbyaddr(server_addr)
			    except:
				servername = server_addr
			    port = sp[1]
                            id = servername + '_' + port
                            #log.info('got server data - datasource.component is %s and serverName is %s and datasource is %s  \n' % (datasource.component, id, datasource.datasource))
                            if datasource.component == id:
                                for datapoint_id in (x.id for x in datasource.points):
                                    if not v1.has_key(datapoint_id):
                                        continue
                                    try:
                                        value = v1[datapoint_id]
                                    except Exception, e:
                                        log.error('Failed to get value datapoint for server component, error is %s' % (e))
                                        continue
				    dpname = '_'.join((datasource.datasource, datapoint_id))
				    data['values'][datasource.component][dpname] = (value, 'N')
			else:
                            # Then we have pool metrics
                            #log.info(' Got pool data - datasource.component is %s and poolName is %s and datasource is %s  \n' % (datasource.component, poolName, datasource.datasource))
                            if datasource.component == poolName:
				for datapoint_id in (x.id for x in datasource.points):
                                    if not v.has_key(datapoint_id):
                                        continue
				    try:
					value = v[datapoint_id]
                                        #log.info('pool %s datapoint %s datapoint_value %s \n' % (poolName, datapoint_id, v[datapoint_id]))
				    except Exception, e:
                                        log.error('Failed to get value datapoint for pool component, error is %s' % (e))
					continue
				    dpname = '_'.join((datasource.datasource, datapoint_id))
				    data['values'][datasource.component][dpname] = (value, 'N')
        returnValue(data)

