Sesam-Bouvet-Zabbix service

This microservice (MS) allows for notifications and node health data from Sesam to be pushed to Zabbix through the third party agent ’Zabbix sender’ in order to monitor integration stoppage/errors.

Prerequisites:
    • Sesam node
    • Notifications active on relevant pipes
    • Zabbix server available and firewall opened for the node.

MS work flow:
    • MS in uploaded as a system in the Sesam node. The Sesam system config supplies the code with environmental variables and secrets in order to authenticate and locate the correct Zabbix server info. 
    • The MS logs in to Zabbix with username/password and receives an access token back
    • The MS retrieves the notification summary through a Sesam API
    • Through the access token the MS collects the host id info necessary to push data to the correct host
    • For each notification from Sesam the MS collects additional notification data from Sesam.
    • For each notification the MS assorts a ’criticality value’ to be pushed to Zabbix.
    • For each notification the MS creates a corresponding trapper item in Zabbix to which the Zabbix sender software pushes the required data.

Zabbix work flow to display Sesam data:
    • The data is available inside the items in the specified host (configuration --> host --> item)
    • In the host page, enter ’Graphs’ and select ’Create Graph’. Choose the trigger item correspondng to the data you wish to display (all trigger items are named after their notification name in addition to ’node-health’, ie. ’bouvet’event’ or ’catalystone-user’).
    • Once the graph is created, enter ’Monitoring’ and select ’Graphs’ and choose the newly selected graph to display data.

Data information:
    • The MS can be set to push data from the node at any given interval (every 5 min right now). At this moment this is set ny the activation pipe in Sesam, but will in the future be an integral part of the MS.

TODO:
    • Activate more MS tests in order to easely handle errors.
    • Add cron-expression handling in Dockerfile.
    • Follow up on ’criticality values’.
    • Thourough testing.
    • System config and notification examples.
    • Upload to Prod-node
