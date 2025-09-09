# 设置价格提醒接口文档

## 接口功能
用于设置股票价格提醒，当股票价格达到设定条件时触发提醒。

## 接口模块
Quote API - 自定义模块

## 接口参数
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| stock_code | string | 是 | 股票代码，格式为"market.code"，例如"HK.00700" |
| market | string | 否 | 市场代码，例如"HK"、"US"等 |
| price | float | 是 | 提醒价格 |
| op | string | 是 | 操作符，可选值："<="（小于等于）、">="（大于等于） |
| frequency | string | 否 | 提醒频率，可选值："ONCE"（一次）、"EVERY"（每次），默认为"ONCE" |
| is_relative | bool | 否 | 是否为相对价格，默认为false |
| relative_price | float | 否 | 相对价格，当is_relative为true时必填 |
| relative_type | string | 否 | 相对类型，可选值："PERCENT"（百分比）、"PRICE"（价格），当is_relative为true时必填 |
| relative_op | string | 否 | 相对操作符，可选值："+"（加）、"-"（减），当is_relative为true时必填 |
| remark | string | 否 | 备注信息 |

## 接口返回结果
```json
{
    "ret_code": 0,
    "ret_msg": "SUCCESS",
    "data": {
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
        "status": "ACTIVE"
    }
}
```

## 接口异常情况
| 错误码 | 错误信息 | 说明 |
|--------|----------|------|
| 1001 | INVALID_PARAM | 参数错误 |
| 1002 | INVALID_MARKET | 市场代码错误 |
| 1003 | INVALID_STOCKCODE | 股票代码错误 |
| 1008 | INVALID_PRICE | 价格错误 |
| 1009 | INVALID_OP | 操作符错误 |
| 1010 | INVALID_FREQUENCY | 提醒频率错误 |
| 1011 | INVALID_RELATIVE_TYPE | 相对类型错误 |
| 1012 | INVALID_RELATIVE_OP | 相对操作符错误 |
| 1047 | SET_PRICE_REMINDER_FAILED | 设置价格提醒失败 |

## 示例代码
```python
from futu import *

# 创建行情连接
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

# 设置价格提醒
ret, data = quote_ctx.set_price_reminder(
    stock_code="HK.00700",
    market="HK",
    price=300.0,
    op=">=",
    frequency="ONCE",
    is_relative=False,
    remark="提醒测试"
)
if ret == RET_OK:
    print('设置价格提醒成功')
    print(f"提醒ID: {data['reminder_id']}")
    print(f"股票代码: {data['stock_code']}")
    print(f"股票名称: {data['stock_name']}")
    print(f"市场: {data['market']}")
    print(f"提醒价格: {data['price']}")
    print(f"操作符: {data['op']}")
    print(f"提醒频率: {data['frequency']}")
    print(f"是否为相对价格: {data['is_relative']}")
    if data['is_relative']:
        print(f"相对价格: {data['relative_price']}")
        print(f"相对类型: {data['relative_type']}")
        print(f"相对操作符: {data['relative_op']}")
    print(f"备注: {data['remark']}")
    print(f"创建时间: {data['create_time']}")
    print(f"状态: {data['status']}")
else:
    print('设置价格提醒失败:', data)

# 关闭连接
quote_ctx.close()
```

## 注意事项
1. 设置价格提醒前需要先建立行情连接
2. 股票代码需要按照指定格式填写
3. 价格必须是有效的价格
4. 操作符必须是有效的操作符
5. 提醒频率必须是有效的频率
6. 如果使用相对价格，需要填写相对价格、相对类型和相对操作符
7. 需要注意处理异常情况，避免程序崩溃
8. 价格提醒信息包括：
   - 提醒ID
   - 股票代码和名称
   - 市场
   - 提醒价格
   - 操作符
   - 提醒频率
   - 相对价格信息（如果有）
   - 备注
   - 创建时间
   - 状态
9. 这些信息对于设置和管理价格提醒非常重要 