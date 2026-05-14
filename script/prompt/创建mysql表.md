请根据以下基础字段信息帮我创建mysql的表，要求如下：
1. 表名：astdc.dc_log_lx2tt_szinv
2.字符集用 utf8mb4,排序规则用utf8mb4_bin，使用innodb引擎.
3. 字段类型尽量用int、varchar、text,datetime 等简单类型，不要用json、blob等复杂类型
4. remark用 text 类型.
5. 帮我添加一个id字段作为自增主键
6. 给orderIdKey添加一个唯一索引


基础字段信息
'orderIdKey':tt_order['orderIdKey']
,'orderIdCode':tt_order['orderIdCode']
,'isInvalid':isInvalid
,'tt_order_updatedTime':tt_order['updatedTime']
,'remark':''
,'lx_outbound_status': '0'
,'lx_outbound_no': None
,'lx_outbound_time':None 
,'tt_inbound_no': None
,'tt_inbound_time':None 
,'tt_inbound_status': '0' # 通途入库单状态，0-未入库，1-已入库
,'lx_outbound_cancel_status':'0' # 领星出库单是否作废，0-未作废，1-作废，只有订单作废了，并且领星已经操作出库了才需要更新
,'lx_outbound_cancel_time':None # 领星出库单作废时间
,'tt_outbound_no': None # 出库单号，只有订单作废并且创建通途出库订单成功才更新此字段
,'tt_outbound_time':None 
,'tt_outbound_status':'0' # 通途出库单状态，0-未出库，1-已出库
,'tt_sku_detail':self._parse_tt_order_sku_info(tt_order['goodsInfo']['tongToolGoodsInfoList'])
,'lx_inv_info':None   # 领星库存信息，这个字段在扣库存成功之后再更新，包含sku、库位、数量
,'platformCode':tt_order['platformCode']
,'saleMode':tt_order['saleMode']
,'saleTime':tt_order['saleTime']
,'import_time':DatePack.getCurtime()