# 获取历史K线接口文档

## 接口功能
用于获取指定股票的历史K线数据，包括日K、周K、月K等不同周期的K线数据。

## 接口模块
Quote API - 基础数据模块

## 接口参数
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| stock_list | list | 是 | 股票代码列表，格式为["市场.代码"]，例如["HK.00700"] |
| market | string | 否 | 市场代码，例如"HK"、"US"等，默认为空 |
| start_date | string | 是 | 开始日期，格式为"YYYY-MM-DD" |
| end_date | string | 是 | 结束日期，格式为"YYYY-MM-DD" |
| kline_type | string | 是 | K线类型，可选值：K_DAY(日K)、K_WEEK(周K)、K_MON(月K)、K_QUARTER(季K)、K_YEAR(年K) |
| autype | string | 否 | 复权类型，可选值：NONE(不复权)、FORWARD(前复权)、BACKWARD(后复权)，默认为NONE |

## 接口返回结果
```json
{
    "ret_code": 0,
    "ret_msg": "SUCCESS",
    "data": {
        "history_kline_list": [
            {
                "code": "HK.00700",
                "kline_list": [
                    {
                        "time_key": "2024-03-20",
                        "open": 300.0,
                        "high": 310.0,
                        "low": 290.0,
                        "close": 305.0,
                        "volume": 1000000,
                        "amount": 305000000,
                        "turnover_rate": 0.1,
                        "pe_ratio": 20.0,
                        "pb_ratio": 5.0,
                        "ps_ratio": 10.0,
                        "market_cap": 1000000000000
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
| 1003 | INVALID_DATE | 日期格式错误 |
| 1004 | INVALID_KLINETYPE | K线类型错误 |
| 1005 | INVALID_AUTYPE | 复权类型错误 |
| 1019 | REQUEST_HISTORY_KLINE_FAILED | 获取历史K线数据失败 |

## 示例代码
```python
from futu import *

# 创建行情连接
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

# 获取历史K线数据
ret, data = quote_ctx.request_history_kline(
    ['HK.00700'],
    start_date='2024-03-01',
    end_date='2024-03-20',
    kline_type=KLType.K_DAY,
    autype=AuType.NONE
)
if ret == RET_OK:
    print('获取历史K线数据成功')
    for kline in data:
        print(f"股票代码: {kline['code']}")
        print("K线数据:")
        for k in kline['kline_list']:
            print(f"时间: {k['time_key']}")
            print(f"开盘价: {k['open']}")
            print(f"最高价: {k['high']}")
            print(f"最低价: {k['low']}")
            print(f"收盘价: {k['close']}")
            print(f"成交量: {k['volume']}")
            print(f"成交额: {k['amount']}")
            print(f"换手率: {k['turnover_rate']}")
            print(f"市盈率: {k['pe_ratio']}")
            print(f"市净率: {k['pb_ratio']}")
            print(f"市销率: {k['ps_ratio']}")
            print(f"市值: {k['market_cap']}")
            print("-------------------")
else:
    print('获取历史K线数据失败:', data)

# 关闭连接
quote_ctx.close()
```

## 注意事项
1. 获取历史K线数据前需要先建立行情连接
2. 可以同时获取多个股票的历史K线数据
3. 历史K线数据量较大，建议根据实际需求选择获取的时间范围
4. 不同周期的K线数据适用于不同的分析场景，建议根据实际需求选择
5. 需要注意处理异常情况，避免程序崩溃 