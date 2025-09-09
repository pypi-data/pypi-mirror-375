# 获取资金分布接口文档

## 接口功能
用于获取指定股票的资金分布数据，包括不同价格区间的资金分布情况。

## 接口模块
Quote API - 基础数据模块

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
        "capital_distribution_list": [
            {
                "code": "HK.00700",
                "update_time": "2024-03-20 10:00:00",
                "price_ranges": [
                    {
                        "price": 300.0,
                        "volume": 1000000,
                        "amount": 300000000,
                        "ratio": 0.2
                    },
                    {
                        "price": 310.0,
                        "volume": 1500000,
                        "amount": 465000000,
                        "ratio": 0.3
                    },
                    {
                        "price": 320.0,
                        "volume": 2000000,
                        "amount": 640000000,
                        "ratio": 0.4
                    }
                ],
                "total_volume": 4500000,
                "total_amount": 1405000000
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
| 1017 | GET_CAPITAL_DISTRIBUTION_FAILED | 获取资金分布数据失败 |

## 示例代码
```python
from futu import *

# 创建行情连接
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

# 获取资金分布数据
ret, data = quote_ctx.get_capital_distribution(['HK.00700'])
if ret == RET_OK:
    print('获取资金分布数据成功')
    for dist in data:
        print(f"股票代码: {dist['code']}")
        print(f"更新时间: {dist['update_time']}")
        print("价格区间分布:")
        for range_data in dist['price_ranges']:
            print(f"价格: {range_data['price']}")
            print(f"成交量: {range_data['volume']}")
            print(f"成交额: {range_data['amount']}")
            print(f"占比: {range_data['ratio']}")
            print("-------------------")
        print(f"总成交量: {dist['total_volume']}")
        print(f"总成交额: {dist['total_amount']}")
else:
    print('获取资金分布数据失败:', data)

# 关闭连接
quote_ctx.close()
```

## 注意事项
1. 获取资金分布数据前需要先建立行情连接
2. 可以同时获取多个股票的资金分布数据
3. 资金分布数据更新频率较高，建议根据实际需求选择获取的股票
4. 资金分布数据主要用于分析价格区间的资金分布情况，建议结合其他指标一起使用
5. 需要注意处理异常情况，避免程序崩溃 