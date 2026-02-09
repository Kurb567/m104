import config as x
import requests 
import json 
import time


URL_PANEL_POLAND = x.URL_PANEL_POLAND
URL_PANEL_NEEDERLAND = x.URL_PANEL_NEEDERLAND
USER_NAME_PANEL = x.USER_NAME_PANEL
PANEL_PASSWORD = x.PANEL_PASSWORD
url = URL_PANEL_POLAND
session = requests.Session()
session.post(f"{url}/login", data={"username": USER_NAME_PANEL, "password": PANEL_PASSWORD})

r = session.get(f"{url}/panel/api/inbounds/list").json()
for i in range(10000):
    tgId = r['obj'][i]['clientStats'][0]['email']
    settings = json.loads(r['obj'][i]['settings'])
    expiryTime = settings['clients'][0]['expiryTime']
    port = r['obj'][i]['port']

    try:
        int(tgId)
        str(tgId) 
    except: continue 