# 获取市场快照接口文档

## 接口功能
用于获取指定股票的市场快照数据，包括最新价、涨跌幅、成交量等行情信息。

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
        "snapshot_list": [
            {
                "code": "HK.00700",
                "update_time": "2024-03-20 10:00:00",
                "last_price": 350.0,
                "open_price": 348.0,
                "high_price": 352.0,
                "low_price": 347.0,
                "prev_close_price": 345.0,
                "volume": 1000000,
                "turnover": 350000000.0,
                "turnover_rate": 0.1,
                "amplitude": 0.014,
                "dark_status": 0,
                "list_time": "2004-06-16",
                "price_spread": 0.1,
                "stock_owner": "TENCENT",
                "lot_size": 100,
                "sec_status": 0,
                "bid_price": [349.9, 349.8, 349.7],
                "bid_volume": [1000, 2000, 3000],
                "ask_price": [350.1, 350.2, 350.3],
                "ask_volume": [1000, 2000, 3000]
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
| 1007 | GET_MARKET_SNAPSHOT_FAILED | 获取市场快照失败 |

## 示例代码
```python
from futu import *

# 创建行情连接
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

# 获取市场快照
ret, data = quote_ctx.get_market_snapshot(['HK.00700'])
if ret == RET_OK:
    print('获取市场快照成功')
    for snapshot in data:
        print(f"股票代码: {snapshot['code']}")
        print(f"最新价: {snapshot['last_price']}")
        print(f"涨跌幅: {(snapshot['last_price'] - snapshot['prev_close_price']) / snapshot['prev_close_price'] * 100:.2f}%")
        print(f"成交量: {snapshot['volume']}")
        print(f"成交额: {snapshot['turnover']}")
else:
    print('获取市场快照失败:', data)

# 关闭连接
quote_ctx.close()
```

## 注意事项
1. 获取市场快照前需要先建立行情连接
2. 可以同时获取多个股票的市场快照数据
3. 市场快照数据包含最新的行情信息，但不包含历史数据
4. 建议根据实际需求选择获取的股票
5. 需要注意处理异常情况，避免程序崩溃 