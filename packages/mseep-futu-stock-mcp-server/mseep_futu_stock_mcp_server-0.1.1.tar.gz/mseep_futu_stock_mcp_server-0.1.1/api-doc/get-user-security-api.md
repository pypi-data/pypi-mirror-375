# 获取用户自选股列表接口文档

## 接口功能
用于获取用户的自选股列表。

## 接口模块
Quote API - 自定义模块

## 接口参数
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| group_id | string | 否 | 分组ID，不传则返回所有分组的自选股 |
| market | string | 否 | 市场代码，例如"HK"、"US"等，不传则返回所有市场的自选股 |
| max_count | int | 否 | 最大返回数据条数，默认为100 |

## 接口返回结果
```json
{
    "ret_code": 0,
    "ret_msg": "SUCCESS",
    "data": {
        "security_list": [
            {
                "stock_code": "HK.00700",
                "stock_name": "腾讯控股",
                "market": "HK",
                "group_id": "123456789",
                "group_name": "港股",
                "add_time": "2024-03-20 10:30:00",
                "remark": "互联网龙头",
                "price": 300.0,
                "change": 5.0,
                "change_ratio": 0.0167
            },
            {
                "stock_code": "HK.03690",
                "stock_name": "美团-W",
                "market": "HK",
                "group_id": "123456789",
                "group_name": "港股",
                "add_time": "2024-03-19 15:30:00",
                "remark": "本地生活",
                "price": 100.0,
                "change": -2.0,
                "change_ratio": -0.02
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
| 1007 | INVALID_COUNT | 数据条数错误 |
| 1050 | GET_USER_SECURITY_FAILED | 获取用户自选股列表失败 |

## 示例代码
```python
from futu import *

# 创建行情连接
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

# 获取用户自选股列表
ret, data = quote_ctx.get_user_security(
    group_id="123456789",  # 可选参数
    market="HK",  # 可选参数
    max_count=100
)
if ret == RET_OK:
    print('获取用户自选股列表成功')
    print("自选股列表:")
    for security in data['security_list']:
        print(f"股票代码: {security['stock_code']}")
        print(f"股票名称: {security['stock_name']}")
        print(f"市场: {security['market']}")
        print(f"分组ID: {security['group_id']}")
        print(f"分组名称: {security['group_name']}")
        print(f"添加时间: {security['add_time']}")
        print(f"备注: {security['remark']}")
        print(f"当前价格: {security['price']}")
        print(f"涨跌幅: {security['change']}")
        print(f"涨跌比率: {security['change_ratio']}")
        print("-------------------")
else:
    print('获取用户自选股列表失败:', data)

# 关闭连接
quote_ctx.close()
```

## 注意事项
1. 获取用户自选股列表前需要先建立行情连接
2. 分组ID必须是有效的分组ID
3. 市场代码必须是有效的市场代码
4. 需要注意处理异常情况，避免程序崩溃
5. 自选股信息包括：
   - 股票代码和名称
   - 市场
   - 分组信息（分组ID和名称）
   - 添加时间
   - 备注
   - 当前价格
   - 涨跌幅和涨跌比率
6. 这些信息对于管理用户自选股非常重要 