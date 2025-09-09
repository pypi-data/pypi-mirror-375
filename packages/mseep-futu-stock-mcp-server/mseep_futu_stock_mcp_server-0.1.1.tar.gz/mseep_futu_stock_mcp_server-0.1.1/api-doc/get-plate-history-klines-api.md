# 获取板块历史K线接口文档

## 接口功能
用于获取指定板块的历史K线数据，包括开盘价、收盘价、最高价、最低价、成交量等信息。

## 接口模块
Quote API - 板块数据模块

## 接口参数
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| plate_code | string | 是 | 板块代码，例如"HK.BK1001" |
| market | string | 否 | 市场代码，例如"HK"、"US"等，如果不填则从plate_code中解析 |
| start_date | string | 是 | 开始日期，格式为"YYYY-MM-DD" |
| end_date | string | 是 | 结束日期，格式为"YYYY-MM-DD" |
| kline_type | string | 否 | K线类型，可选值："K_DAY"（日K）、"K_WEEK"（周K）、"K_MON"（月K）、"K_QUARTER"（季K）、"K_YEAR"（年K），默认为"K_DAY" |
| max_count | int | 否 | 最大返回数量，默认为1000 |

## 接口返回结果
```json
{
    "ret_code": 0,
    "ret_msg": "SUCCESS",
    "data": {
        "plate_code": "HK.BK1001",
        "plate_name": "恒生指数",
        "kline_list": [
            {
                "time": "2024-03-20",
                "open": 16500.0,
                "close": 16700.0,
                "high": 16800.0,
                "low": 16400.0,
                "volume": 1000000000,
                "turnover": 20000000000,
                "change": 200.0,
                "change_ratio": 0.0121,
                "last_close": 16500.0
            },
            {
                "time": "2024-03-19",
                "open": 16400.0,
                "close": 16500.0,
                "high": 16600.0,
                "low": 16300.0,
                "volume": 900000000,
                "turnover": 18000000000,
                "change": 100.0,
                "change_ratio": 0.0061,
                "last_close": 16400.0
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
| 1003 | INVALID_PLATECODE | 板块代码错误 |
| 1004 | INVALID_DATE | 日期格式错误 |
| 1005 | INVALID_KLINETYPE | K线类型错误 |
| 1006 | INVALID_COUNT | 数量错误 |
| 1057 | GET_PLATE_HISTORY_KLINES_FAILED | 获取板块历史K线失败 |

## 示例代码
```python
from futu import *

# 创建行情连接
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

# 获取板块历史K线
ret, data = quote_ctx.get_plate_history_klines(
    plate_code="HK.BK1001",
    market="HK",
    start_date="2024-03-01",
    end_date="2024-03-20",
    kline_type="K_DAY",
    max_count=100
)
if ret == RET_OK:
    print('获取板块历史K线成功')
    print(f"板块代码: {data['plate_code']}")
    print(f"板块名称: {data['plate_name']}")
    print("K线列表:")
    for kline in data['kline_list']:
        print(f"时间: {kline['time']}")
        print(f"开盘价: {kline['open']}")
        print(f"收盘价: {kline['close']}")
        print(f"最高价: {kline['high']}")
        print(f"最低价: {kline['low']}")
        print(f"成交量: {kline['volume']}")
        print(f"成交额: {kline['turnover']}")
        print(f"涨跌: {kline['change']}")
        print(f"涨跌幅: {kline['change_ratio']}")
        print(f"昨收: {kline['last_close']}")
        print("-------------------")
else:
    print('获取板块历史K线失败:', data)

# 关闭连接
quote_ctx.close()
```

## 注意事项
1. 获取板块历史K线前需要先建立行情连接
2. 板块代码需要按照指定格式填写
3. 市场代码必须是有效的市场代码
4. 日期格式必须是有效的日期格式
5. K线类型必须是有效的类型
6. 需要注意处理异常情况，避免程序崩溃
7. 返回的数据包含板块信息和K线列表，如：
   - 板块代码和名称
   - K线列表（包含时间、价格、成交量等信息）
8. 这些信息对于分析板块走势和交易决策非常重要 