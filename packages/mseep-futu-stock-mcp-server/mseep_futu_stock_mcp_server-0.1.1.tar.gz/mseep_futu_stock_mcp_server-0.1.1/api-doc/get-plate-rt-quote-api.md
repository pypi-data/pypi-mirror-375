# 获取板块实时行情接口文档

## 接口功能
用于获取指定板块的实时行情数据，包括最新价、涨跌幅、成交量等信息。

## 接口模块
Quote API - 板块数据模块

## 接口参数
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| plate_code | string | 是 | 板块代码，例如"HK.BK1001" |
| market | string | 否 | 市场代码，例如"HK"、"US"等，如果不填则从plate_code中解析 |

## 接口返回结果
```json
{
    "ret_code": 0,
    "ret_msg": "SUCCESS",
    "data": {
        "plate_code": "HK.BK1001",
        "plate_name": "恒生指数",
        "last_price": 16700.0,
        "open_price": 16500.0,
        "high_price": 16800.0,
        "low_price": 16400.0,
        "prev_close_price": 16500.0,
        "volume": 1000000000,
        "turnover": 20000000000,
        "turnover_rate": 0.15,
        "amplitude": 0.0242,
        "change": 200.0,
        "change_ratio": 0.0121,
        "update_time": "2024-03-20 15:00:00",
        "status": "TRADING"
    }
}
```

## 接口异常情况
| 错误码 | 错误信息 | 说明 |
|--------|----------|------|
| 1001 | INVALID_PARAM | 参数错误 |
| 1002 | INVALID_MARKET | 市场代码错误 |
| 1003 | INVALID_PLATECODE | 板块代码错误 |
| 1058 | GET_PLATE_RT_QUOTE_FAILED | 获取板块实时行情失败 |

## 示例代码
```python
from futu import *

# 创建行情连接
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

# 获取板块实时行情
ret, data = quote_ctx.get_plate_rt_quote(
    plate_code="HK.BK1001",
    market="HK"
)
if ret == RET_OK:
    print('获取板块实时行情成功')
    print(f"板块代码: {data['plate_code']}")
    print(f"板块名称: {data['plate_name']}")
    print(f"最新价: {data['last_price']}")
    print(f"开盘价: {data['open_price']}")
    print(f"最高价: {data['high_price']}")
    print(f"最低价: {data['low_price']}")
    print(f"昨收价: {data['prev_close_price']}")
    print(f"成交量: {data['volume']}")
    print(f"成交额: {data['turnover']}")
    print(f"换手率: {data['turnover_rate']}")
    print(f"振幅: {data['amplitude']}")
    print(f"涨跌: {data['change']}")
    print(f"涨跌幅: {data['change_ratio']}")
    print(f"更新时间: {data['update_time']}")
    print(f"交易状态: {data['status']}")
else:
    print('获取板块实时行情失败:', data)

# 关闭连接
quote_ctx.close()
```

## 注意事项
1. 获取板块实时行情前需要先建立行情连接
2. 板块代码需要按照指定格式填写
3. 市场代码必须是有效的市场代码
4. 需要注意处理异常情况，避免程序崩溃
5. 返回的数据包含板块的实时行情信息，如：
   - 板块代码和名称
   - 价格信息（最新价、开盘价、最高价、最低价、昨收价）
   - 成交量信息（成交量、成交额、换手率）
   - 涨跌信息（涨跌、涨跌幅、振幅）
   - 更新时间
   - 交易状态
6. 这些信息对于实时监控板块走势和交易决策非常重要 