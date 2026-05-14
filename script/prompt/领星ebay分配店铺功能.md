你用selenium帮我写个领星erp系统的用户批量分配店铺的rpa功能。
1. 数据来源：读取excel文档（我的文档\a.xlsx），文档中有两列：姓名，授权店铺。授权店铺可能有多个，用逗号分隔（可能有多余的空格，注意清理掉空格）。
2. 登录：系统需要登录的，我不会给你账号密码，在需要登录的时候你等待我登录即可。
3. 分配店铺：先根据人名搜索，确认搜索出来的结果只有一行数据，且名字是对应的。检查完成就可以勾选改行数据，点击上方的【批量】下拉按钮，选择下拉菜单中的【分配店铺】。
4. 在弹出的对话框中，点击ebay，根据excel文档中的授权店铺逐个勾选，然后点击确定即可完成。
5. 完成一个用户后，继续下一个用户，直到所有用户完成。
我的电脑已经安装好python，selenium，chrome和chromedriver.exe(chromedriver.exe路径是D:\data\chromedriver.exe)，你在此项目的venv中执行代码即可。
我授权你运行代码，使用chromedriver。
你可以开始编写代码和测试了。
代码文件你放在astpy\运维管理\ebay店铺授权.py
领星erp的url：https://auxito.lingxing.com/erp/muser/userManage?wsRefresh=1

