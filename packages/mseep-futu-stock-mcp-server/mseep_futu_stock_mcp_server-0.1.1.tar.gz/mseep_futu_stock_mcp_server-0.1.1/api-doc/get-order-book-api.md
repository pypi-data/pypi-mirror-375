# 获取买卖盘接口文档

## 接口功能
用于获取指定股票的实时买卖盘数据，包括买卖盘档位、价格、数量等信息。

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
        "order_book_list": [
            {
                "code": "HK.00700",
                "update_time": "2024-03-20 10:00:00",
                "bid_price": [349.9, 349.8, 349.7, 349.6, 349.5],
                "bid_volume": [1000, 2000, 3000, 4000, 5000],
                "ask_price": [350.1, 350.2, 350.3, 350.4, 350.5],
                "ask_volume": [1000, 2000, 3000, 4000, 5000]
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
| 1009 | GET_ORDER_BOOK_FAILED | 获取买卖盘失败 |

## 示例代码
```python
from futu import *

# 创建行情连接
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

# 获取买卖盘数据
ret, data = quote_ctx.get_order_book(['HK.00700'])
if ret == RET_OK:
    print('获取买卖盘数据成功')
    for order_book in data:
        print(f"股票代码: {order_book['code']}")
        print("买盘:")
        for i in range(len(order_book['bid_price'])):
            print(f"价格: {order_book['bid_price'][i]}, 数量: {order_book['bid_volume'][i]}")
        print("卖盘:")
        for i in range(len(order_book['ask_price'])):
            print(f"价格: {order_book['ask_price'][i]}, 数量: {order_book['ask_volume'][i]}")
else:
    print('获取买卖盘数据失败:', data)

# 关闭连接
quote_ctx.close()
```

## 注意事项
1. 获取买卖盘数据前需要先建立行情连接
2. 可以同时获取多个股票的买卖盘数据
3. 买卖盘数据包含最新的买卖盘信息，但不包含历史数据
4. 建议根据实际需求选择获取的股票
5. 需要注意处理异常情况，避免程序崩溃 