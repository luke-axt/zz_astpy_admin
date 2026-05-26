
这是一个测试网关类。我希望用于测试外网能否穿透到内网，我会在外网调用请求访问API。

你帮写一个基于fastapi的一个接口就好了，调用接口无需入参，接口直接返回【当前时间YYYY-MM-DD HH:MM:SS】+【aaa】

你写好之后，给我提供一个调用该接口的测试方法、启动网关的命令等测试相关的文档。

测试脚本写在同目录下的 test.py


 pip install -r a.priv_serv\test_gateway\requirements.txt
 cd .\a.priv_serv\test_gateway\
 uvicorn main:app --host 0.0.0.0 --port 8000
 