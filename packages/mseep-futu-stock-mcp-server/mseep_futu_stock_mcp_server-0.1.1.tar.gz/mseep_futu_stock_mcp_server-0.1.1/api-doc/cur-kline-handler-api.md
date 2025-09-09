# K线推送接口文档

## 接口功能
用于接收订阅的股票实时K线数据推送，包括不同周期的K线数据。

## 接口模块
Quote API - 实时数据推送模块

## 接口参数
| 参数名 | 类型 | 说明 |
|--------|------|------|
| stock_code | string | 股票代码，格式为"市场.代码"，例如"HK.00700" |
| kline_type | string | K线类型，可选值：<br>K_1M: 1分钟<br>K_5M: 5分钟<br>K_15M: 15分钟<br>K_30M: 30分钟<br>K_60M: 60分钟<br>K_DAY: 日K线<br>K_WEEK: 周K线<br>K_MON: 月K线<br>K_QUARTER: 季K线<br>K_YEAR: 年K线 |
| open_price | float | 开盘价 |
| high_price | float | 最高价 |
| low_price | float | 最低价 |
| close_price | float | 收盘价 |
| volume | int | 成交量 |
| turnover | float | 成交额 |
| pe_ratio | float | 市盈率 |
| turnover_rate | float | 换手率 |
| timestamp | string | 时间戳 |
| kline_status | int | K线状态 |

## 接口返回结果
无返回结果，此接口为回调接口，用于接收推送数据。

## 接口异常情况
| 错误码 | 错误信息 | 说明 |
|--------|----------|------|
| 2001 | PUSH_DATA_ERROR | 推送数据错误 |
| 2002 | PUSH_DATA_TIMEOUT | 推送数据超时 |

## 示例代码
```python
from futu import *

class CurKlineHandler(CurKlineHandlerBase):
    def on_recv_rsp(self, rsp_str):
        ret_code, data = super(CurKlineHandler, self).on_recv_rsp(rsp_str)
        if ret_code != RET_OK:
            print("CurKlineHandler: error, msg: %s" % data)
            return RET_ERROR, data
        
        print("CurKlineHandler: ", data)
        return RET_OK, data

# 创建行情连接
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

# 设置回调
handler = CurKlineHandler()
quote_ctx.set_handler(handler)

# 订阅K线数据
quote_ctx.subscribe(['HK.00700'], [SubType.K_1M])

# 保持连接
while True:
    time.sleep(1)

# 关闭连接
quote_ctx.close()
```

## 注意事项
1. 此接口为回调接口，需要继承CurKlineHandlerBase类并实现on_recv_rsp方法
2. 在订阅K线数据前需要先设置回调处理器
3. K线数据会实时更新，建议在回调中及时处理数据
4. 不同周期的K线数据更新频率不同，需要注意数据更新的时间间隔
5. 需要注意处理异常情况，避免程序崩溃 