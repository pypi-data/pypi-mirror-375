# 逐笔成交推送接口文档

## 接口功能
用于接收订阅的股票实时逐笔成交数据推送，包括每笔成交的价格、数量、时间等信息。

## 接口模块
Quote API - 实时数据推送模块

## 接口参数
| 参数名 | 类型 | 说明 |
|--------|------|------|
| stock_code | string | 股票代码，格式为"市场.代码"，例如"HK.00700" |
| sequence | int | 成交序号 |
| price | float | 成交价格 |
| volume | int | 成交数量 |
| turnover | float | 成交金额 |
| ticker_direction | int | 成交方向，0-未知，1-买盘，2-卖盘 |
| ticker_type | int | 成交类型，0-未知，1-自动对盘，2-开市前成交盘，3-收市后成交盘 |
| timestamp | string | 成交时间 |
| ticker_status | int | 成交状态 |

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

class TickerHandler(TickerHandlerBase):
    def on_recv_rsp(self, rsp_str):
        ret_code, data = super(TickerHandler, self).on_recv_rsp(rsp_str)
        if ret_code != RET_OK:
            print("TickerHandler: error, msg: %s" % data)
            return RET_ERROR, data
        
        print("TickerHandler: ", data)
        return RET_OK, data

# 创建行情连接
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

# 设置回调
handler = TickerHandler()
quote_ctx.set_handler(handler)

# 订阅逐笔成交数据
quote_ctx.subscribe(['HK.00700'], [SubType.TICKER])

# 保持连接
while True:
    time.sleep(1)

# 关闭连接
quote_ctx.close()
```

## 注意事项
1. 此接口为回调接口，需要继承TickerHandlerBase类并实现on_recv_rsp方法
2. 在订阅逐笔成交数据前需要先设置回调处理器
3. 逐笔成交数据更新频率较高，建议在回调中及时处理数据
4. 需要注意处理异常情况，避免程序崩溃
5. 逐笔成交数据量大，建议根据实际需求选择订阅的股票 