# 获取股票筛选接口文档

## 接口功能
用于根据指定的条件筛选股票，包括市值、市盈率、市净率等条件。

## 接口模块
Quote API - 市场筛选模块

## 接口参数
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| market | string | 是 | 市场代码，例如"HK"、"US"等 |
| filter_conditions | dict | 是 | 筛选条件，格式如下：<br>{"market_cap": {"min": 1000000000, "max": 10000000000},<br>"pe_ratio": {"min": 0, "max": 20},<br>"pb_ratio": {"min": 0, "max": 5},<br>"ps_ratio": {"min": 0, "max": 10},<br>"dividend_ratio": {"min": 0, "max": 0.1},<br>"turnover_rate": {"min": 0, "max": 0.5}} |
| sort_field | string | 否 | 排序字段，可选值：MARKET_CAP(市值)、PE_RATIO(市盈率)、PB_RATIO(市净率)、PS_RATIO(市销率)、DIVIDEND_RATIO(股息率)、TURNOVER_RATE(换手率)，默认为MARKET_CAP |
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
        "stock_list": [
            {
                "code": "HK.00700",
                "name": "腾讯控股",
                "market": "HK",
                "market_cap": 1000000000000,
                "pe_ratio": 20.0,
                "pb_ratio": 5.0,
                "ps_ratio": 10.0,
                "dividend_ratio": 0.02,
                "turnover_rate": 0.1
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
| 1009 | INVALID_FILTERCONDITION | 筛选条件错误 |
| 1010 | INVALID_SORTFIELD | 排序字段错误 |
| 1011 | INVALID_SORTTYPE | 排序类型错误 |
| 1012 | INVALID_PAGE | 页码错误 |
| 1013 | INVALID_PAGESIZE | 每页数量错误 |
| 1026 | GET_STOCK_FILTER_FAILED | 获取股票筛选结果失败 |

## 示例代码
```python
from futu import *

# 创建行情连接
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

# 设置筛选条件
filter_conditions = {
    "market_cap": {"min": 1000000000, "max": 10000000000},
    "pe_ratio": {"min": 0, "max": 20},
    "pb_ratio": {"min": 0, "max": 5},
    "ps_ratio": {"min": 0, "max": 10},
    "dividend_ratio": {"min": 0, "max": 0.1},
    "turnover_rate": {"min": 0, "max": 0.5}
}

# 获取股票筛选结果
ret, data = quote_ctx.get_stock_filter(
    market="HK",
    filter_conditions=filter_conditions,
    sort_field="MARKET_CAP",
    sort_type="DESC",
    page=1,
    page_size=20
)
if ret == RET_OK:
    print('获取股票筛选结果成功')
    print(f"总数量: {data['total_count']}")
    print(f"页码: {data['page']}")
    print(f"每页数量: {data['page_size']}")
    print("股票列表:")
    for stock in data['stock_list']:
        print(f"股票代码: {stock['code']}")
        print(f"股票名称: {stock['name']}")
        print(f"市场: {stock['market']}")
        print(f"市值: {stock['market_cap']}")
        print(f"市盈率: {stock['pe_ratio']}")
        print(f"市净率: {stock['pb_ratio']}")
        print(f"市销率: {stock['ps_ratio']}")
        print(f"股息率: {stock['dividend_ratio']}")
        print(f"换手率: {stock['turnover_rate']}")
        print("-------------------")
else:
    print('获取股票筛选结果失败:', data)

# 关闭连接
quote_ctx.close()
```

## 注意事项
1. 获取股票筛选结果前需要先建立行情连接
2. 筛选条件可以根据实际需求灵活设置
3. 股票筛选结果更新频率较高，建议根据实际需求选择获取的股票
4. 股票筛选结果主要用于选股，建议结合其他指标一起使用
5. 需要注意处理异常情况，避免程序崩溃 