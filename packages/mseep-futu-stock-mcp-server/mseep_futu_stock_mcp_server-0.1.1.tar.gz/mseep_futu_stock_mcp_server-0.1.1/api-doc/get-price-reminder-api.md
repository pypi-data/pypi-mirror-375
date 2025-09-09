# 获取价格提醒列表接口文档

## 接口功能
用于获取已设置的价格提醒列表。

## 接口模块
Quote API - 自定义模块

## 接口参数
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| market | string | 否 | 市场代码，例如"HK"、"US"等，不传则返回所有市场的提醒 |
| status | string | 否 | 提醒状态，可选值："ACTIVE"（活跃）、"INACTIVE"（非活跃）、"TRIGGERED"（已触发），默认为"ACTIVE" |
| start_time | string | 否 | 开始时间，格式为"YYYY-MM-DD HH:MM:SS"，默认为当前时间前30天 |
| end_time | string | 否 | 结束时间，格式为"YYYY-MM-DD HH:MM:SS"，默认为当前时间 |
| max_count | int | 否 | 最大返回数据条数，默认为100 |

## 接口返回结果
```json
{
    "ret_code": 0,
    "ret_msg": "SUCCESS",
    "data": {
        "reminder_list": [
            {
                "reminder_id": "123456789",
                "stock_code": "HK.00700",
                "stock_name": "腾讯控股",
                "market": "HK",
                "price": 300.0,
                "op": ">=",
                "frequency": "ONCE",
                "is_relative": false,
                "relative_price": null,
                "relative_type": null,
                "relative_op": null,
                "remark": "提醒测试",
                "create_time": "2024-03-20 10:30:00",
                "trigger_time": null,
                "status": "ACTIVE"
            },
            {
                "reminder_id": "987654321",
                "stock_code": "HK.03690",
                "stock_name": "美团-W",
                "market": "HK",
                "price": 100.0,
                "op": "<=",
                "frequency": "EVERY",
                "is_relative": true,
                "relative_price": 5.0,
                "relative_type": "PERCENT",
                "relative_op": "-",
                "remark": "提醒测试2",
                "create_time": "2024-03-19 15:30:00",
                "trigger_time": "2024-03-20 09:30:00",
                "status": "TRIGGERED"
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
| 1006 | INVALID_TIME | 时间格式错误 |
| 1007 | INVALID_COUNT | 数据条数错误 |
| 1048 | GET_PRICE_REMINDER_FAILED | 获取价格提醒列表失败 |

## 示例代码
```python
from futu import *

# 创建行情连接
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

# 获取价格提醒列表
ret, data = quote_ctx.get_price_reminder(
    market="HK",
    status="ACTIVE",
    start_time="2024-03-01 00:00:00",
    end_time="2024-03-20 23:59:59",
    max_count=100
)
if ret == RET_OK:
    print('获取价格提醒列表成功')
    print("提醒列表:")
    for reminder in data['reminder_list']:
        print(f"提醒ID: {reminder['reminder_id']}")
        print(f"股票代码: {reminder['stock_code']}")
        print(f"股票名称: {reminder['stock_name']}")
        print(f"市场: {reminder['market']}")
        print(f"提醒价格: {reminder['price']}")
        print(f"操作符: {reminder['op']}")
        print(f"提醒频率: {reminder['frequency']}")
        print(f"是否为相对价格: {reminder['is_relative']}")
        if reminder['is_relative']:
            print(f"相对价格: {reminder['relative_price']}")
            print(f"相对类型: {reminder['relative_type']}")
            print(f"相对操作符: {reminder['relative_op']}")
        print(f"备注: {reminder['remark']}")
        print(f"创建时间: {reminder['create_time']}")
        if reminder['trigger_time']:
            print(f"触发时间: {reminder['trigger_time']}")
        print(f"状态: {reminder['status']}")
        print("-------------------")
else:
    print('获取价格提醒列表失败:', data)

# 关闭连接
quote_ctx.close()
```

## 注意事项
1. 获取价格提醒列表前需要先建立行情连接
2. 市场代码必须是有效的市场代码
3. 时间范围必须在有效范围内
4. 需要注意处理异常情况，避免程序崩溃
5. 价格提醒信息包括：
   - 提醒ID
   - 股票代码和名称
   - 市场
   - 提醒价格
   - 操作符
   - 提醒频率
   - 相对价格信息（如果有）
   - 备注
   - 创建时间
   - 触发时间（如果有）
   - 状态
6. 这些信息对于管理价格提醒非常重要 