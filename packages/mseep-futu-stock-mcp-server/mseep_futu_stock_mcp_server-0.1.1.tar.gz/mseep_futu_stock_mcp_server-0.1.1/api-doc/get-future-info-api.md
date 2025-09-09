# 获取期货信息接口文档

## 接口功能
用于获取指定期货合约的基本信息，包括合约代码、名称、交易单位等。

## 接口模块
Quote API - 相关衍生品模块

## 接口参数
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| stock_list | list | 是 | 期货合约代码列表，格式为["市场.代码"]，例如["HK.HSI"] |
| market | string | 否 | 市场代码，例如"HK"、"US"等，默认为空 |

## 接口返回结果
```json
{
    "ret_code": 0,
    "ret_msg": "SUCCESS",
    "data": {
        "future_info_list": [
            {
                "code": "HK.HSI",
                "update_time": "2024-03-20 10:00:00",
                "future_info": {
                    "name": "恒生指数期货",
                    "contract_size": 50,
                    "price_tick": 1,
                    "trading_unit": "HKD",
                    "delivery_month": "2024-03",
                    "last_trading_date": "2024-03-28",
                    "delivery_date": "2024-03-29",
                    "trading_hours": "09:15-12:00,13:00-16:30",
                    "settlement_method": "CASH",
                    "margin_ratio": 0.1,
                    "commission_rate": 0.0001,
                    "min_price_limit": -10,
                    "max_price_limit": 10,
                    "underlying_code": "HK.HSI",
                    "underlying_name": "恒生指数"
                }
            }
        ]
    }
}
```

## 接口异常情况
| 错误码 | 错误信息 | 说明 |
|--------|----------|------|
| 1001 | INVALID_PARAM | 参数错误 |
| 1002 | INVALID_CODE | 期货合约代码格式错误 |
| 1025 | GET_FUTURE_INFO_FAILED | 获取期货信息失败 |

## 示例代码
```python
from futu import *

# 创建行情连接
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

# 获取期货信息
ret, data = quote_ctx.get_future_info(['HK.HSI'])
if ret == RET_OK:
    print('获取期货信息成功')
    for future in data:
        print(f"期货合约代码: {future['code']}")
        print(f"更新时间: {future['update_time']}")
        info = future['future_info']
        print(f"期货名称: {info['name']}")
        print(f"合约乘数: {info['contract_size']}")
        print(f"最小变动价位: {info['price_tick']}")
        print(f"交易单位: {info['trading_unit']}")
        print(f"交割月份: {info['delivery_month']}")
        print(f"最后交易日: {info['last_trading_date']}")
        print(f"交割日期: {info['delivery_date']}")
        print(f"交易时间: {info['trading_hours']}")
        print(f"交割方式: {info['settlement_method']}")
        print(f"保证金比例: {info['margin_ratio']}")
        print(f"手续费率: {info['commission_rate']}")
        print(f"最小价格限制: {info['min_price_limit']}")
        print(f"最大价格限制: {info['max_price_limit']}")
        print(f"标的代码: {info['underlying_code']}")
        print(f"标的名称: {info['underlying_name']}")
else:
    print('获取期货信息失败:', data)

# 关闭连接
quote_ctx.close()
```

## 注意事项
1. 获取期货信息前需要先建立行情连接
2. 可以同时获取多个期货合约的信息
3. 期货信息更新频率较低，建议缓存使用
4. 期货信息主要用于期货交易，建议结合其他指标一起使用
5. 需要注意处理异常情况，避免程序崩溃 