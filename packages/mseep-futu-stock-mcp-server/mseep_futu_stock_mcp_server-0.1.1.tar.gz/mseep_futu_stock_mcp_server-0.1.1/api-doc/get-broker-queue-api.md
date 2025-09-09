# 获取经纪队列数据接口文档

## 接口功能
用于获取指定股票的实时经纪队列数据，包括经纪商买卖盘信息。

## 接口模块
Quote API - 实时数据获取模块

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
        "broker_list": [
            {
                "code": "HK.00700",
                "update_time": "2024-03-20 10:00:00",
                "bid_broker_id": ["B001", "B002", "B003"],
                "bid_broker_name": ["经纪商1", "经纪商2", "经纪商3"],
                "bid_broker_pos": [1, 2, 3],
                "ask_broker_id": ["S001", "S002", "S003"],
                "ask_broker_name": ["经纪商4", "经纪商5", "经纪商6"],
                "ask_broker_pos": [1, 2, 3],
                "timestamp": "2024-03-20 10:00:00",
                "broker_status": 0
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
| 1013 | GET_BROKER_QUEUE_FAILED | 获取经纪队列数据失败 |

## 示例代码
```python
from futu import *

# 创建行情连接
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

# 获取经纪队列数据
ret, data = quote_ctx.get_broker_queue(['HK.00700'])
if ret == RET_OK:
    print('获取经纪队列数据成功')
    for broker in data:
        print(f"股票代码: {broker['code']}")
        print("买盘经纪商:")
        for i in range(len(broker['bid_broker_id'])):
            print(f"ID: {broker['bid_broker_id'][i]}, 名称: {broker['bid_broker_name'][i]}, 位置: {broker['bid_broker_pos'][i]}")
        print("卖盘经纪商:")
        for i in range(len(broker['ask_broker_id'])):
            print(f"ID: {broker['ask_broker_id'][i]}, 名称: {broker['ask_broker_name'][i]}, 位置: {broker['ask_broker_pos'][i]}")
else:
    print('获取经纪队列数据失败:', data)

# 关闭连接
quote_ctx.close()
```

## 注意事项
1. 获取经纪队列数据前需要先建立行情连接
2. 可以同时获取多个股票的经纪队列数据
3. 经纪队列数据更新频率较高，建议根据实际需求选择获取的股票
4. 经纪队列数据主要用于展示经纪商买卖盘信息，建议根据实际需求选择获取的股票
5. 需要注意处理异常情况，避免程序崩溃 