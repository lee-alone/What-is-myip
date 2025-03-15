import socket
import psutil

def get_local_ips():
    ip_dict = {}
    
    # 获取所有网络接口
    for interface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            # 只获取IPv4地址
            if addr.family == socket.AF_INET:
                # 排除虚拟机和回环地址
                if not interface.startswith(('vmnet', 'vEthernet')) and addr.address != '127.0.0.1':
                    ip_dict[interface] = addr.address
    
    return ip_dict
