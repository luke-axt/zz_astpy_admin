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
