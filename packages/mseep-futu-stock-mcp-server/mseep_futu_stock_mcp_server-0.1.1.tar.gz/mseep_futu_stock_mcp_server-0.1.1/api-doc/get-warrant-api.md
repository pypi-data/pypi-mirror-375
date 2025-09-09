# 获取窝轮接口文档

## 接口功能
用于获取指定股票的窝轮数据，包括窝轮代码、名称、行权价等信息。

## 接口模块
Quote API - 相关衍生品模块

## 接口参数
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| stock_list | list | 是 | 股票代码列表，格式为["市场.代码"]，例如["HK.00700"] |
| market | string | 否 | 市场代码，例如"HK"、"US"等，默认为空 |
| warrant_type | string | 否 | 窝轮类型，可选值：CALL(认购证)、PUT(认沽证)，默认为空(获取所有类型) |

## 接口返回结果
```json
{
    "ret_code": 0,
    "ret_msg": "SUCCESS",
    "data": {
        "warrant_list": [
            {
                "code": "HK.00700",
                "update_time": "2024-03-20 10:00:00",
                "warrants": [
                    {
                        "warrant_code": "HK.12345",
                        "warrant_name": "腾讯控股认购证",
                        "warrant_type": "CALL",
                        "strike_price": 300.0,
                        "maturity_date": "2024-06-26",
                        "conversion_ratio": 10,
                        "last_price": 0.5,
                        "volume": 1000000,
                        "issuer": "高盛",
                        "issuer_code": "GS",
                        "leverage": 5.0,
                        "premium": 0.1,
                        "implied_volatility": 0.3,
                        "delta": 0.5,
                        "gamma": 0.1,
                        "theta": -0.05,
                        "vega": 0.2,
                        "rho": 0.01
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
| 1007 | INVALID_WARRANTTYPE | 窝轮类型错误 |
| 1023 | GET_WARRANT_FAILED | 获取窝轮数据失败 |

## 示例代码
```python
from futu import *

# 创建行情连接
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

# 获取窝轮数据
ret, data = quote_ctx.get_warrant(
    ['HK.00700'],
    warrant_type='CALL'
)
if ret == RET_OK:
    print('获取窝轮数据成功')
    for warrant in data:
        print(f"股票代码: {warrant['code']}")
        print(f"更新时间: {warrant['update_time']}")
        print("窝轮信息:")
        for w in warrant['warrants']:
            print(f"窝轮代码: {w['warrant_code']}")
            print(f"窝轮名称: {w['warrant_name']}")
            print(f"窝轮类型: {w['warrant_type']}")
            print(f"行权价: {w['strike_price']}")
            print(f"到期日: {w['maturity_date']}")
            print(f"换股比率: {w['conversion_ratio']}")
            print(f"最新价: {w['last_price']}")
            print(f"成交量: {w['volume']}")
            print(f"发行人: {w['issuer']}")
            print(f"发行人代码: {w['issuer_code']}")
            print(f"杠杆比率: {w['leverage']}")
            print(f"溢价率: {w['premium']}")
            print(f"隐含波动率: {w['implied_volatility']}")
            print(f"Delta: {w['delta']}")
            print(f"Gamma: {w['gamma']}")
            print(f"Theta: {w['theta']}")
            print(f"Vega: {w['vega']}")
            print(f"Rho: {w['rho']}")
            print("-------------------")
else:
    print('获取窝轮数据失败:', data)

# 关闭连接
quote_ctx.close()
```

## 注意事项
1. 获取窝轮数据前需要先建立行情连接
2. 可以同时获取多个股票的窝轮数据
3. 窝轮数据更新频率较高，建议根据实际需求选择获取的股票
4. 窝轮数据主要用于窝轮交易，建议结合正股数据一起使用
5. 需要注意处理异常情况，避免程序崩溃 