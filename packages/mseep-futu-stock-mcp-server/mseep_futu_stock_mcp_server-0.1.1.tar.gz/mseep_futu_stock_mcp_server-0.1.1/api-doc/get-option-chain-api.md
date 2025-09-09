# 获取期权链接口文档

## 接口功能
用于获取指定标的的期权链信息，包括各个行权价和到期日的期权合约信息。

## 接口模块
Quote API - 相关衍生品模块

## 接口参数
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| stock_code | string | 是 | 标的股票代码，格式为"market.code"，例如"HK.00700" |
| market | string | 否 | 市场代码，例如"HK"、"US"等，如果不填则从stock_code中解析 |
| expiry_date | string | 否 | 到期日，格式为"YYYY-MM-DD"，如果不填则返回所有到期日 |
| option_type | string | 否 | 期权类型，可选值："CALL"（认购）、"PUT"（认沽），如果不填则返回所有类型 |
| strike_price | float | 否 | 行权价，如果不填则返回所有行权价 |
| max_count | int | 否 | 最大返回数量，默认为100 |

## 接口返回结果
```json
{
    "ret_code": 0,
    "ret_msg": "SUCCESS",
    "data": {
        "stock_code": "HK.00700",
        "stock_name": "腾讯控股",
        "option_list": [
            {
                "option_code": "HK.00700C20240320",
                "option_name": "腾讯控股认购期权",
                "option_type": "CALL",
                "strike_price": 300.0,
                "expiry_date": "2024-03-20",
                "last_price": 5.2,
                "volume": 1000,
                "open_interest": 5000,
                "implied_volatility": 0.25,
                "delta": 0.6,
                "gamma": 0.02,
                "theta": -0.1,
                "vega": 0.15,
                "update_time": "2024-03-20 10:30:00"
            },
            {
                "option_code": "HK.00700P20240320",
                "option_name": "腾讯控股认沽期权",
                "option_type": "PUT",
                "strike_price": 300.0,
                "expiry_date": "2024-03-20",
                "last_price": 4.8,
                "volume": 800,
                "open_interest": 4000,
                "implied_volatility": 0.28,
                "delta": -0.4,
                "gamma": 0.02,
                "theta": -0.08,
                "vega": 0.12,
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
| 1003 | INVALID_STOCKCODE | 股票代码错误 |
| 1004 | INVALID_EXPIRYDATE | 到期日错误 |
| 1005 | INVALID_OPTIONTYPE | 期权类型错误 |
| 1006 | INVALID_STRIKEPRICE | 行权价错误 |
| 1007 | INVALID_COUNT | 数量错误 |
| 1055 | GET_OPTION_CHAIN_FAILED | 获取期权链失败 |

## 示例代码
```python
from futu import *

# 创建行情连接
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

# 获取期权链
ret, data = quote_ctx.get_option_chain(
    stock_code="HK.00700",
    market="HK",
    expiry_date="2024-03-20",
    option_type="CALL",
    strike_price=300.0,
    max_count=50
)
if ret == RET_OK:
    print('获取期权链成功')
    print(f"标的代码: {data['stock_code']}")
    print(f"标的名称: {data['stock_name']}")
    print("期权列表:")
    for option in data['option_list']:
        print(f"期权代码: {option['option_code']}")
        print(f"期权名称: {option['option_name']}")
        print(f"期权类型: {option['option_type']}")
        print(f"行权价: {option['strike_price']}")
        print(f"到期日: {option['expiry_date']}")
        print(f"最新价: {option['last_price']}")
        print(f"成交量: {option['volume']}")
        print(f"持仓量: {option['open_interest']}")
        print(f"隐含波动率: {option['implied_volatility']}")
        print(f"Delta: {option['delta']}")
        print(f"Gamma: {option['gamma']}")
        print(f"Theta: {option['theta']}")
        print(f"Vega: {option['vega']}")
        print(f"更新时间: {option['update_time']}")
        print("-------------------")
else:
    print('获取期权链失败:', data)

# 关闭连接
quote_ctx.close()
```

## 注意事项
1. 获取期权链前需要先建立行情连接
2. 股票代码需要按照指定格式填写
3. 市场代码必须是有效的市场代码
4. 到期日必须是有效的日期
5. 期权类型必须是有效的类型
6. 行权价必须是有效的价格
7. 需要注意处理异常情况，避免程序崩溃
8. 返回的数据包含标的股票信息和期权列表，如：
   - 标的股票代码和名称
   - 期权列表（包含期权代码、名称、类型、行权价、到期日等信息）
   - 期权价格和交易数据
   - 期权希腊字母（Delta、Gamma、Theta、Vega等）
9. 这些信息对于期权交易和风险管理非常重要 