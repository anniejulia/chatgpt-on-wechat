import json
import datetime
import requests
from config import conf, load_config

def getRequest(url, interface, params, headers):
    try:
        interface_url = url + interface
        res = requests.get(url=interface_url, params=params, headers=headers)
        json_response = json.loads(res.content)
        return json_response
    except Exception as err:
        print(err)

def postRequest(url, interface, json_post, headers):
    try:
        interface_url = url + interface
        res = requests.post(url=interface_url, data=json.dumps(json_post), headers=headers)
        json_response = json.loads(res.content)
        return json_response
    except Exception as err:
        print(err)

class XMindAi(object):
    def __init__(self):
        self.active = conf().get("use_xmindai", False)
        self.clientId = conf().get("xmindai_clientId", "") #"1609df70-3e1e-4cd0-b476-f96024c20071"
        self.clientSecret = conf().get("xmindai_clientSecret","") #"v7cCPJFZLVnOjUSBrZYFFLA/qf35uZwbqhGOUVPXPqXRzghNUgAnWC0qjokz9LLPF7SLw8h3D0Ftf+BK+8NMgA=="
    
    def getToken(self):
        if self.active == False:
            return
        
        url = "https://login.xmindai.com/api/Common/"
        interface = "Verification"
        params ={}
        params["clientId"] = self.clientId
        params["clientSecret"] = self.clientSecret
        headers = {}
        result = getRequest(url=url, interface=interface, params=params, headers=headers)
        self.access_token = result["access_Token"]
        self.refresh_Token = result["refresh_Token"]
        self.expires_in = int(result["expires_in"])

    def getServerTime(self):
        if self.active == False:
            return
        url = "https://login.xmindai.com/api/Common/"
        interface = "CurrentTimeStamp"
        params = {}
        headers = {}
        headers["Authorization"] = f"Bearer {self.access_token}"
        result = getRequest(url=url, interface=interface, params=params, headers=headers)
        return int(result)

    def flushtoken(self):
        if self.active == False:
            return
        current_time = self.getServerTime()
        if current_time < self.expires_in + 5 * 60 *1000:
            self.getToken()

    def chat(self, messages, custom):
        if self.active == False:
            return
        self.flushtoken()
        now_timestamp = str(int(datetime.datetime.now().timestamp()*1000))
        params = {}
        headers = {}
        headers["Authorization"] = f"Bearer {self.access_token}"
        headers["Content-Type"] = "application/json"
        url = "https://cognitive.xmindai.com/api/OpenAI/Chat/"
        interface = "Completions"
        params["timeStamp"] = now_timestamp
        params["tppBizNo"] =  "1609df70-1"
        params["endUser"] =  "man1"
        params["messages"] = messages
        params["model"] = 1
        params["temperature"] = conf().get("temperature", 0.9)
        params["top_p"] = 1
        params["n"] = 1
        params["stream"] = False
        params["max_tokens"] = conf().get("conversation_max_tokens", 1000)
        params["presence_penalty"] = conf().get("presence_penalty", 0.0)
        params["frequency_penalty"] = conf().get("frequency_penalty", 0.0)
        params["user"]=custom

        result = postRequest(url=url, interface=interface, json_post=params, headers=headers)
        return result

