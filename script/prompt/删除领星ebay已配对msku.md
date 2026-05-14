你用selenium帮我写个领星erp系统的用户批量分配店铺的rpa功能。
0. 代码存放路径：astpy\运维管理\删除领星ebay的msku配对数据.py
1. 数据来源：读取excel文档 D:\data\eBay删除已配对msku店铺清单.xlsx，文档只有一列：店铺简称。
2. 要操作的url地址：https://auxito.lingxing.com/erp/mmulti/pairList
3. 页面登录：系统需要登录的，我不会给你账号密码，你打开链接之后，你等待这个元素出现就行，每隔1秒钟检查一次。最多等待120秒。等待期间我会手动登录的。无法检测到这个元素则退出程序。
<div id="tab-1" aria-controls="pane-1" role="tab" tabindex="0" class="el-tabs__item is-top is-active" style="overflow: hidden; text-overflow: ellipsis;" inelement="0" aria-selected="true">已配对</div>
4. 操作动作：
4.1 从数据来源读取所有数据，逐个店铺操作，直到所有店铺都操作完成。
4.2 检查 页面显示行数，不是200行调整为200行，对应的元素：<div class="el-input el-input--small el-input--prefix el-input--suffix"><!----><input type="text" readonly="readonly" autocomplete="off" placeholder="" class="el-input__inner" inelement="0"><!----><span class="el-input__prefix"><span class="fake-placeholder" style="display: none;"></span><span class="fake-select-label" style="display: none;">
        200条/页
      </span><span class="fake-placeholder fake-placeholder-hidden">200条/页</span><span class="el-input__follow">
        
      </span><!----></span><span class="el-input__suffix"><span class="el-input__suffix-inner"><!----><!----><i class="el-select__caret el-input__icon iconfont lx_arrow_down_rev is-reverse"></i><!----><!----><!----><!----></span><!----></span><!----><!----></div>
4.3 确认是否切换到【已配对】页面，没有的话，则点击。对应元素：<div id="tab-1" aria-controls="pane-1" role="tab" tabindex="0" class="el-tabs__item is-top is-active" style="overflow: hidden; text-overflow: ellipsis;" inelement="0" aria-selected="true">已配对</div>
4.4 搜索店铺数据：每个店铺简称需要增加前缀“[eBay].”，然后输入到这个元素，回车进行查询。<div class="el-select__tags collapse-tags" style="max-width: 268px;"><span class="no-backgroud oneline el-tag el-tag--info el-tag--small el-tag--light"><span class="el-select__tags-text">[eBay].EPZ</span></span><!----><!----><!----></div>
只要这个table有数据就要执行删除。<table xid="71" cellspacing="0" cellpadding="0" border="0" class="vxe-table--body" style="width: 2178px; margin-top: 0px;">

4.5 删除动作：
勾选：<span class="vxe-checkbox--icon vxe-checkbox--unchecked-icon"></span>
点击删除：<button data-v-d8b00b82="" type="button" data-auth="auth-button" class="el-button el-button--default el-button--small is-round"><span class="el-tooltip text-wrap" aria-describedby="el-tooltip-6522" tabindex="-1"> 删除 </span></button>
确认删除：<button type="button" data-auth="auth-button" class="el-button el-button--danger el-button--small is-round"><span class="el-tooltip text-wrap" aria-describedby="el-tooltip-6121" tabindex="-1">删除
        <!----></span></button>
等待页面删除完成，刷新完成。可以检查这个元素没有被选中即可：<span class="vxe-checkbox--icon vxe-checkbox--unchecked-icon"></span>
一个店铺的数据全部删除之后，就可以进入下一个店铺处理。



5. 所有店铺处理完成之后，等待120秒才能退出程序

环境信息及开发要求：
1. 我的电脑已经安装好python，selenium，chrome和chromedriver.exe(chromedriver.exe路径是D:\data\chromedriver.exe)，你在此项目的venv中执行代码即可。
2. 我授权你运行代码，使用chromedriver。
3. 你可以编写代码和测试了。
4. 你复制 astpy\运维管理\template_script\rpa.py 这个脚本为基础，在action后面继续补全代码即可，运行代码直接实例化类，调用run方法即可。

