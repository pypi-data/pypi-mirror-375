# 获取逐笔成交数据接口文档

## 接口功能
用于获取指定股票的实时逐笔成交数据，包括每笔成交的价格、数量、时间等信息。

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
        "ticker_list": [
            {
                "code": "HK.00700",
                "sequence": 1000,
                "price": 350.0,
                "volume": 1000,
                "turnover": 350000.0,
                "ticker_direction": 1,
                "ticker_type": 1,
                "timestamp": "2024-03-20 10:00:00",
                "ticker_status": 0
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
| 1012 | GET_RT_TICKER_FAILED | 获取逐笔成交数据失败 |

## 示例代码
```python
from futu import *

# 创建行情连接
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

# 获取逐笔成交数据
ret, data = quote_ctx.get_rt_ticker(['HK.00700'])
if ret == RET_OK:
    print('获取逐笔成交数据成功')
    for ticker in data:
        print(f"股票代码: {ticker['code']}")
        print(f"成交序号: {ticker['sequence']}")
        print(f"成交价格: {ticker['price']}")
        print(f"成交数量: {ticker['volume']}")
        print(f"成交金额: {ticker['turnover']}")
        print(f"成交方向: {ticker['ticker_direction']}")
        print(f"成交类型: {ticker['ticker_type']}")
        print(f"成交时间: {ticker['timestamp']}")
else:
    print('获取逐笔成交数据失败:', data)

# 关闭连接
quote_ctx.close()
```

## 注意事项
1. 获取逐笔成交数据前需要先建立行情连接
2. 可以同时获取多个股票的逐笔成交数据
3. 逐笔成交数据更新频率较高，建议根据实际需求选择获取的股票
4. 逐笔成交数据量大，建议在回调中及时处理数据
5. 需要注意处理异常情况，避免程序崩溃 