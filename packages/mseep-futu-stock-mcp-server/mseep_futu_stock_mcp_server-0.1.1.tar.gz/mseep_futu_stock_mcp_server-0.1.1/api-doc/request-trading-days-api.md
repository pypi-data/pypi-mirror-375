# 获取交易日历接口文档

## 接口功能
用于获取指定市场的交易日历，包括交易日和非交易日。

## 接口模块
Quote API - 市场筛选模块

## 接口参数
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| market | string | 是 | 市场代码，例如"HK"、"US"等 |
| start_date | string | 是 | 开始日期，格式为"YYYY-MM-DD" |
| end_date | string | 是 | 结束日期，格式为"YYYY-MM-DD" |
| is_open | bool | 否 | 是否只返回交易日，默认为true |

## 接口返回结果
```json
{
    "ret_code": 0,
    "ret_msg": "SUCCESS",
    "data": {
        "market": "HK",
        "trading_days": [
            {
                "date": "2024-03-20",
                "is_trading_day": true,
                "is_weekend": false,
                "is_holiday": false,
                "holiday_name": null,
                "is_half_day": false
            },
            {
                "date": "2024-03-21",
                "is_trading_day": true,
                "is_weekend": false,
                "is_holiday": false,
                "holiday_name": null,
                "is_half_day": false
            },
            {
                "date": "2024-03-22",
                "is_trading_day": false,
                "is_weekend": true,
                "is_holiday": false,
                "holiday_name": null,
                "is_half_day": false
            },
            {
                "date": "2024-03-23",
                "is_trading_day": false,
                "is_weekend": true,
                "is_holiday": false,
                "holiday_name": null,
                "is_half_day": false
            },
            {
                "date": "2024-03-24",
                "is_trading_day": false,
                "is_weekend": false,
                "is_holiday": true,
                "holiday_name": "复活节",
                "is_half_day": false
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
| 1005 | INVALID_DATE | 日期格式错误 |
| 1045 | REQUEST_TRADING_DAYS_FAILED | 获取交易日历失败 |

## 示例代码
```python
from futu import *

# 创建行情连接
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

# 获取交易日历
ret, data = quote_ctx.request_trading_days(
    market="HK",
    start_date="2024-03-20",
    end_date="2024-03-24",
    is_open=True  # 可选参数，默认为true
)
if ret == RET_OK:
    print('获取交易日历成功')
    print(f"市场: {data['market']}")
    print("交易日历:")
    for day in data['trading_days']:
        print(f"日期: {day['date']}")
        print(f"是否为交易日: {day['is_trading_day']}")
        print(f"是否为周末: {day['is_weekend']}")
        print(f"是否为假日: {day['is_holiday']}")
        if day['holiday_name']:
            print(f"假日名称: {day['holiday_name']}")
        print(f"是否为半日市: {day['is_half_day']}")
        print("-------------------")
else:
    print('获取交易日历失败:', data)

# 关闭连接
quote_ctx.close()
```

## 注意事项
1. 获取交易日历前需要先建立行情连接
2. 市场代码必须是有效的市场代码
3. 日期范围必须在有效范围内
4. 需要注意处理异常情况，避免程序崩溃
5. 交易日历信息包括：
   - 日期
   - 是否为交易日
   - 是否为周末
   - 是否为假日
   - 假日名称（如果有）
   - 是否为半日市
6. 这些信息对于了解市场的交易安排和进行交易计划非常重要 