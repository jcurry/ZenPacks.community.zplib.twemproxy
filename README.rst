=============================
ZenPack to support twemproxy
=============================

Description
===========
This ZenPack supports  devices that are using the twemproxy package. 

twemproxy (pronounced "two-em-proxy"), aka nutcracker, is a fast and lightweight proxy for 
memcached and redis protocol. It was built primarily to reduce the number of connections to the 
caching servers on the backend.  For more information and the code, 
visit https://github.com/twitter/twemproxy .

The zenpack gathers pool and server statistics simply by attaching to the twemproxy port with
a socket-level Python program.

This ZenPack is built with the zenpacklib library so does not have explicit code definitions for
device classes, device and component objects or zProperties.  Templates are also created through zenpacklib.
These elements are all created through the zenpack.yaml file in the main directory of the ZenPack.
See http://zenpacklib.zenoss.com/en/latest/index.html for more information on zenpacklib.

Note that if templates are changed in the zenpack.yaml file then when the ZenPack is reinstalled, the
existing templates will be renamed in the Zenoss ZODB database and the new template from the YAML file
will be installed; thus a backup is effectively taken.  Old templates should be deleted in the Zenoss GUI
when the new version is proven.

The ZenPack introduces a new zProperties for configuring twemproxy:
    * zTwemproxyPort            default is 22222

The ZenPack creates a new device object called TwemproxyDevice and new component types for:
    * Twemproxy Server Pool
    * Twemproxy Server

where TwemproxyDevice -> contains many TwemproxyServerPool components -> contains many TwemproxyServer components.

The Overview display for a device in the /Server/Linux/twemproxy class has been extended in the
middle-upper panel to include twemproxy version, uptime and current_connections data.

The /Server/Linux/twemproxy device class is supplied with appropriate zProperties 
and templates applied. Although a modeler plugin is supplied, it is not automatically
added to this device class, so as not to override any /Server/Linux plugins inherited in the
local environment.  The zPythonClass standard property is set 
to ZenPacks.community.zplib.twemproxy.TwemproxyDevice for the device class.

THE zplibTwemproxy MODELER PLUGIN MUST BE MANUALLY ADDED TO YOUR /Server/Linux/twemproxy DEVICE
CLASS AFTER THE ZENPACK HAS BEEN INSTALLED.

Component templates for Server Pool and Server are supplied with:
    * Twemproxy Server Pool
        * client_eof
        * client_err
        * server_ejects
        * forward_error
        * client_connections
        * fragments
    * Twemproxy Server
        * server_eof
        * server_err
        * server_timedout
        * requests
        * request_bytes
        * responses
        * response_bytes
        * in_queue
        * in_queue_bytes
        * out_queue
        * out_queue_bytes

All the templates are based on Python and a dsplugins.py is provided in the main Zenpack
directory which queries the twemproxy port and parses the data into the defined datapoints. 
These Python templates require the PythonCollector ZenPack to be installed as a 
prerequisite (version >=1.6)

There may be a large number of components for twemproxy devices, each with a large number of
datapoints.  The cycle time of the templates is set at 300 seconds and it is strongly recommended
that this is not decreased.

The component display for a Twemproxy Server Pool has a dropdown menu to show all related Twemproxy Servers.  
The Twemproxy Server component has a link back to its related Twemproxy Server Pool.


A /Twemproxy Event Class is included  with the ZenPack and is configured into the templates.


Requirements & Dependencies
===========================

    * Zenoss Versions Supported:  4.x
    * External Dependencies: 
      * The zenpacklib package that this ZenPack is built on, requires PyYAML.  This is installed as 
      standard with Zenoss 5 and with Zenoss 4 with SP457.  To test whether it is installed, as
      the zenoss user, enter the python environment and import yaml:

        python
        import yaml
        yaml

        <module 'yaml' from '/opt/zenoss/lib/python2.7/site-packages/PyYAML-3.11-py2.7-linux-x86_64.egg/yaml/__init__.py'>

      If pyYAML is not installed, install it, as the zenoss user, with:

        easy_install PyYAML

      and then rerun the test above.


    * ZenPack Dependencies: PythonCollector >= 1.6
    * Installation Notes: Restart zenoss entirely after installation
    * Configuration: Add the zplibTwemproxy modeler plugin to the /Server/Linux/twemproxy device class



Download
========
Download the appropriate package for your Zenoss version from the list
below.

* Zenoss 4.0+ `Latest Package for Python 2.7`_

ZenPack installation
======================

This ZenPack can be installed from the .egg file using either the GUI or the
zenpack command line. To install in development mode, from github - 
https://github.com/jcurry/ZenPacks.community.zplib.twemproxy  use the ZIP button
(top left) to download a tgz file and unpack it to a local directory, say,
$ZENHOME/local.  Install from $ZENHOME/local with:

zenpack --link --install ZenPacks.community.zplib.twemproxy

Restart zenoss after installation.

Device Support
==============

This ZenPack has been tested against Version 0.4.0 of the twemproxy package.


Change History
==============
* 1.0.0
   * Initial Release

Screenshots
===========

See the screenshots directory.


.. External References Below. Nothing Below This Line Should Be Rendered

.. _Latest Package for Python 2.7: https://github.com/jcurry/ZenPacks.community.zplib.twemproxy/blob/master/dist/ZenPacks.community.zplib.twemproxy-1.0.0-py2.7.egg?raw=true

Acknowledgements
================

This ZenPack has been developed under contract to TuneIn Inc who have generously open-sourced
it to the community.

