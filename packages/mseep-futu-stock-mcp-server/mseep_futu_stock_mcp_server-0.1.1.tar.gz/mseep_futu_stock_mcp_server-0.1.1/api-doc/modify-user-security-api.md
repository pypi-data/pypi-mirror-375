# 修改用户自选股接口文档

## 接口功能
用于修改用户的自选股，包括添加、删除、修改分组等操作。

## 接口模块
Quote API - 自定义模块

## 接口参数
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| op | string | 是 | 操作类型，可选值："ADD"（添加）、"DEL"（删除）、"MOD"（修改） |
| stock_code | string | 是 | 股票代码，格式为"market.code"，例如"HK.00700" |
| market | string | 否 | 市场代码，例如"HK"、"US"等 |
| group_id | string | 否 | 分组ID，当op为"ADD"或"MOD"时必填 |
| remark | string | 否 | 备注信息，当op为"ADD"或"MOD"时可选 |

## 接口返回结果
```json
{
    "ret_code": 0,
    "ret_msg": "SUCCESS",
    "data": {
        "op": "ADD",
        "stock_code": "HK.00700",
        "stock_name": "腾讯控股",
        "market": "HK",
        "group_id": "123456789",
        "group_name": "港股",
        "remark": "互联网龙头",
        "update_time": "2024-03-20 10:30:00"
    }
}
```

## 接口异常情况
| 错误码 | 错误信息 | 说明 |
|--------|----------|------|
| 1001 | INVALID_PARAM | 参数错误 |
| 1002 | INVALID_MARKET | 市场代码错误 |
| 1003 | INVALID_STOCKCODE | 股票代码错误 |
| 1013 | INVALID_OP | 操作类型错误 |
| 1014 | INVALID_GROUPID | 分组ID错误 |
| 1051 | MODIFY_USER_SECURITY_FAILED | 修改用户自选股失败 |

## 示例代码
```python
from futu import *

# 创建行情连接
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

# 添加自选股
ret, data = quote_ctx.modify_user_security(
    op="ADD",
    stock_code="HK.00700",
    market="HK",
    group_id="123456789",
    remark="互联网龙头"
)
if ret == RET_OK:
    print('修改用户自选股成功')
    print(f"操作类型: {data['op']}")
    print(f"股票代码: {data['stock_code']}")
    print(f"股票名称: {data['stock_name']}")
    print(f"市场: {data['market']}")
    print(f"分组ID: {data['group_id']}")
    print(f"分组名称: {data['group_name']}")
    print(f"备注: {data['remark']}")
    print(f"更新时间: {data['update_time']}")
else:
    print('修改用户自选股失败:', data)

# 删除自选股
ret, data = quote_ctx.modify_user_security(
    op="DEL",
    stock_code="HK.00700",
    market="HK"
)
if ret == RET_OK:
    print('删除用户自选股成功')
else:
    print('删除用户自选股失败:', data)

# 修改自选股
ret, data = quote_ctx.modify_user_security(
    op="MOD",
    stock_code="HK.00700",
    market="HK",
    group_id="987654321",
    remark="修改备注"
)
if ret == RET_OK:
    print('修改用户自选股成功')
else:
    print('修改用户自选股失败:', data)

# 关闭连接
quote_ctx.close()
```

## 注意事项
1. 修改用户自选股前需要先建立行情连接
2. 股票代码需要按照指定格式填写
3. 市场代码必须是有效的市场代码
4. 分组ID必须是有效的分组ID
5. 需要注意处理异常情况，避免程序崩溃
6. 修改操作包括：
   - 添加自选股
   - 删除自选股
   - 修改自选股（包括修改分组和备注）
7. 这些操作对于管理用户自选股非常重要 