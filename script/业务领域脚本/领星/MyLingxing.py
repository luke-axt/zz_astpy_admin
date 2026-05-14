from CoreBussiness.LingXingService import LingXingService
from 运维管理.MyAdmin import MyAdminBase


class MyLingxing(MyAdminBase):

    def __init__(self, job_name):
        super().__init__(job_name)
        self.job_name = job_name
        self.lx_service = LingXingService()

    def remove_lx_midwh_inv(self):
        """
        将领星的海外中转仓api对接仓库的库存清零。2025-8-28 一次性方法
        :return:
        """
        self.logger.info(f'开始')
        sql = """
        select l.wid,l.product_id ,l.sku,l.seller_id ,l.fnsku ,l.product_valid_num 
          from astdc.lx_inv_local_inventory l
         where l.wid  in (118) and l.product_valid_num != 0
           and l.seller_id != '134578917975174656'
        """
        df = self.dbs.select(sql)
        data_dict = {}
        for index, row in df.iterrows():
            wid = row['wid']
            if wid not in data_dict:
                data_dict[wid] = {'wid':wid,
                                  'remark': '九方API对接中转仓库存清零然后重新初始化',
                                  'product_list':[]
                                  }
            _dict = {
                'adjustment_valid_num': row['product_valid_num'],
                'adjustment_bad_num': 0,
                'adjustment_available_bin': "可用暂存",
                'adjustment_inferior_bin': "次品暂存",
                'adjustment_valid_sgn': '-',
                'adjustment_bad_sgn': '-',
                'sku': row['sku'],
                'fnsku': row['fnsku'],
                'product_id': row['product_id'],
                'seller_id': row['seller_id']
            }
            data_dict[wid]['product_list'].append(_dict)

        for wid,_dict2 in data_dict.items():
            action = '/erp/sc/routing/inventoryReceipt/StorageAdjustment/addAdjustmentOrder'
            res = self.lx_service.call_lx_api_new(action,_dict2)
            print(_dict2)
            self.logger.info(res)
            a = 1


MyLingxing('清理九方中转仓库存').remove_lx_midwh_inv()

