# 获取板块历史分时数据接口文档

## 接口功能
用于获取指定板块的历史分时数据，包括开盘价、最高价、最低价、收盘价、成交量等信息。

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
        "time_share": [
            {
                "time": "09:30:00",
                "open": 100.0,  // 开盘价
                "high": 101.0,  // 最高价
                "low": 99.0,    // 最低价
                "close": 100.5, // 收盘价
                "volume": 1000000,  // 成交量
                "turnover": 100500000,  // 成交额
                "change": 0.5,  // 涨跌幅
                "change_ratio": 0.005  // 涨跌比率
            },
            {
                "time": "09:31:00",
                "open": 100.5,
                "high": 102.0,
                "low": 100.0,
                "close": 101.5,
                "volume": 2000000,
                "turnover": 203000000,
                "change": 1.0,
                "change_ratio": 0.01
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
| 1041 | GET_PLATE_HISTORY_TIME_SHARE_FAILED | 获取板块历史分时数据失败 |

## 示例代码
```python
from futu import *

# 创建行情连接
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

# 获取板块历史分时数据
ret, data = quote_ctx.get_plate_history_time_share(
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
    for share in data['time_share']:
        print(f"时间: {share['time']}")
        print(f"开盘价: {share['open']}")
        print(f"最高价: {share['high']}")
        print(f"最低价: {share['low']}")
        print(f"收盘价: {share['close']}")
        print(f"成交量: {share['volume']}")
        print(f"成交额: {share['turnover']}")
        print(f"涨跌幅: {share['change']}")
        print(f"涨跌比率: {share['change_ratio']}")
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
6. 历史分时数据主要用于技术分析和趋势研究
7. 数据量较大时，建议适当设置max_count参数
8. 分时数据说明：
   - 开盘价：该时间段开始时的价格
   - 最高价：该时间段内的最高价格
   - 最低价：该时间段内的最低价格
   - 收盘价：该时间段结束时的价格
   - 成交量：该时间段内的成交数量
   - 成交额：该时间段内的成交金额
   - 涨跌幅：该时间段内的价格变化
   - 涨跌比率：该时间段内的价格变化比率 