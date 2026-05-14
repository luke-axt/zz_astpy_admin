from utils.DictUtils import DictUtils

jsonstr="""
[{"ISOCode": "USD", "feeNumber": 1.35, "feeSource": "OUTBOUND", "rebate": 0, "feeCode": "290", "feeName": "最后一公里派送费-旺季", "discount": 0, "paid-up": 1.35}, {"ISOCode": "USD", "feeNumber": 26.42, "feeSource": "OUTBOUND", "rebate": 0, "feeCode": "103", "feeName": "最后一公里派送费", "discount": -8.4544, "paid-up": 17.9656}, {"ISOCode": "USD", "feeNumber": 0.0, "feeSource": "OUTBOUND", "rebate": 0, "feeCode": "3000016", "feeName": "出库处理费-应急附加费", "discount": 0, "paid-up": 0.0}, {"ISOCode": "USD", "feeNumber": 10.25, "feeSource": "OUTBOUND", "rebate": 0, "feeCode": "3000011", "feeName": "出库处理费-续件费", "discount": 0, "paid-up": 10.25}, {"ISOCode": "USD", "feeNumber": 3.48, "feeSource": "OUTBOUND", "rebate": 0, "feeCode": "102", "feeName": "出库处理费", "discount": 0, "paid-up": 3.48}, {"ISOCode": "USD", "feeNumber": 4.3, "feeSource": "OUTBOUND", "rebate": 0, "feeCode": "100", "feeName": "燃油附加费", "discount": 0, "paid-up": 4.3}]
"""
array = DictUtils.parseJsonStrToDict(jsonstr)
print(f"费用名称,原价,折扣,实付")
for dict in array:
    print(f"{dict['feeName']},{dict['feeNumber']},{dict['discount']},{dict['paid-up']}")