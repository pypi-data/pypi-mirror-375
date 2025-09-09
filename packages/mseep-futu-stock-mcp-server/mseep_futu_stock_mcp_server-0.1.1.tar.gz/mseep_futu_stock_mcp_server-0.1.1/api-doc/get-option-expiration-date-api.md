# 获取期权到期日接口文档

## 接口功能
用于获取指定股票的期权到期日信息，包括到期日期、剩余天数等。

## 接口模块
Quote API - 相关衍生品模块

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
        "option_expiration_list": [
            {
                "code": "HK.00700",
                "update_time": "2024-03-20 10:00:00",
                "expiration_dates": [
                    {
                        "expiration_date": "2024-03-27",
                        "remaining_days": 7,
                        "is_week_option": true,
                        "is_month_option": false,
                        "is_quarter_option": false
                    },
                    {
                        "expiration_date": "2024-04-24",
                        "remaining_days": 35,
                        "is_week_option": false,
                        "is_month_option": true,
                        "is_quarter_option": false
                    },
                    {
                        "expiration_date": "2024-06-26",
                        "remaining_days": 98,
                        "is_week_option": false,
                        "is_month_option": false,
                        "is_quarter_option": true
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
| 1021 | GET_OPTION_EXPIRATION_DATE_FAILED | 获取期权到期日失败 |

## 示例代码
```python
from futu import *

# 创建行情连接
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

# 获取期权到期日
ret, data = quote_ctx.get_option_expiration_date(['HK.00700'])
if ret == RET_OK:
    print('获取期权到期日成功')
    for option in data:
        print(f"股票代码: {option['code']}")
        print(f"更新时间: {option['update_time']}")
        print("到期日信息:")
        for date in option['expiration_dates']:
            print(f"到期日期: {date['expiration_date']}")
            print(f"剩余天数: {date['remaining_days']}")
            print(f"是否周期权: {date['is_week_option']}")
            print(f"是否月期权: {date['is_month_option']}")
            print(f"是否季期权: {date['is_quarter_option']}")
            print("-------------------")
else:
    print('获取期权到期日失败:', data)

# 关闭连接
quote_ctx.close()
```

## 注意事项
1. 获取期权到期日前需要先建立行情连接
2. 可以同时获取多个股票的期权到期日信息
3. 期权到期日信息更新频率较低，建议缓存使用
4. 期权到期日信息主要用于期权交易，建议结合期权链数据一起使用
5. 需要注意处理异常情况，避免程序崩溃 