import json
import sys
sys.path.insert(0, r"D:\app\astpy")

from utils.dateutil import DatePack
from utils.BrowserUtils import BrowserUtils

from common.ResultObj import ResultObj
from rpa.RpaAdmin import RpaAdmin
from CoreBussiness.LingXingService import LingXingService


class ImportLxPlatformMapDataUnmatch(RpaAdmin):

    def __init__(self, job_name):
        super().__init__(job_name)
        self.job_name = job_name

    def action(self,**kwargs) -> ResultObj:
        res = self.import_lx_sku_platform_unmatch()
        if res.is_fail():
            return res
        res = self.proc_lx_sku_ebay_multi_sku_map()
        self.print_result()
        return res


    def import_lx_sku_platform_unmatch(self):
        """
        采集领星平台sku未配对数据

        :return:
        """
        self.logger.info(f"ImportOsSkuMapData 开始 -------")
        lx_serv = LingXingService()
        code,msg,browser = lx_serv.loginChrome(self.admin.getChromeUserPath(self.job_name)
                                            ,self.admin.get_config()['lingxing']['rpa_usr']
                                            ,self.admin.decryptFernet(self.admin.get_config()['lingxing']['rpa_usr_pw'])
                                            )
        if code != 0:
            return ResultObj.error(ResultObj.FATAL_ERROR,f"打开浏览器失败。错误信息：{msg}")
        res = lx_serv.get_lx_jsapi_token(browser)
        if res.is_fail():
            return res
        lx_header = res.get_data()
        lx_header['X-AK-ENV-KEY'] = 'auxito'
        lx_header['X-AK-Zid'] = '1'
        all_data_cnt = 0
        offset = 0
        length = 1000
        self.dbs.delete("delete from astdc.lx_sku_platform_unmatch where 1=1;")
        while True:
            if offset % 3000 == 0:
                self.logger.info(f"offset:{offset} --- ")
            url = f'https://auxito.lingxing.com/api/platforms/product_pair/noPairList?offset={offset}&length={length}&req_time_sequence=%2Fapi%2Fplatforms%2Fproduct_pair%2FnoPairList$$2'
            param = f""
            res = BrowserUtils.jsapi(browser,url,param,'GET',lx_header)
            if res.is_fail():
                return res
            res_dict = json.loads(res.get_data())
            if res_dict['code'] != 1:
                return ResultObj.error(ResultObj.FATAL_ERROR,res.get_data())
            res_dict_data = res_dict.get('data',{}).get('list',[])
            all_data_cnt += len(res_dict_data)
            if len(res_dict_data) == 0:
                break
            for item in res_dict_data:
                item['datasyntime'] = DatePack.getCurtime()
                item['tmp_lx_sku'] = item['msku'].replace('*','_').replace('+','_').replace(':','_').replace('/','_')\
                    .replace('%','_').replace(',','_').replace('.','_').replace('(','_').replace(')','_')\
                    .replace('?','_').replace('#','_').replace(' ','_')


            self.dbs.insertmysql('insert','astdc.lx_sku_platform_unmatch',res_dict_data)
            if len(res_dict_data) < length:
                break
            offset += length

        if browser is not None:
            browser.quit()
        self.logger.info(f"完成，实际写入 {all_data_cnt} 行。")
        return ResultObj.success()

    def proc_lx_sku_ebay_multi_sku_map(self):
        """
        生成ebay平台捆绑产品的产品关系表，这个脚本的逻辑是最佳

        """
        sql = """
-- 以下脚本需要按顺序执行
--  US
INSERT INTO astdc.lx_sku_ebay_multi_sku_map
(msku, lx_msku_m, lx_local_sku, qty, country,status)
with t_msku as (
select distinct t.msku ,t.tmp_lx_sku  
  from astdc.lx_sku_platform_unmatch t
  left join astdc.lx_sku_ebay_multi_sku_map tt 
    on t.msku = tt.msku 
 where tt.id is null and t.msku not in ('','1')
)
select t1.msku,t1.tmp_lx_sku
      ,ifnull(t3.pfsku ,t2.tt_sku) as lx_local_sku
      ,t2.qty 
      ,t2.currency 
      ,'N'
  from t_msku t1 
  join clx.sz_组合产品表 t2 
    on t1.msku = t2.sku_multi 
  left join astdc.dc_oldprod_ref t3 
    on t2.tt_sku = t3.ttsku 
   and t3.platform = 'lx'
 where t2.currency = 'US';
   
-- 
-- ************ ************ ************ ************ ************ ************
--  UK
INSERT INTO astdc.lx_sku_ebay_multi_sku_map
(msku, lx_msku_m, lx_local_sku, qty, country,status)
with t_msku as (
select distinct t.msku ,t.tmp_lx_sku  
  from astdc.lx_sku_platform_unmatch t
  left join astdc.lx_sku_ebay_multi_sku_map tt 
    on t.msku = tt.msku 
 where tt.id is null and t.msku not in ('','1')
)
select t1.msku,t1.tmp_lx_sku
      ,ifnull(t3.pfsku ,t2.tt_sku) as lx_local_sku
      ,t2.qty 
      ,t2.currency 
      ,'N'
  from t_msku t1 
  join clx.sz_组合产品表 t2 
    on t1.msku = t2.sku_multi 
  left join astdc.dc_oldprod_ref t3 
    on t2.tt_sku = t3.ttsku 
   and t3.platform = 'lx'
 where t2.currency = 'UK';
-- 
-- ************ ************ ************ ************ ************ ************
--  AU
INSERT INTO astdc.lx_sku_ebay_multi_sku_map
(msku, lx_msku_m, lx_local_sku, qty, country,status)
with t_msku as (
select distinct t.msku ,t.tmp_lx_sku  
  from astdc.lx_sku_platform_unmatch t
  left join astdc.lx_sku_ebay_multi_sku_map tt 
    on t.msku = tt.msku 
 where tt.id is null and t.msku not in ('','1')
)
select t1.msku,t1.tmp_lx_sku
      ,ifnull(t3.pfsku ,t2.tt_sku) as lx_local_sku
      ,t2.qty 
      ,t2.currency 
      ,'N'
  from t_msku t1 
  join clx.sz_组合产品表 t2 
    on t1.msku = t2.sku_multi 
  left join astdc.dc_oldprod_ref t3 
    on t2.tt_sku = t3.ttsku 
   and t3.platform = 'lx'
 where t2.currency = 'AU';
 
-- 
-- ************ ************ ************ ************ ************ ************
--  DE
INSERT INTO astdc.lx_sku_ebay_multi_sku_map
(msku, lx_msku_m, lx_local_sku, qty, country,status)
with t_msku as (
select distinct t.msku ,t.tmp_lx_sku  
  from astdc.lx_sku_platform_unmatch t
  left join astdc.lx_sku_ebay_multi_sku_map tt 
    on t.msku = tt.msku 
 where tt.id is null and t.msku not in ('','1')
)
select t1.msku,t1.tmp_lx_sku
      ,ifnull(t3.pfsku ,t2.tt_sku) as lx_local_sku
      ,t2.qty 
      ,t2.currency 
      ,'N'
  from t_msku t1 
  join clx.sz_组合产品表 t2 
    on t1.msku = t2.sku_multi 
  left join astdc.dc_oldprod_ref t3 
    on t2.tt_sku = t3.ttsku 
   and t3.platform = 'lx'
 where t2.currency = 'DE';
"""
        self.dbs.exec_many_sql(sql)
        return ResultObj.success()

    def print_result(self):
        res_text = f"""
1. astdc.lx_sku_ebay_multi_sku_map 用表格中的lx_msku_m字段来注册捆绑产品，然后还需要将ebay实际的捆绑产品【配对】到表格中的lx_msku_m字段对应的lx捆绑产品。


2. 创见完捆绑产品，就可以使用这个表保存的关系进行捆绑产品配对，sql如下：
with t_lxmsku as (select distinct t.msku ,t.lx_msku_m 
  from astdc.lx_sku_ebay_multi_sku_map t 
)
select t1.store_name ,t1.store_id ,t1.platform_code  ,t1.msku ,t.lx_msku_m ,'组合产品配对' as stype
  from t_lxmsku t 
  join astdc.lx_sku_platform_unmatch t1 on t.msku = t1.msku 
 where t1.platform_code ='10003'

3. 非捆绑产品，直接用sku匹配，只要msku能匹配上领星sku就配对
select t.store_name ,t.store_id ,t.platform_code,t.msku
      ,case when l.id is not null then l.sku 
            when l2.id is not null then l2.sku 
        end as lx_local_sku
      ,ifnull(l.id,l2.id) as lxskuid
      ,'通途映射领星' as stype 
  from astdc.lx_sku_platform_unmatch t
  left join astdc.dc_oldprod_ref t3 
    on t.msku = t3.ttsku 
   and t3.platform = 'lx' 
  left join astdc.lx_local_sku l
    on ifnull(t3.pfsku,t.msku) = l.sku 
  left join astdc.lx_local_sku l2
    on t.msku = l2.sku  
 where l.id is not null or l2.id is not null -- 提取能关联上ttsku映射表或者本身就是领星sku的数据
"""
        return res_text

print(ImportLxPlatformMapDataUnmatch('test').run())
