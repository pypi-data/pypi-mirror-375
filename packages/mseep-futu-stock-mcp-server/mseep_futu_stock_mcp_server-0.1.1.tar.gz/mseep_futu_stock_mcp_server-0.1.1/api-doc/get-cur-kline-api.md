# 获取K线数据接口文档

## 接口功能
用于获取指定股票的实时K线数据，包括不同周期的K线信息。

## 接口模块
Quote API - 实时数据获取模块

## 接口参数
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| stock_list | list | 是 | 股票代码列表，格式为["市场.代码"]，例如["HK.00700"] |
| kline_type | string | 是 | K线类型，可选值：<br>K_1M: 1分钟<br>K_5M: 5分钟<br>K_15M: 15分钟<br>K_30M: 30分钟<br>K_60M: 60分钟<br>K_DAY: 日K线<br>K_WEEK: 周K线<br>K_MON: 月K线<br>K_QUARTER: 季K线<br>K_YEAR: 年K线 |
| market | string | 否 | 市场代码，例如"HK"、"US"等，默认为空 |

## 接口返回结果
```json
{
    "ret_code": 0,
    "ret_msg": "SUCCESS",
    "data": {
        "kline_list": [
            {
                "code": "HK.00700",
                "kline_type": "K_1M",
                "update_time": "2024-03-20 10:00:00",
                "open_price": 350.0,
                "high_price": 351.0,
                "low_price": 349.0,
                "close_price": 350.5,
                "volume": 1000000,
                "turnover": 350500000.0,
                "pe_ratio": 25.0,
                "turnover_rate": 0.1,
                "timestamp": "2024-03-20 10:00:00",
                "kline_status": 0
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
| 1003 | INVALID_SUBTYPE | K线类型错误 |
| 1010 | GET_CUR_KLINE_FAILED | 获取K线数据失败 |

## 示例代码
```python
from futu import *

# 创建行情连接
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

# 获取K线数据
ret, data = quote_ctx.get_cur_kline(['HK.00700'], SubType.K_1M)
if ret == RET_OK:
    print('获取K线数据成功')
    for kline in data:
        print(f"股票代码: {kline['code']}")
        print(f"K线类型: {kline['kline_type']}")
        print(f"开盘价: {kline['open_price']}")
        print(f"最高价: {kline['high_price']}")
        print(f"最低价: {kline['low_price']}")
        print(f"收盘价: {kline['close_price']}")
        print(f"成交量: {kline['volume']}")
        print(f"成交额: {kline['turnover']}")
else:
    print('获取K线数据失败:', data)

# 关闭连接
quote_ctx.close()
```

## 注意事项
1. 获取K线数据前需要先建立行情连接
2. 可以同时获取多个股票的K线数据
3. K线数据包含最新的K线信息，但不包含历史数据
4. 不同周期的K线数据更新频率不同，需要注意数据更新的时间间隔
5. 建议根据实际需求选择获取的股票和K线类型
6. 需要注意处理异常情况，避免程序崩溃 