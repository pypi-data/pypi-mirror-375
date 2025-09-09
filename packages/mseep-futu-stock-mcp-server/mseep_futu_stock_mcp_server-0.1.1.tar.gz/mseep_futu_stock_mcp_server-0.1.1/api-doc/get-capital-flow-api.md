# 获取资金流向接口文档

## 接口功能
用于获取指定股票的资金流向数据，包括主力资金、散户资金等流向信息。

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
        "capital_flow_list": [
            {
                "code": "HK.00700",
                "update_time": "2024-03-20 10:00:00",
                "main_net_inflow": 1000000,
                "main_net_inflow_ratio": 0.5,
                "retail_net_inflow": 500000,
                "retail_net_inflow_ratio": 0.3,
                "super_net_inflow": 2000000,
                "super_net_inflow_ratio": 0.7,
                "large_net_inflow": 1500000,
                "large_net_inflow_ratio": 0.6,
                "medium_net_inflow": 800000,
                "medium_net_inflow_ratio": 0.4,
                "small_net_inflow": 300000,
                "small_net_inflow_ratio": 0.2
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
| 1016 | GET_CAPITAL_FLOW_FAILED | 获取资金流向数据失败 |

## 示例代码
```python
from futu import *

# 创建行情连接
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

# 获取资金流向数据
ret, data = quote_ctx.get_capital_flow(['HK.00700'])
if ret == RET_OK:
    print('获取资金流向数据成功')
    for flow in data:
        print(f"股票代码: {flow['code']}")
        print(f"更新时间: {flow['update_time']}")
        print(f"主力净流入: {flow['main_net_inflow']}")
        print(f"主力净流入比例: {flow['main_net_inflow_ratio']}")
        print(f"散户净流入: {flow['retail_net_inflow']}")
        print(f"散户净流入比例: {flow['retail_net_inflow_ratio']}")
        print(f"超大单净流入: {flow['super_net_inflow']}")
        print(f"超大单净流入比例: {flow['super_net_inflow_ratio']}")
        print(f"大单净流入: {flow['large_net_inflow']}")
        print(f"大单净流入比例: {flow['large_net_inflow_ratio']}")
        print(f"中单净流入: {flow['medium_net_inflow']}")
        print(f"中单净流入比例: {flow['medium_net_inflow_ratio']}")
        print(f"小单净流入: {flow['small_net_inflow']}")
        print(f"小单净流入比例: {flow['small_net_inflow_ratio']}")
else:
    print('获取资金流向数据失败:', data)

# 关闭连接
quote_ctx.close()
```

## 注意事项
1. 获取资金流向数据前需要先建立行情连接
2. 可以同时获取多个股票的资金流向数据
3. 资金流向数据更新频率较高，建议根据实际需求选择获取的股票
4. 资金流向数据主要用于分析资金动向，建议结合其他指标一起使用
5. 需要注意处理异常情况，避免程序崩溃 