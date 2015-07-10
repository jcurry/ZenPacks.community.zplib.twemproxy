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
        # Pass parameter that represents the server's <IP address>:<port>
        #   as is used for the key to the server dictionary in the raw data
        # Twemproxy object has string attributes for serverAddress and serverPort

        params = {}
        
        params['ipPort'] = ''
        if hasattr(context, 'serverAddress') and hasattr(context, 'serverPort'):
            params['ipPort'] = context.serverAddress + ':' + context.serverPort

        return params

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
	    log.info('End of netcat. hostname is %s and port is %s \n' % (hostname, port))
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

        for datasource in config.datasources:   # ie. one per component instance - probably lots
            #log.info(' Datasource is %s and datasource.component is %s\n' % (datasource.datasource, datasource.component))
	    if j_data.has_key(datasource.component):
		# got a pool
                log.info(' Got a pool %s \n' % (datasource.component))
                poolDict = j_data[datasource.component]
		for datapoint_id in (x.id for x in datasource.points):
		    if not poolDict.has_key(datapoint_id):
			continue
		    try:
			value = poolDict[datapoint_id]
			#log.info('pool %s datapoint %s datapoint_value %s \n' % (poolName, datapoint_id, v[datapoint_id]))
		    except Exception, e:
			log.error('Failed to get value datapoint for pool component, error is %s' % (e))
			continue
		    dpname = '_'.join((datasource.datasource, datapoint_id))
		    data['values'][datasource.component][dpname] = (value, 'N')

            else:  # datasource.component is not a pool - must be a server
                ipPort = datasource.params['ipPort']
                #log.info(' Datasource is %s and ipPort is %s \n' % (datasource.datasource, ipPort))
                for k,v in j_data.iteritems():
                    if isinstance(v, dict):    # got a server pool
			#serverKey = getattr(v, ipPort, None)
                        if v.has_key(ipPort):
                            serverDict = v[ipPort]
                        #log.info('ipPort is %s and serverKey is %s and k is %s and v is %s \n' % (ipPort, serverKey, k, v))
			#if serverKey:	# got dictionary for server data matching component
			    #log.info(' Got dictionary for server data matching component %s \n' % (serverDict))
			    for datapoint_id in (x.id for x in datasource.points):
				if not serverDict.has_key(datapoint_id):
				    continue
				try:
				    value = serverDict[datapoint_id]
				except Exception, e:
				    log.error('Failed to get value datapoint for server component, error is %s' % (e))
				    continue
				dpname = '_'.join((datasource.datasource, datapoint_id))
				data['values'][datasource.component][dpname] = (value, 'N')
				break

        returnValue(data)

