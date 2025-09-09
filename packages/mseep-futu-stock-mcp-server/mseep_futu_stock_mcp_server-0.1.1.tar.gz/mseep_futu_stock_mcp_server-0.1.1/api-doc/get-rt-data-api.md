# 获取实时分时数据接口文档

## 接口功能
用于获取指定股票的实时分时数据，包括分时价格、成交量等信息。

## 接口模块
Quote API - 实时数据获取模块

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
        "rt_data_list": [
            {
                "code": "HK.00700",
                "time": "10:00:00",
                "price": 350.0,
                "volume": 1000000,
                "turnover": 350000000.0,
                "avg_price": 350.0,
                "timestamp": "2024-03-20 10:00:00",
                "rt_data_status": 0
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
| 1011 | GET_RT_DATA_FAILED | 获取实时分时数据失败 |

## 示例代码
```python
from futu import *

# 创建行情连接
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

# 获取实时分时数据
ret, data = quote_ctx.get_rt_data(['HK.00700'])
if ret == RET_OK:
    print('获取实时分时数据成功')
    for rt_data in data:
        print(f"股票代码: {rt_data['code']}")
        print(f"时间: {rt_data['time']}")
        print(f"价格: {rt_data['price']}")
        print(f"成交量: {rt_data['volume']}")
        print(f"成交额: {rt_data['turnover']}")
        print(f"均价: {rt_data['avg_price']}")
else:
    print('获取实时分时数据失败:', data)

# 关闭连接
quote_ctx.close()
```

## 注意事项
1. 获取实时分时数据前需要先建立行情连接
2. 可以同时获取多个股票的实时分时数据
3. 实时分时数据包含最新的分时信息，但不包含历史数据
4. 实时分时数据更新频率较高，建议根据实际需求选择获取的股票
5. 需要注意处理异常情况，避免程序崩溃 