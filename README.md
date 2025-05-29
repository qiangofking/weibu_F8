# weibu_F8
weibu query on Windows based on Python by shortcut key🖐🖐🖐
基于python，windows上的微步快捷键查询

### 原理
模拟ctrl+c复制，读取文本正则匹配IP，依次遍历查询

### 配置
1. 需使用微步的API key，请在query.py，16行配置
2. 微步需配置出口IP，如自建代理，请在query.py，8-9行配置
![image](https://github.com/user-attachments/assets/6e3b6e93-1e84-40cb-bbd9-c24a3df6e64d)



### 安装
```
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 启动（启动后命令行别关，快捷键全局监听）
```
python hotkey.py
```

### 快捷键
F8——识别选中文本——hotkey，75行修改
esc——关闭结果窗口——display，83行修改

### 功能模块独立验证

```
python query.py 8.8.8.8

{
  "ip": "8.8.8.8",
  "severity": "无威胁",
  "judgments": "白名单, CDN服务器, 网关",
  "is_malicious": false,
  "asn_info": "GOOGLE (AS15169)",
  "location": "美国 ",
  "carrier": "谷歌公司",
  "permalink": "https://x.threatbook.com/v5/ip/8.8.8.8"
}
```

```
echo {"results": [{"ip": "8.8.8.8", "severity": "无威胁", "judgments": "白名单, CDN服务器, 网关", "is_malicious": false, "asn_info": "GOOGLE (AS15169)", "location": "美国 ", "carrier": "谷歌公司", "permalink": "https://x.threatbook.com/v5/ip/8.8.8.8"}]} | python display.py
```
