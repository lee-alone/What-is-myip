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
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_ip_info(session, endpoint) for endpoint in endpoints]
        results = await asyncio.gather(*tasks)
        for result in results:
            yield result