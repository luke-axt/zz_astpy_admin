你用selenium帮我写个领星erp系统的用户批量分配店铺的rpa功能。
1. 数据来源：读取excel文档（D:\data\eBay配置通途订单规则的店铺清单.xlsx），文档中只有一列：店铺简称。
2. 网页地址：https://tuyao.tongtool.com/myaccount/orderrule/index.htm。系统需要登录的，我不会给你账号密码，你在需要登录的时候等待我登录即可。
3. 操作流程：我会在登录之后，协助你点击页面到操作页面。（正式运行的时候我会打断点调试运行的。），然后程序执行动作。
4. 程序需要做的动作：逐行根据店铺简称，在页面查找对应的店铺，并勾选即可。页面元素参考如下，搜索的时候用 店铺简称+中文帐号，比如EAD店铺就输入EAD帐号可以精确搜索。
<span class="ml5 mt3 dbl w290">
									<input type="checkbox" class="wh14" id="6160008913201706270000149854" groupnameid="8179008913202110200000980087" name="ebayAccountIdebay" onclick="selectedEbayAccountChecked('6160008913201706270000149854','ebay')">
										<span class="mr10">top-autotech(EAD帐号)</span>
									
								</span>

我的电脑已经安装好python，selenium，chrome和chromedriver.exe(chromedriver.exe路径是D:\data\chromedriver.exe)，你在此项目的venv中执行代码即可。
我授权你运行代码，使用chromedriver。
你可以开始编写代码和测试了。
代码文件你放在astpy\运维管理\通途自动订单规则添加店铺.py

