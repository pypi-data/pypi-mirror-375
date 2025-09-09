# 取消订阅接口文档

## 接口功能
用于取消已订阅的股票、期货、期权等金融产品的实时行情数据。

## 接口模块
Quote API - 实时数据订阅模块

## 接口参数
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| code | string | 是 | 股票代码，格式为"市场.代码"，例如"HK.00700" |
| subtype | string | 是 | 订阅类型，可选值：<br>- QUOTE: 报价<br>- ORDER_BOOK: 买卖盘<br>- TICKER: 逐笔成交<br>- K_1M: 1分钟K线<br>- K_5M: 5分钟K线<br>- K_15M: 15分钟K线<br>- K_30M: 30分钟K线<br>- K_60M: 60分钟K线<br>- K_DAY: 日K线<br>- K_WEEK: 周K线<br>- K_MON: 月K线<br>- K_QUARTER: 季K线<br>- K_YEAR: 年K线 |

## 接口返回结果
```json
{
    "ret_code": 0,
    "ret_msg": "SUCCESS",
    "data": {
        "unsub_list": [
            {
                "code": "HK.00700",
                "subtype": "QUOTE",
                "is_unsubscribed": true
            }
        ]
    }
}
```

## 接口异常情况
| 错误码 | 错误信息 | 说明 |
|--------|----------|------|
| 1001 | INVALID_PARAM | 参数错误 |
| 1002 | INVALID_CODE | 股票代码格式错误 |
| 1003 | INVALID_SUBTYPE | 订阅类型错误 |
| 1005 | UNSUBSCRIBE_FAILED | 取消订阅失败 |

## 示例代码
```python
from futu import *

# 创建行情连接
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

# 取消订阅股票行情
ret = quote_ctx.unsubscribe(['HK.00700'], [SubType.QUOTE])
if ret == RET_OK:
    print('取消订阅成功')
else:
    print('取消订阅失败:', ret)

# 关闭连接
quote_ctx.close()
```

## 注意事项
1. 取消订阅前需要先建立行情连接
2. 取消订阅后，将不再收到该股票对应类型的数据推送
3. 建议在不需要接收数据时及时取消订阅，以节省系统资源 