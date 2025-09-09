# 获取板块历史分时数据接口文档

## 接口功能
用于获取指定板块的历史分时数据，包括每个时间点的价格、成交量等信息。

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
| max_count | int | 否 | 最大返回数据条数，默认为1000 |

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
        "ticks": [
            {
                "time": "09:30:00",
                "price": 100.0,
                "volume": 10000,
                "turnover": 1000000,
                "pe_ratio": 20.5,
                "turnover_rate": 0.1
            },
            {
                "time": "09:31:00",
                "price": 100.5,
                "volume": 15000,
                "turnover": 1507500,
                "pe_ratio": 20.6,
                "turnover_rate": 0.15
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
| 1007 | INVALID_COUNT | 数据条数错误 |
| 1038 | GET_PLATE_HISTORY_TICK_FAILED | 获取板块历史分时数据失败 |

## 示例代码
```python
from futu import *

# 创建行情连接
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

# 获取板块历史分时数据
ret, data = quote_ctx.get_plate_history_tick(
    plate_code="HK.INDUSTRY.IT",
    market="HK",
    date="2024-03-20",
    start_time="09:30:00",
    end_time="16:00:00",
    max_count=1000
)
if ret == RET_OK:
    print('获取板块历史分时数据成功')
    print(f"板块代码: {data['plate_code']}")
    print(f"板块名称: {data['plate_name']}")
    print(f"市场: {data['market']}")
    print(f"日期: {data['date']}")
    print("分时数据:")
    for tick in data['ticks']:
        print(f"时间: {tick['time']}")
        print(f"价格: {tick['price']}")
        print(f"成交量: {tick['volume']}")
        print(f"成交额: {tick['turnover']}")
        print(f"市盈率: {tick['pe_ratio']}")
        print(f"换手率: {tick['turnover_rate']}")
        print("-------------------")
else:
    print('获取板块历史分时数据失败:', data)

# 关闭连接
quote_ctx.close()
```

## 注意事项
1. 获取板块历史分时数据前需要先建立行情连接
2. 板块代码需要按照指定格式填写
3. 日期必须在有效范围内
4. 时间范围必须在交易时间内
5. 需要注意处理异常情况，避免程序崩溃
6. 历史分时数据主要用于技术分析和历史数据研究
7. 数据量较大时，建议适当设置max_count参数 