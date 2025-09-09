# 获取板块成分股接口文档

## 接口功能
用于获取指定板块的成分股列表，包括股票代码、名称、权重等信息。

## 接口模块
Quote API - 市场筛选模块

## 接口参数
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| plate_code | string | 是 | 板块代码，例如"HK.BK1001" |
| market | string | 否 | 市场代码，例如"HK"、"US"等，如果不填则从plate_code中解析 |
| sort_field | string | 否 | 排序字段，可选值："code"（代码）、"name"（名称）、"weight"（权重） |
| asc | bool | 否 | 是否升序排序，默认为true |
| max_count | int | 否 | 最大返回数量，默认为100 |

## 接口返回结果
```json
{
    "ret_code": 0,
    "ret_msg": "SUCCESS",
    "data": {
        "plate_code": "HK.BK1001",
        "plate_name": "恒生指数",
        "stock_list": [
            {
                "stock_code": "HK.00700",
                "stock_name": "腾讯控股",
                "weight": 0.1,
                "update_time": "2024-03-20 10:30:00"
            },
            {
                "stock_code": "HK.00941",
                "stock_name": "中国移动",
                "weight": 0.08,
                "update_time": "2024-03-20 10:30:00"
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
| 1004 | INVALID_SORTFIELD | 排序字段错误 |
| 1005 | INVALID_COUNT | 数量错误 |
| 1054 | GET_PLATE_STOCK_FAILED | 获取板块成分股失败 |

## 示例代码
```python
from futu import *

# 创建行情连接
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

# 获取板块成分股
ret, data = quote_ctx.get_plate_stock(
    plate_code="HK.BK1001",
    market="HK",
    sort_field="weight",
    asc=False,
    max_count=50
)
if ret == RET_OK:
    print('获取板块成分股成功')
    print(f"板块代码: {data['plate_code']}")
    print(f"板块名称: {data['plate_name']}")
    print("成分股列表:")
    for stock in data['stock_list']:
        print(f"股票代码: {stock['stock_code']}")
        print(f"股票名称: {stock['stock_name']}")
        print(f"权重: {stock['weight']}")
        print(f"更新时间: {stock['update_time']}")
        print("-------------------")
else:
    print('获取板块成分股失败:', data)

# 关闭连接
quote_ctx.close()
```

## 注意事项
1. 获取板块成分股前需要先建立行情连接
2. 板块代码需要按照指定格式填写
3. 市场代码必须是有效的市场代码
4. 排序字段必须是有效的字段
5. 需要注意处理异常情况，避免程序崩溃
6. 返回的数据包含板块信息和成分股列表，如：
   - 板块代码和名称
   - 成分股列表（包含股票代码、名称、权重等信息）
7. 这些信息对于了解板块构成和权重分布非常重要 