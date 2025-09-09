# 获取复权信息接口文档

## 接口功能
用于获取指定股票的复权信息，包括分红、配股、拆股等复权事件。

## 接口模块
Quote API - 基础数据模块

## 接口参数
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| stock_list | list | 是 | 股票代码列表，格式为["市场.代码"]，例如["HK.00700"] |
| market | string | 否 | 市场代码，例如"HK"、"US"等，默认为空 |

## 接口返回结果
```json
{
    "ret_code": 0,
    "ret_msg": "SUCCESS",
    "data": {
        "rehab_list": [
            {
                "code": "HK.00700",
                "update_time": "2024-03-20 10:00:00",
                "rehab_events": [
                    {
                        "event_time": "2024-03-20",
                        "event_type": "DIVIDEND",
                        "event_desc": "分红",
                        "event_price": 1.0,
                        "event_ratio": 0.1,
                        "event_amount": 1000000000
                    },
                    {
                        "event_time": "2024-03-19",
                        "event_type": "SPLIT",
                        "event_desc": "拆股",
                        "event_price": 0.0,
                        "event_ratio": 2.0,
                        "event_amount": 0
                    }
                ]
            }
        ]
    }
}
```

## 接口异常情况
| 错误码 | 错误信息 | 说明 |
|--------|----------|------|
| 1001 | INVALID_PARAM | 参数错误 |
| 1002 | INVALID_CODE | 股票代码格式错误 |
| 1020 | GET_REHAB_FAILED | 获取复权信息失败 |

## 示例代码
```python
from futu import *

# 创建行情连接
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

# 获取复权信息
ret, data = quote_ctx.get_rehab(['HK.00700'])
if ret == RET_OK:
    print('获取复权信息成功')
    for rehab in data:
        print(f"股票代码: {rehab['code']}")
        print(f"更新时间: {rehab['update_time']}")
        print("复权事件:")
        for event in rehab['rehab_events']:
            print(f"事件时间: {event['event_time']}")
            print(f"事件类型: {event['event_type']}")
            print(f"事件描述: {event['event_desc']}")
            print(f"事件价格: {event['event_price']}")
            print(f"事件比例: {event['event_ratio']}")
            print(f"事件金额: {event['event_amount']}")
            print("-------------------")
else:
    print('获取复权信息失败:', data)

# 关闭连接
quote_ctx.close()
```

## 注意事项
1. 获取复权信息前需要先建立行情连接
2. 可以同时获取多个股票的复权信息
3. 复权信息更新频率较低，建议缓存使用
4. 复权信息主要用于计算复权价格，建议结合历史K线数据一起使用
5. 需要注意处理异常情况，避免程序崩溃 