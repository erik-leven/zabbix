import requests
import json
from flask import Flask,jsonify
import os
import logging



app = Flask(__name__)
logger = logging.getLogger('Zabbix_integrator')
logger.setLevel({"INFO": logging.INFO,
                 "DEBUG": logging.DEBUG,
                 "WARNING": logging.WARNING,
                 "ERROR": logging.ERROR}.get(os.getenv("LOG_LEVEL", "INFO")))  # Default log level: INFO

stdout_handler = logging.StreamHandler()
stdout_handler.setFormatter(logging.Formatter('%(name)s - %(levelname)s - %(message)s'))
logger.addHandler(stdout_handler)

subscription = os.environ.get("SUBSCRIPTION")
sesam_jwt = os.environ.get("SESAM_JWT")
zabbix_server = os.environ.get("ZABBIX_SERVER")
zabbix_ip = os.environ.get("ZABBIX_IP")

user = os.environ.get("USER")
password = os.environ.get("PASSWORD")
host_name = os.environ.get("HOST_NAME")


@app.route("/notifications", methods=["GET","POST"])
def main():
    login_data = get_login_data(user, password)
    token = get_token(login_data)
    notifications = get_notifications(sesam_jwt)
    host_data = create_host_data(token, host_name)
    host_id = get_host_id(host_data)
    # getting node status from /health API
    node_value = get_node_health()
    node_item_data = create_item_data(token, "node-health", "node-health", host_id)
    create_item(node_item_data)
    push_data("node-health", node_value)

    for notification in notifications:
        if notification['_deleted'] == True:
            continue
        try:
            item_name = notification['pipe_id']
            req = get_extended_notification(notification['pipe_id'])
        except KeyError:
            item_name = "node-health"
            continue
        value = find_value(notification['status'], item_name, req)
        item_data = create_item_data(token, item_name, item_name, host_id) 
        print(item_data)
        create_item(item_data)
        push_data(item_name, value)
    return jsonify(notifications)

def get_node_health():
    req = requests.get(url="https://sesam.bouvet.no/api/health".format(subscription), headers={'Authorization': 'bearer {}'.format(sesam_jwt)}, verify=False).json()
    if req["status"] == "ok":
        return 1
    else:
        logger.error("Unexpected response status code: %d with response text %s" % (req.status_code, req.text))
        return 4

def find_value(status, item_name, notification = None):
    if status == "ok":
        return 1
    if notification['name'] == "Read errors time":
        return 2
    if notification['name'] == "Write errors time":
        return 2
    if notification['name'] == "Pump failed":
        return 3

def get_extended_notification(pipe_name):
    req = requests.get(url="https://portal.sesam.io/api/subscriptions/{}/pipes/{}/notification-rules".format(subscription, pipe_name), timeout=180, headers={'Authorization': 'bearer {}'.format(sesam_jwt)}, verify=False)
    if req.status_code != 200:
            logger.error("Unexpected response status code: %d with response text %s" % (req.status_code, req.text))
            raise AssertionError("Unexpected response status code: %d with response text %s" % (req.status_code, req.text))
    return req.json()[0]

def push_data(item_key, value):
    os.system('zabbix_sender -z {} -s "{}" -k {} -o {}'.format(zabbix_ip, host_name, item_key, value))

def get_host_id(host_data):
    req = requests.get(url= "http://" + zabbix_server + "/zabbix/api_jsonrpc.php", data=json.dumps(host_data),headers={'Content-Type':'application/json'})
    if req.status_code != 200:
            logger.error("Unexpected response status code: %d with response text %s" % (req.status_code, req.text))
            raise AssertionError("Unexpected response status code: %d with response text %s" % (req.status_code, req.text))
    try:
        return json.loads(req.text)['result'][0]['hostid']
    except Exception as e:
        logger.error("Unexpected error {}".format(e))
        raise AssertionError("Unexpected error {}".format(e))

def create_host_data(token, host_name):
    return {
            "jsonrpc": "2.0",
            "method": "host.get",
            "params": {
                "filter": {
                    "host": [
                        host_name
                    ]
                }
            },
            "auth": token,
            "id": 1
            }
    req = requests.get("http://zabbix-test.bouvet.no/zabbix/api_jsonrpc.php",data=json.dumps(host_data),headers={'Content-Type':'application/json'})

def create_item_data(token, item_name, item_key, host_id):
    return {
            "jsonrpc": "2.0",
            "method": "item.create",
            "params": {
                "name": item_name,
                "key_": item_key,
                "key": item_key,
                "hostid": host_id,
                "type": 2,
                "value_type": 3,
                "interfaceid": "1",
                "delay": "10s"
            },
            "auth": token,
            "id": 1
            }

def get_login_data(user, password):
    return {
            "id":1,
            "jsonrpc":"2.0",
            "method":"user.login",
            "auth": None,
            "params":{"user":user,"password":password}
            }

def get_token(login_data):
    req = requests.get(url=  "http://" + zabbix_server + "/zabbix/api_jsonrpc.php", data=json.dumps(login_data),headers={'Content-Type':'application/json'})
    if req.status_code != 200:
            logger.error("Unexpected response status code: %d with response text %s" % (req.status_code, req.text))
            raise AssertionError("Unexpected response status code: %d with response text %s" % (req.status_code, req.text))
    return json.loads(req.text)['result']

def get_notifications(sesam_jwt):
    req = requests.get(url="https://portal.sesam.io/api/notifications-summary", timeout=180, headers={'Authorization': 'bearer {}'.format(sesam_jwt)}, verify=False)
    if req.status_code != 200:
            logger.error("Unexpected response status code: %d with response text %s" % (req.status_code, req.text))
            raise AssertionError("Unexpected response status code: %d with response text %s" % (req.status_code, req.text))
    return req.json()

def create_item(item_data):
    req = requests.post(url = "http://" + zabbix_server + "/zabbix/api_jsonrpc.php",data=json.dumps(item_data),headers={'Content-Type':'application/json'})
    if req.status_code != 200:
            logger.error("Unexpected response status code: %d with response text %s" % (req.status_code, req.text))
            raise AssertionError("Unexpected response status code: %d with response text %s" % (req.status_code, req.text))
    return None



if __name__ == '__main__':
    #main()
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)