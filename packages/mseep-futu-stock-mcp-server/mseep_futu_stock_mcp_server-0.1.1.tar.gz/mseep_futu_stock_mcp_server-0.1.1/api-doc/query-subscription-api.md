# 查询订阅状态接口文档

## 接口功能
用于查询当前连接下所有已订阅的股票、期货、期权等金融产品的实时行情数据订阅状态。

## 接口模块
Quote API - 实时数据订阅模块

## 接口参数
无参数

## 接口返回结果
```json
{
    "ret_code": 0,
    "ret_msg": "SUCCESS",
    "data": {
        "sub_list": [
            {
                "code": "HK.00700",
                "subtype": "QUOTE",
                "is_subscribed": true
            },
            {
                "code": "HK.00700",
                "subtype": "ORDER_BOOK",
                "is_subscribed": true
            }
        ]
    }
}
```

## 接口异常情况
| 错误码 | 错误信息 | 说明 |
|--------|----------|------|
| 1006 | QUERY_SUBSCRIPTION_FAILED | 查询订阅状态失败 |

## 示例代码
```python
from futu import *

# 创建行情连接
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

# 查询订阅状态
ret, data = quote_ctx.query_subscription()
if ret == RET_OK:
    print('查询订阅状态成功')
    for sub in data:
        print(f"股票代码: {sub['code']}, 订阅类型: {sub['subtype']}, 订阅状态: {sub['is_subscribed']}")
else:
    print('查询订阅状态失败:', ret)

# 关闭连接
quote_ctx.close()
```

## 注意事项
1. 查询订阅状态前需要先建立行情连接
2. 返回的订阅列表包含所有当前连接的订阅信息
3. 可以通过此接口检查订阅是否成功
4. 建议在订阅后调用此接口确认订阅状态 