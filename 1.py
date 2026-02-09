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

    session = requests.Session()
    session.post(f"{URL_PANEL_NEEDERLAND}/login", data={"username": USER_NAME_PANEL, "password": PANEL_PASSWORD})
    data = {
    "id": 0,  # 0 для нового инбаунда
    "userId": tgId,
    "up": 0,
    "down": 0,
    "total": 0,
    "allTime": 0,
    "remark": "",
    "enable": True,
    "expiryTime": 0,
    "trafficReset": "never",
    "lastTrafficResetTime": 0,
    "listen": "",
    "port": port,
    "protocol": "vless",
    "settings": json.dumps({
        "clients": [
            {
                "id": tgId,
                "security": "",
                "password": "",
                "flow": "xtls-rprx-vision",
                "email": tgId,  # email пользователя
                "limitIp": 0,
                "totalGB": 0,
                "expiryTime": expiryTime,  # время истечения
                "enable": True,
                "tgId": tgId,
                "subId": f'{tgId}-{port}',
                "comment": "",
                "reset": 0,
                "created_at": int(time.time() * 1000),
                "updated_at": int(time.time() * 1000)
            }
        ],
        "decryption": "none",
        "encryption": "none",
        "testseed": [900, 500, 900, 256]
    }, ensure_ascii=False),
    "streamSettings": json.dumps({
        "network": "tcp",
        "security": "reality",
        "externalProxy": [],
        "realitySettings": {
            "show": False,
            "xver": 0,
            "target": "api.vk.ru:443",
            "serverNames": ["api.vk.ru"],
            "privateKey": "AMKU-qwbEL9I-HgmFJyN_wWb0OCeGB3WMkDlvG6eT2g",
            "minClientVer": "",
            "maxClientVer": "",
            "maxTimediff": 0,
            "shortIds": [
                "30288ee8", "4d", "b81ef2", "4b9d", "fbe9984473bb",
                "5c8a987746627fa3", "e622c3039e", "5185906a2999da"
            ],
            "mldsa65Seed": "",
            "settings": {
                "publicKey": "MnNd4UgtPfmeBLDcYGUunP9CkdauibvF8Bb9owlyFFQ",
                "fingerprint": "chrome",
                "serverName": "",
                "spiderX": "/",
                "mldsa65Verify": ""
            }
        },
        "tcpSettings": {
            "acceptProxyProtocol": False,
            "header": {
                "type": "none"
            }
        }
    }, ensure_ascii=False),
    "tag": "inbound-443",
    "sniffing": json.dumps({
        "enabled": False,
        "destOverride": ["http", "tls", "quic", "fakedns"],
        "metadataOnly": False,
        "routeOnly": False
    }, ensure_ascii=False),
    "clientStats": [
        {
            "id": int(tgId),
            "inboundId": 0,
            "enable": True,
            "email": tgId,
            "uuid": tgId,
            "subId": f'{tgId}-{port}',
            "up": 0,
            "down": 0,
            "allTime": 0,
            "expiryTime": expiryTime,
            "total": 0,
            "reset": 0,
            "lastOnline": 0
        }
    ]}

    response = session.post(f"{URL_PANEL_NEEDERLAND}/panel/api/inbounds/add", json=data)
    print(response.json()['success'])
         
        