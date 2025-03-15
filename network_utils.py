import asyncio
import aiohttp
import json
import re
from typing import List, Dict, Any

async def fetch_ip_info(session: aiohttp.ClientSession, endpoint: Dict[str, str]) -> Dict[str, Any]:
    try:
        async with session.get(endpoint['url'], timeout=5) as response:
            if response.status == 200:
                try:
                    text = await response.text()
                    ip_address = 'N/A'
                    
                    # 处理默认端点
                    if endpoint['name'] == 'IPInfo.io':
                        try:
                            json_data = json.loads(text)
                            ip_address = json_data.get('ip', 'N/A')
                        except json.JSONDecodeError:
                            pass
                            
                    elif endpoint['name'] == 'My-IP.io':
                        try:
                            json_data = json.loads(text)
                            # 检查两种可能的IP地址字段
                            ip_address = json_data.get('ip', None)
                            if isinstance(ip_address, dict):
                                ip_address = ip_address.get('address', 'N/A')
                            elif not ip_address:
                                ip_address = 'N/A'
                        except json.JSONDecodeError:
                            pass
                            
                    elif endpoint['name'] == 'DynDNS':
                        match = re.search(r'Current IP Address: (\d+\.\d+\.\d+\.\d+)', text)
                        if match:
                            ip_address = match.group(1)
                            
                    elif endpoint['name'] == 'MyIP.com':
                        try:
                            json_data = json.loads(text)
                            ip_address = json_data.get('ip', 'N/A')
                        except json.JSONDecodeError:
                            pass
                    
                    # 处理自定义端点 - 直接显示原始响应
                    else:
                        ip_address = text.strip()
                    
                    return {
                        'name': endpoint['name'],
                        'ip': ip_address,
                        'server': response.headers.get('Server', 'N/A'),
                        'status': 'success'
                    }
                    
                except Exception as e:
                    return {
                        'name': endpoint['name'],
                        'ip': 'N/A',
                        'server': str(e),
                        'status': 'error'
                    }
    except Exception as e:
        return {
            'name': endpoint['name'],
            'ip': '查询失败',
            'server': str(e),
            'status': 'error'
        }

async def check_all_ips(endpoints: List[Dict[str, str]]):
    # 分离默认端点和自定义端点
    default_endpoints = [ep for ep in endpoints if ep['name'] in ['IPInfo.io', 'My-IP.io', 'DynDNS', 'MyIP.com']]
    custom_endpoints = [ep for ep in endpoints if ep['name'] not in ['IPInfo.io', 'My-IP.io', 'DynDNS', 'MyIP.com']]
    
    async with aiohttp.ClientSession() as session:
        # 首先并发查询所有默认端点
        default_tasks = [fetch_ip_info(session, endpoint) for endpoint in default_endpoints]
        default_results = await asyncio.gather(*default_tasks)
        for result in default_results:
            yield result
        
        # 然后并发查询所有自定义端点
        if custom_endpoints:
            custom_tasks = [fetch_ip_info(session, endpoint) for endpoint in custom_endpoints]
            custom_results = await asyncio.gather(*custom_tasks)
            for result in custom_results:
                yield result