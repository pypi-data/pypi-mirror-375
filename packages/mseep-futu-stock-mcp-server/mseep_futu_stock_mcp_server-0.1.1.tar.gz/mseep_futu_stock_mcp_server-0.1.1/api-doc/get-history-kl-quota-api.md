# 获取历史K线配额接口文档

## 接口功能
用于获取历史K线数据的配额信息，包括已使用配额和剩余配额。

## 接口模块
Quote API - 自定义模块

## 接口参数
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| market | string | 否 | 市场代码，例如"HK"、"US"等，不传则返回所有市场的配额 |

## 接口返回结果
```json
{
    "ret_code": 0,
    "ret_msg": "SUCCESS",
    "data": {
        "quota_list": [
            {
                "market": "HK",
                "market_name": "香港",
                "total_quota": 1000000,
                "used_quota": 500000,
                "remaining_quota": 500000,
                "quota_unit": "条",
                "reset_time": "2024-04-01 00:00:00",
                "quota_type": "DAILY"
            },
            {
                "market": "US",
                "market_name": "美国",
                "total_quota": 2000000,
                "used_quota": 1000000,
                "remaining_quota": 1000000,
                "quota_unit": "条",
                "reset_time": "2024-04-01 00:00:00",
                "quota_type": "DAILY"
            },
            {
                "market": "CN",
                "market_name": "中国",
                "total_quota": 500000,
                "used_quota": 200000,
                "remaining_quota": 300000,
                "quota_unit": "条",
                "reset_time": "2024-04-01 00:00:00",
                "quota_type": "DAILY"
            }
        ]
    }
}
```

## 接口异常情况
| 错误码 | 错误信息 | 说明 |
|--------|----------|------|
| 1001 | INVALID_PARAM | 参数错误 |
| 1002 | INVALID_MARKET | 市场代码错误 |
| 1046 | GET_HISTORY_KL_QUOTA_FAILED | 获取历史K线配额失败 |

## 示例代码
```python
from futu import *

# 创建行情连接
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

# 获取历史K线配额
ret, data = quote_ctx.get_history_kl_quota(
    market="HK"  # 可选参数，不传则返回所有市场的配额
)
if ret == RET_OK:
    print('获取历史K线配额成功')
    print("配额列表:")
    for quota in data['quota_list']:
        print(f"市场: {quota['market']} ({quota['market_name']})")
        print(f"总配额: {quota['total_quota']} {quota['quota_unit']}")
        print(f"已使用配额: {quota['used_quota']} {quota['quota_unit']}")
        print(f"剩余配额: {quota['remaining_quota']} {quota['quota_unit']}")
        print(f"重置时间: {quota['reset_time']}")
        print(f"配额类型: {quota['quota_type']}")
        print("-------------------")
else:
    print('获取历史K线配额失败:', data)

# 关闭连接
quote_ctx.close()
```

## 注意事项
1. 获取历史K线配额前需要先建立行情连接
2. 市场代码必须是有效的市场代码
3. 需要注意处理异常情况，避免程序崩溃
4. 配额信息包括：
   - 市场代码和名称
   - 总配额
   - 已使用配额
   - 剩余配额
   - 配额单位
   - 重置时间
   - 配额类型
5. 配额类型说明：
   - DAILY：每日配额
   - MONTHLY：每月配额
   - YEARLY：每年配额
6. 这些信息对于了解API使用限制和进行配额管理非常重要 