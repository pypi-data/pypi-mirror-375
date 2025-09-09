# 股票报价推送接口文档

## 接口功能
用于接收订阅的股票实时报价数据推送，包括最新价、涨跌幅、成交量等行情信息。

## 接口模块
Quote API - 实时数据推送模块

## 接口参数
| 参数名 | 类型 | 说明 |
|--------|------|------|
| stock_code | string | 股票代码，格式为"市场.代码"，例如"HK.00700" |
| last_price | float | 最新价 |
| open_price | float | 开盘价 |
| high_price | float | 最高价 |
| low_price | float | 最低价 |
| prev_close_price | float | 昨收价 |
| volume | int | 成交量 |
| turnover | float | 成交额 |
| turnover_rate | float | 换手率 |
| amplitude | float | 振幅 |
| dark_status | int | 暗盘状态 |
| list_time | string | 上市时间 |
| price_spread | float | 价差 |
| stock_owner | string | 股票所属人 |
| lot_size | int | 每手股数 |
| sec_status | int | 股票状态 |
| update_time | string | 更新时间 |

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

class StockQuoteHandler(StockQuoteHandlerBase):
    def on_recv_rsp(self, rsp_str):
        ret_code, data = super(StockQuoteHandler, self).on_recv_rsp(rsp_str)
        if ret_code != RET_OK:
            print("StockQuoteHandler: error, msg: %s" % data)
            return RET_ERROR, data
        
        print("StockQuoteHandler: ", data)
        return RET_OK, data

# 创建行情连接
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

# 设置回调
handler = StockQuoteHandler()
quote_ctx.set_handler(handler)

# 订阅股票行情
quote_ctx.subscribe(['HK.00700'], [SubType.QUOTE])

# 保持连接
while True:
    time.sleep(1)

# 关闭连接
quote_ctx.close()
```

## 注意事项
1. 此接口为回调接口，需要继承StockQuoteHandlerBase类并实现on_recv_rsp方法
2. 在订阅股票行情前需要先设置回调处理器
3. 推送数据会实时更新，建议在回调中及时处理数据
4. 需要注意处理异常情况，避免程序崩溃 