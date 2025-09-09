# 获取板块K线数据接口文档

## 接口功能
用于获取指定板块的K线数据，包括日K、周K、月K等不同周期的K线数据。

## 接口模块
Quote API - K线数据模块

## 接口参数
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| plate_code | string | 是 | 板块代码，格式为"market.type.code"，例如"HK.INDUSTRY.IT" |
| market | string | 否 | 市场代码，例如"HK"、"US"等 |
| ktype | string | 是 | K线类型，可选值：<br>K_DAY - 日K<br>K_WEEK - 周K<br>K_MON - 月K<br>K_QUARTER - 季K<br>K_YEAR - 年K |
| start_date | string | 否 | 开始日期，格式为"YYYY-MM-DD"，默认为当前日期 |
| end_date | string | 否 | 结束日期，格式为"YYYY-MM-DD"，默认为当前日期 |

## 接口返回结果
```json
{
    "ret_code": 0,
    "ret_msg": "SUCCESS",
    "data": {
        "plate_code": "HK.INDUSTRY.IT",
        "plate_name": "信息技术",
        "market": "HK",
        "kline": [
            {
                "time_key": "2024-03-20",
                "open": 100.0,
                "high": 110.0,
                "low": 95.0,
                "close": 105.0,
                "volume": 1000000,
                "turnover": 100000000
            },
            {
                "time_key": "2024-03-19",
                "open": 98.0,
                "high": 102.0,
                "low": 96.0,
                "close": 100.0,
                "volume": 900000,
                "turnover": 90000000
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
| 1004 | INVALID_KTYPE | K线类型错误 |
| 1005 | INVALID_DATE | 日期格式错误 |
| 1034 | GET_PLATE_KLINE_FAILED | 获取板块K线数据失败 |

## 示例代码
```python
from futu import *

# 创建行情连接
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

# 获取板块K线数据
ret, data = quote_ctx.get_plate_kline(
    plate_code="HK.INDUSTRY.IT",
    market="HK",
    ktype=KLType.K_DAY,
    start_date="2024-03-01",
    end_date="2024-03-20"
)
if ret == RET_OK:
    print('获取板块K线数据成功')
    print(f"板块代码: {data['plate_code']}")
    print(f"板块名称: {data['plate_name']}")
    print(f"市场: {data['market']}")
    print("K线数据:")
    for kline in data['kline']:
        print(f"日期: {kline['time_key']}")
        print(f"开盘价: {kline['open']}")
        print(f"最高价: {kline['high']}")
        print(f"最低价: {kline['low']}")
        print(f"收盘价: {kline['close']}")
        print(f"成交量: {kline['volume']}")
        print(f"成交额: {kline['turnover']}")
        print("-------------------")
else:
    print('获取板块K线数据失败:', data)

# 关闭连接
quote_ctx.close()
```

## 注意事项
1. 获取板块K线数据前需要先建立行情连接
2. 板块代码需要按照指定格式填写
3. K线类型需要选择正确的类型
4. 日期范围不能超过系统限制
5. K线数据主要用于技术分析和历史数据研究
6. 需要注意处理异常情况，避免程序崩溃 