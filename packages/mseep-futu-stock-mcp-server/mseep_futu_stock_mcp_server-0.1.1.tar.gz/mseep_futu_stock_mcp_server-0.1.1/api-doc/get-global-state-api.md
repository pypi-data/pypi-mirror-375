# 获取全局状态接口文档

## 接口功能
用于获取全局市场状态信息，包括各个市场的交易状态、休市时间等。

## 接口模块
Quote API - 市场筛选模块

## 接口参数
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| market | string | 否 | 市场代码，例如"HK"、"US"等，如果不填则返回所有市场状态 |

## 接口返回结果
```json
{
    "ret_code": 0,
    "ret_msg": "SUCCESS",
    "data": {
        "market_list": [
            {
                "market": "HK",
                "market_name": "香港",
                "market_state": "OPEN",
                "market_time": "09:30-12:00,13:00-16:00",
                "lunch_break": "12:00-13:00",
                "time_zone": "Asia/Hong_Kong",
                "update_time": "2024-03-20 10:30:00"
            },
            {
                "market": "US",
                "market_name": "美国",
                "market_state": "CLOSED",
                "market_time": "09:30-16:00",
                "lunch_break": "",
                "time_zone": "America/New_York",
                "update_time": "2024-03-20 10:30:00"
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
| 1053 | GET_GLOBAL_STATE_FAILED | 获取全局状态失败 |

## 示例代码
```python
from futu import *

# 创建行情连接
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

# 获取所有市场状态
ret, data = quote_ctx.get_global_state()
if ret == RET_OK:
    print('获取全局状态成功')
    for market in data['market_list']:
        print(f"市场: {market['market']}")
        print(f"市场名称: {market['market_name']}")
        print(f"市场状态: {market['market_state']}")
        print(f"交易时间: {market['market_time']}")
        print(f"午休时间: {market['lunch_break']}")
        print(f"时区: {market['time_zone']}")
        print(f"更新时间: {market['update_time']}")
        print("-------------------")
else:
    print('获取全局状态失败:', data)

# 获取指定市场状态
ret, data = quote_ctx.get_global_state(market="HK")
if ret == RET_OK:
    print('获取香港市场状态成功')
    market = data['market_list'][0]
    print(f"市场状态: {market['market_state']}")
    print(f"交易时间: {market['market_time']}")
    print(f"午休时间: {market['lunch_break']}")
else:
    print('获取香港市场状态失败:', data)

# 关闭连接
quote_ctx.close()
```

## 注意事项
1. 获取全局状态前需要先建立行情连接
2. 市场代码必须是有效的市场代码
3. 需要注意处理异常情况，避免程序崩溃
4. 返回的数据包含各个市场的状态信息，如：
   - 市场代码和名称
   - 市场状态（开市/休市）
   - 交易时间
   - 午休时间
   - 时区信息
   - 更新时间
5. 这些信息对于了解各个市场的交易状态非常重要 