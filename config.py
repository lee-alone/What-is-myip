import json
import os

DEFAULT_API_ENDPOINTS = [
     {
        "name": "IPInfo.io",
        "url": "https://ipinfo.io/json"
    },
    {
        "name": "My-IP.io",
        "url": "https://api.my-ip.io/v2/ip.json"
    },
        {
        "name": "DynDNS",
        "url": "http://checkip.dyndns.org/"
    },
    {
        "name": "MyIP.com",
        "url": "https://api.myip.com"
    }
    
    ]

def load_custom_endpoints():
    try:
        config_path = "custom_endpoints.json"
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"读取自定义配置失败: {str(e)}")
    return []
