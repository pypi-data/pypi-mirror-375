# 获取板块历史分时数据接口文档

## 接口功能
用于获取指定板块的历史分时数据，包括每分钟的价格、成交量、成交额等信息。

## 接口模块
Quote API - 历史数据模块

## 接口参数
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| plate_code | string | 是 | 板块代码，格式为"market.type.code"，例如"HK.INDUSTRY.IT" |
| market | string | 否 | 市场代码，例如"HK"、"US"等 |
| date | string | 是 | 日期，格式为"YYYY-MM-DD" |
| start_time | string | 否 | 开始时间，格式为"HH:MM:SS"，默认为"09:30:00" |
| end_time | string | 否 | 结束时间，格式为"HH:MM:SS"，默认为"16:00:00" |

## 接口返回结果
```json
{
    "ret_code": 0,
    "ret_msg": "SUCCESS",
    "data": {
        "plate_code": "HK.INDUSTRY.IT",
        "plate_name": "信息技术",
        "market": "HK",
        "date": "2024-03-20",
        "intraday": [
            {
                "time": "09:30:00",
                "price": 100.0,
                "volume": 10000,
                "turnover": 1000000,
                "change": 0.0,
                "change_rate": 0.0
            },
            {
                "time": "09:31:00",
                "price": 101.0,
                "volume": 20000,
                "turnover": 2020000,
                "change": 1.0,
                "change_rate": 1.0
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
| 1005 | INVALID_DATE | 日期格式错误 |
| 1006 | INVALID_TIME | 时间格式错误 |
| 1035 | GET_PLATE_HISTORY_INTRADAY_FAILED | 获取板块历史分时数据失败 |

## 示例代码
```python
from futu import *

# 创建行情连接
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

# 获取板块历史分时数据
ret, data = quote_ctx.get_plate_history_intraday(
    plate_code="HK.INDUSTRY.IT",
    market="HK",
    date="2024-03-20",
    start_time="09:30:00",
    end_time="16:00:00"
)
if ret == RET_OK:
    print('获取板块历史分时数据成功')
    print(f"板块代码: {data['plate_code']}")
    print(f"板块名称: {data['plate_name']}")
    print(f"市场: {data['market']}")
    print(f"日期: {data['date']}")
    print("分时数据:")
    for intraday in data['intraday']:
        print(f"时间: {intraday['time']}")
        print(f"价格: {intraday['price']}")
        print(f"成交量: {intraday['volume']}")
        print(f"成交额: {intraday['turnover']}")
        print(f"涨跌: {intraday['change']}")
        print(f"涨跌幅: {intraday['change_rate']}%")
        print("-------------------")
else:
    print('获取板块历史分时数据失败:', data)

# 关闭连接
quote_ctx.close()
```

## 注意事项
1. 获取板块历史分时数据前需要先建立行情连接
2. 板块代码需要按照指定格式填写
3. 日期必须在交易日内
4. 时间范围必须在交易时间内
5. 分时数据主要用于日内交易分析和历史数据研究
6. 需要注意处理异常情况，避免程序崩溃 