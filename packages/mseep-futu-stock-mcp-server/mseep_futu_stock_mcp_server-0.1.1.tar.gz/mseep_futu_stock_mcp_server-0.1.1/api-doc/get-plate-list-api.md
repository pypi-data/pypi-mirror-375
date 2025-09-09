# 获取板块列表接口文档

## 接口功能
用于获取指定市场的板块列表，包括行业板块、概念板块等。

## 接口模块
Quote API - 市场筛选模块

## 接口参数
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| market | string | 是 | 市场代码，例如"HK"、"US"等 |
| plate_type | string | 否 | 板块类型，可选值：INDUSTRY(行业)、CONCEPT(概念)、REGION(地区)，默认为空(获取所有类型) |
| sort_field | string | 否 | 排序字段，可选值：MARKET_CAP(市值)、STOCK_COUNT(股票数量)、TURNOVER_RATE(换手率)，默认为MARKET_CAP |
| sort_type | string | 否 | 排序类型，可选值：ASC(升序)、DESC(降序)，默认为DESC |
| page | int | 否 | 页码，从1开始，默认为1 |
| page_size | int | 否 | 每页数量，默认为20 |

## 接口返回结果
```json
{
    "ret_code": 0,
    "ret_msg": "SUCCESS",
    "data": {
        "total_count": 100,
        "page": 1,
        "page_size": 20,
        "plate_list": [
            {
                "plate_code": "HK.INDUSTRY.IT",
                "plate_name": "信息技术",
                "plate_type": "INDUSTRY",
                "market": "HK",
                "market_cap": 10000000000000,
                "stock_count": 100,
                "turnover_rate": 0.1,
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
| 1014 | INVALID_PLATETYPE | 板块类型错误 |
| 1010 | INVALID_SORTFIELD | 排序字段错误 |
| 1011 | INVALID_SORTTYPE | 排序类型错误 |
| 1012 | INVALID_PAGE | 页码错误 |
| 1013 | INVALID_PAGESIZE | 每页数量错误 |
| 1028 | GET_PLATE_LIST_FAILED | 获取板块列表失败 |

## 示例代码
```python
from futu import *

# 创建行情连接
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

# 获取板块列表
ret, data = quote_ctx.get_plate_list(
    market="HK",
    plate_type="INDUSTRY",
    sort_field="MARKET_CAP",
    sort_type="DESC",
    page=1,
    page_size=20
)
if ret == RET_OK:
    print('获取板块列表成功')
    print(f"总数量: {data['total_count']}")
    print(f"页码: {data['page']}")
    print(f"每页数量: {data['page_size']}")
    print("板块列表:")
    for plate in data['plate_list']:
        print(f"板块代码: {plate['plate_code']}")
        print(f"板块名称: {plate['plate_name']}")
        print(f"板块类型: {plate['plate_type']}")
        print(f"市场: {plate['market']}")
        print(f"市值: {plate['market_cap']}")
        print(f"股票数量: {plate['stock_count']}")
        print(f"换手率: {plate['turnover_rate']}")
        print(f"更新时间: {plate['update_time']}")
        print("-------------------")
else:
    print('获取板块列表失败:', data)

# 关闭连接
quote_ctx.close()
```

## 注意事项
1. 获取板块列表前需要先建立行情连接
2. 板块类型可以根据实际需求选择
3. 板块列表更新频率较低，建议缓存使用
4. 板块列表主要用于分析市场结构，建议结合其他指标一起使用
5. 需要注意处理异常情况，避免程序崩溃 