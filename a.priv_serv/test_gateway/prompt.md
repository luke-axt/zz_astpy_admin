# 需求描述

这是一个测试网关类。我希望用于测试外网能否穿透到内网，我会在外网调用请求访问API。

你帮写一个基于fastapi的一个接口就好了，调用接口无需入参，接口直接返回【当前时间YYYY-MM-DD HH:MM:SS】+【aaa】

你写好之后，给我提供一个调用该接口的测试方法、启动网关的命令等测试相关的文档。

测试脚本写在同目录下的 test.py


# 完整的部署流程：

python -m venv venv
venv\Scripts\Activate.ps1
pip install -r a.priv_serv\test_gateway\requirements.txt
cd .\a.priv_serv\test_gateway\
uvicorn main:app --host 0.0.0.0 --port 25666

# 测试代码

```
import urllib.request
import json

URL = "http://192.168.110.9:8000/"


def test_gateway():
    req = urllib.request.Request(URL, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            print("状态码:", resp.status)
            print("响应内容:", data)
            return data
    except Exception as e:
        print("请求失败:", e)
        raise


if __name__ == "__main__":
    test_gateway()


```