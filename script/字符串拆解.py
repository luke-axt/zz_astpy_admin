
t_str = """
amz
 concat(t1.amazon_order_id,'_',t1.sid) as order_key
      ,'AMZFBA' as data_src
      ,left(t1.purchase_date_local ,10) as order_dt
      ,t5.country as country
      ,'amz' as sale_platform
      ,t1.amazon_order_id as ordercode
      ,t1.amazon_order_id as ordercode_origin
      ,t1.sid as shopid
      ,t1.seller_name  as shopname
      ,t1.order_status as order_status
      ,t1.postal_code as postal_code
      ,null as state
      ,null as city
      ,null as full_addr
      ,null as buyer_id
      ,t1.order_total_currency_code as currency_cd
      ,t1.refund_amount as refund_amount
      ,t1.is_assessed as is_assessed
      ,t1.is_return as is_return
      ,t1.is_mcf_order as is_mcf_order
      ,t1.is_replaced_order as is_replaced_order
      ,concat('AMZ-',t1.fulfillment_channel) as order_type 
      ,DATE_ADD(STR_TO_DATE(t1.purchase_date_local_utc,'%Y-%m-%d %H:%i:%s') ,INTERVAL 8 HOUR) as purchase_date
      ,DATE_ADD(STR_TO_DATE(t1.posted_date_utc,'%Y-%m-%d %H:%i:%s') ,INTERVAL 8 HOUR) as paid_date
      ,DATE_ADD(STR_TO_DATE(t1.shipment_date_utc,'%Y-%m-%d %H:%i:%s') ,INTERVAL 8 HOUR) AS shipment_date
      ,DATE_ADD(STR_TO_DATE(t1.gmt_modified_utc,'%Y-%m-%d %H:%i:%s') ,INTERVAL 8 HOUR) as modified_date
      ,now() as etl_time
      
tt自发货
ifnull(t1.orderidcode,t1.salesRecordNumber) order_key
	  ,'TTZFH' as data_src
	  ,date_format( t1.saleTime,'%Y-%m-%d') as order_dt
	  ,ifnull(t3.country,t1.buyerCountry) as country
	  ,t1.platformCode as sale_platform
	  ,SUBSTRING_INDEX(ifnull(t1.orderidcode,t1.salesRecordNumber),'_',1) as ordercode
	  ,ifnull(t1.orderidcode,t1.salesRecordNumber) as ordercode_origin
	  ,t1.saleAccount as shopid
	  ,t1.saleAccount as shopname
	  ,t1.orderStatus as order_status
	  ,t1.postalCode as postal_code
	  ,ifnull(t4.codename,upper(t1.buyerState)) as state
	  ,t1.buyerCity as city
	  ,t1.receiveAddress as full_addr
	  ,t1.buyerAccountId as buyerAccountId
	  ,t1.buyerEmail as buyerEmail
	  ,t1.buyerMobile as buyerMobile
	  ,t1.buyerName as buyerName
	  ,t1.buyerPhone as buyerPhone
	  ,t1.orderAmount as orderAmount
	  ,t1.orderAmountCurrency as orderAmountCurrency
	  ,ifnull(t1.isInvalid,'0') as isInvalid 
	  ,t1.isRefunded as isRefunded
	  ,t1.webstoreOrderId as platform_ordercode
	  ,t1.paidTime as paidTime
	  ,t1.saleTime as saleTime
	  ,t1.updatedTime as updatedTime
	  ,now() as etl_time

tt平台仓
ifnull(t1.orderidkey,'') as order_key
	  ,'通途平台仓' as data_src
	  ,date_format( t1.saleTime,'%Y-%m-%d') as order_dt
	  ,ifnull(t8.country ,t1.buyerCountry) as country
	  ,t1.platformCode as sale_platform
	  ,ifnull(t1.orderidcode,'') as ordercode
	  ,ifnull(t1.orderidcode,'') as ordercode_origin
	  ,t1.saleAccount as shopid
	  ,t1.saleAccount as shopname
	  ,t1.orderStatus as order_status
	  ,t1.postalCode as postal_code
	  ,ifnull(t4.codename,upper(t1.buyerState)) as state
	  ,t1.buyerCity as city
	  ,t1.receiveAddress as full_addr
	  ,t1.buyerAccountId as buyerAccountId
	  ,t1.buyerEmail as buyerEmail
	  ,t1.buyerMobile as buyerMobile
	  ,t1.buyerName as buyerName
	  ,t1.buyerPhone as buyerPhone
	  ,t1.orderAmount as orderAmount
	  ,t1.orderAmountCurrency as orderAmountCurrency
	  ,ifnull(t1.isInvalid,'0') as isInvalid 
	  ,t1.isRefunded as isRefunded
	  ,t1.webstoreOrderId as platform_ordercode
	  ,t1.paidTime as paidTime
	  ,t1.saleTime as saleTime
	  ,t1.updatedTime as updatedTime
	  ,now() as etl_time

amz多渠道
concat(t1.amazonOrderId,'_',t1.sid) as order_key
		,left(t2.purchaseDateLocal ,10) as order_dt
		,t1.country as country
		,'amz' as sale_platform
        ,t1.sellerFulfillmentOrderId  as ordercode
		,t1.sellerFulfillmentOrderId  as ordercode_origin
      	,ifnull(t1.sid,'') as shopid
      	,t1.storeName as shopname
	    ,t1.orderStatus as order_status
	    ,'' as postal_code
	    ,'' as state
	    ,'' as city
	    ,t1.remark as remark
	    ,t1.buyerName as buyerName,
	    DATE_ADD(STR_TO_DATE(t1.shipDateUtc,'%Y-%m-%d %H:%i:%s') ,INTERVAL 8 HOUR) as ship_date
	    ,t1.lastUpdateTime as lastUpdateTime
	    ,t1.purchaseDateLocal as  purchaseDate
      	,now() as etl_time
"""

for item in t_str.split('\n'):
    if item == '':
        continue
    item = item.strip().lstrip(' ').lstrip('\t')
    if ' as ' in item:
        print(f"{item} $ {item.split(' as ')[1]}")
    else:
        print(item)