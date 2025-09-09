# 获取用户自选股分组接口文档

## 接口功能
用于获取用户的自选股分组列表。

## 接口模块
Quote API - 自定义模块

## 接口参数
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| market | string | 否 | 市场代码，例如"HK"、"US"等，不传则返回所有市场的分组 |

## 接口返回结果
```json
{
    "ret_code": 0,
    "ret_msg": "SUCCESS",
    "data": {
        "group_list": [
            {
                "group_id": "123456789",
                "group_name": "港股",
                "market": "HK",
                "stock_count": 10,
                "create_time": "2024-03-20 10:30:00",
                "update_time": "2024-03-20 10:30:00",
                "is_default": true
            },
            {
                "group_id": "987654321",
                "group_name": "美股",
                "market": "US",
                "stock_count": 5,
                "create_time": "2024-03-19 15:30:00",
                "update_time": "2024-03-19 15:30:00",
                "is_default": false
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
| 1049 | GET_USER_SECURITY_GROUP_FAILED | 获取用户自选股分组失败 |

## 示例代码
```python
from futu import *

# 创建行情连接
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

# 获取用户自选股分组
ret, data = quote_ctx.get_user_security_group(
    market="HK"  # 可选参数，不传则返回所有市场的分组
)
if ret == RET_OK:
    print('获取用户自选股分组成功')
    print("分组列表:")
    for group in data['group_list']:
        print(f"分组ID: {group['group_id']}")
        print(f"分组名称: {group['group_name']}")
        print(f"市场: {group['market']}")
        print(f"股票数量: {group['stock_count']}")
        print(f"创建时间: {group['create_time']}")
        print(f"更新时间: {group['update_time']}")
        print(f"是否为默认分组: {group['is_default']}")
        print("-------------------")
else:
    print('获取用户自选股分组失败:', data)

# 关闭连接
quote_ctx.close()
```

## 注意事项
1. 获取用户自选股分组前需要先建立行情连接
2. 市场代码必须是有效的市场代码
3. 需要注意处理异常情况，避免程序崩溃
4. 分组信息包括：
   - 分组ID
   - 分组名称
   - 市场
   - 股票数量
   - 创建时间
   - 更新时间
   - 是否为默认分组
5. 这些信息对于管理用户自选股分组非常重要 