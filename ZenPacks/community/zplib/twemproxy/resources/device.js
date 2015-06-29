Ext.onReady(function() {
    var DEVICE_OVERVIEW_ID = 'deviceoverviewpanel_idsummary';
    Ext.ComponentMgr.onAvailable(DEVICE_OVERVIEW_ID, function(){
        var overview = Ext.getCmp(DEVICE_OVERVIEW_ID);

        overview.addField({
            name: 'twemproxy_version',
            fieldLabel: _t('twemproxy version')
        });

        overview.addField({
            name: 'twemproxy_uptime',
            fieldLabel: _t('twemproxy uptime (days)')
        });

        overview.addField({
            name: 'twemproxy_curr_connections',
            fieldLabel: _t('twemproxy current connections')
        });

    });
});
