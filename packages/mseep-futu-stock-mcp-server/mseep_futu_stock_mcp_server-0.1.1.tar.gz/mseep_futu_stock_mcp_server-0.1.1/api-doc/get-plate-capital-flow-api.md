# 获取板块资金流向接口文档

## 接口功能
用于获取指定板块的资金流向数据，包括主力净流入、散户净流入等。

## 接口模块
Quote API - 资金流向模块

## 接口参数
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| plate_code | string | 是 | 板块代码，格式为"market.type.code"，例如"HK.INDUSTRY.IT" |
| market | string | 否 | 市场代码，例如"HK"、"US"等 |
| start_time | string | 否 | 开始时间，格式为"YYYY-MM-DD HH:MM:SS"，默认为当天开盘时间 |
| end_time | string | 否 | 结束时间，格式为"YYYY-MM-DD HH:MM:SS"，默认为当前时间 |
| period | string | 否 | 统计周期，可选值：DAY(日)、WEEK(周)、MONTH(月)，默认为DAY |

## 接口返回结果
```json
{
    "ret_code": 0,
    "ret_msg": "SUCCESS",
    "data": {
        "plate_code": "HK.INDUSTRY.IT",
        "plate_name": "信息技术",
        "market": "HK",
        "capital_flow": [
            {
                "time": "2024-03-20 10:00:00",
                "main_net_inflow": 1000000000,
                "retail_net_inflow": -500000000,
                "total_net_inflow": 500000000,
                "main_inflow_ratio": 0.6,
                "retail_inflow_ratio": 0.4,
                "update_time": "2024-03-20 10:00:00"
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
| 1004 | INVALID_TIME | 时间格式错误 |
| 1005 | INVALID_PERIOD | 统计周期错误 |
| 1029 | GET_PLATE_CAPITAL_FLOW_FAILED | 获取板块资金流向失败 |

## 示例代码
```python
from futu import *

# 创建行情连接
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

# 获取板块资金流向
ret, data = quote_ctx.get_plate_capital_flow(
    plate_code="HK.INDUSTRY.IT",
    market="HK",
    start_time="2024-03-20 09:30:00",
    end_time="2024-03-20 16:00:00",
    period="DAY"
)
if ret == RET_OK:
    print('获取板块资金流向成功')
    print(f"板块代码: {data['plate_code']}")
    print(f"板块名称: {data['plate_name']}")
    print(f"市场: {data['market']}")
    print("资金流向数据:")
    for flow in data['capital_flow']:
        print(f"时间: {flow['time']}")
        print(f"主力净流入: {flow['main_net_inflow']}")
        print(f"散户净流入: {flow['retail_net_inflow']}")
        print(f"总净流入: {flow['total_net_inflow']}")
        print(f"主力流入占比: {flow['main_inflow_ratio']}")
        print(f"散户流入占比: {flow['retail_inflow_ratio']}")
        print(f"更新时间: {flow['update_time']}")
        print("-------------------")
else:
    print('获取板块资金流向失败:', data)

# 关闭连接
quote_ctx.close()
```

## 注意事项
1. 获取板块资金流向前需要先建立行情连接
2. 板块代码需要按照指定格式填写
3. 时间范围不能超过30天
4. 资金流向数据主要用于分析板块资金动向，建议结合其他指标一起使用
5. 需要注意处理异常情况，避免程序崩溃 