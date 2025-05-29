import requests
import json
import sys
import socks
import socket

# 设置SOCKS代理
socks.set_default_proxy(socks.SOCKS5, "x.x.x.x", xxxx, username='xxxx', password='xxxxxxx')
socket.socket = socks.socksocket

def query_ip(ip):
    """查询IP威胁情报并返回格式化结果"""
    try:
        url = "https://api.threatbook.cn/v3/scene/ip_reputation"
        query = {
            "apikey": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            "resource": ip,
            "lang": "zh"
        }
        
        session = requests.Session()
        response = session.get(url, params=query, timeout=10)
        response.raise_for_status()

        data = response.json()
        
        if data.get('response_code') != 0:
            return f"查询失败: {data.get('verbose_msg', '未知错误')}"
            
        ip_data = data['data'].get(ip, {})
        result = {
            'ip': ip,
            'severity': ip_data.get('severity', '未知'),
            'judgments': ', '.join(ip_data.get('judgments', [])),
            'is_malicious': ip_data.get('is_malicious', False),
            'asn_info': f"{ip_data.get('asn', {}).get('info', '未知')} (AS{ip_data.get('asn', {}).get('number', '')})",
            'location': f"{ip_data.get('basic', {}).get('location', {}).get('country', '')} {ip_data.get('basic', {}).get('location', {}).get('city', '')}",
            'carrier': ip_data.get('basic', {}).get('carrier', '未知'),
            'permalink': ip_data.get('permalink', '')
        }
        return json.dumps(result, indent=2, ensure_ascii=False)
        
    except requests.exceptions.RequestException as e:
        return f"网络请求错误: {str(e)}"
    except Exception as e:
        return f"处理错误: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        ip = sys.argv[1]
        print(query_ip(ip))
    else:
        print(json.dumps({"error": "未提供IP地址"}))

