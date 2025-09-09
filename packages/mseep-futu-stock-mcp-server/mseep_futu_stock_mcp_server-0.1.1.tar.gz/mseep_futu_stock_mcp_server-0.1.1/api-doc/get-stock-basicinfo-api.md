# 获取股票基本信息接口文档

## 接口功能
用于获取股票的基本信息，包括股票代码、名称、上市日期、所属行业、市值等静态信息。

## 接口模块
Quote API - 市场筛选模块

## 接口参数
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| stock_code | string | 是 | 股票代码，格式为"market.code"，例如"HK.00700" |
| market | string | 否 | 市场代码，例如"HK"、"US"等，如果不填则从stock_code中解析 |

## 接口返回结果
```json
{
    "ret_code": 0,
    "ret_msg": "SUCCESS",
    "data": {
        "stock_code": "HK.00700",
        "stock_name": "腾讯控股",
        "market": "HK",
        "stock_type": "STOCK",
        "stock_child_type": "MAIN_BOARD",
        "list_time": "2004-06-16",
        "delist_time": "",
        "lot_size": 100,
        "stock_owner": "腾讯控股有限公司",
        "issue_price": 3.7,
        "issue_size": 4200000000,
        "net_profit": 159000000000,
        "net_profit_growth": 0.36,
        "revenue": 560000000000,
        "revenue_growth": 0.1,
        "eps": 16.84,
        "pe_ratio": 20.5,
        "pb_ratio": 4.2,
        "dividend_ratio": 0.02,
        "stock_derivatives": [
            {
                "derivative_type": "OPTION",
                "derivative_code": "HK.00700C",
                "strike_price": 300,
                "expiry_date": "2024-12-20"
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
| 1003 | INVALID_STOCKCODE | 股票代码错误 |
| 1052 | GET_STOCK_BASICINFO_FAILED | 获取股票基本信息失败 |

## 示例代码
```python
from futu import *

# 创建行情连接
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

# 获取股票基本信息
ret, data = quote_ctx.get_stock_basicinfo(
    stock_code="HK.00700",
    market="HK"
)
if ret == RET_OK:
    print('获取股票基本信息成功')
    print(f"股票代码: {data['stock_code']}")
    print(f"股票名称: {data['stock_name']}")
    print(f"市场: {data['market']}")
    print(f"股票类型: {data['stock_type']}")
    print(f"上市日期: {data['list_time']}")
    print(f"每手股数: {data['lot_size']}")
    print(f"公司名称: {data['stock_owner']}")
    print(f"发行价: {data['issue_price']}")
    print(f"发行量: {data['issue_size']}")
    print(f"净利润: {data['net_profit']}")
    print(f"净利润增长率: {data['net_profit_growth']}")
    print(f"营业收入: {data['revenue']}")
    print(f"营业收入增长率: {data['revenue_growth']}")
    print(f"每股收益: {data['eps']}")
    print(f"市盈率: {data['pe_ratio']}")
    print(f"市净率: {data['pb_ratio']}")
    print(f"股息率: {data['dividend_ratio']}")
else:
    print('获取股票基本信息失败:', data)

# 关闭连接
quote_ctx.close()
```

## 注意事项
1. 获取股票基本信息前需要先建立行情连接
2. 股票代码需要按照指定格式填写
3. 市场代码必须是有效的市场代码
4. 需要注意处理异常情况，避免程序崩溃
5. 返回的数据包含股票的基本信息，如：
   - 股票代码和名称
   - 市场信息
   - 股票类型
   - 上市日期
   - 每手股数
   - 公司信息
   - 财务数据
   - 估值指标
   - 衍生品信息
6. 这些信息对于了解股票的基本情况非常重要 