# 获取股票列表接口文档

## 接口功能
用于获取指定市场的股票列表信息，包括股票代码、名称、上市状态等。

## 接口模块
Quote API - 基础数据模块

## 接口参数
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| market | string | 是 | 市场代码，例如"HK"、"US"等 |

## 接口返回结果
```json
{
    "ret_code": 0,
    "ret_msg": "SUCCESS",
    "data": {
        "stock_list": [
            {
                "code": "00700",
                "name": "腾讯控股",
                "market": "HK",
                "lot_size": 100,
                "stock_type": "STOCK",
                "stock_owner": 0,
                "list_time": "2004-06-16",
                "delist_time": "",
                "status": 1
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
| 1015 | GET_STOCK_LIST_FAILED | 获取股票列表失败 |

## 示例代码
```python
from futu import *

# 创建行情连接
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

# 获取股票列表
ret, data = quote_ctx.get_stock_list("HK")
if ret == RET_OK:
    print('获取股票列表成功')
    for stock in data:
        print(f"股票代码: {stock['code']}")
        print(f"股票名称: {stock['name']}")
        print(f"市场: {stock['market']}")
        print(f"每手股数: {stock['lot_size']}")
        print(f"股票类型: {stock['stock_type']}")
        print(f"上市时间: {stock['list_time']}")
        print(f"状态: {stock['status']}")
        print("-------------------")
else:
    print('获取股票列表失败:', data)

# 关闭连接
quote_ctx.close()
```

## 注意事项
1. 获取股票列表前需要先建立行情连接
2. 股票列表数据量较大，建议缓存使用
3. 股票状态会实时更新，建议定期获取最新列表
4. 不同市场的股票代码格式不同，需要注意区分
5. 需要注意处理异常情况，避免程序崩溃 