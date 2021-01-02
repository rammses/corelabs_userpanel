import requests
import json

def get_lab_status(gns3_server_ip, lab_uuid):
    uri = 'http://' + str(gns3_server_ip) + ':3080/v2/projects/' + lab_uuid
    # print(uri)
    response = requests.get(uri)
    details = json.loads(response.content)
    if details['status'] == 'opened':
        return True
    else:
        return False
