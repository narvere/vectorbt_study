import vectorbt as vbt
import datetime as dt
import pandas as pd
import numpy as np

end = dt.datetime.now()
start = end - dt.timedelta(days=5)

price = vbt.YFData.download(
    ["XMR-USD", "NEO-USD", "EOS-USD", "LTC-USD"],
    start=start,
    end=end,
    interval="1m",
    missing_index="drop").get("Close")


def custom_indicator(close, rsi_window=14, ma_window=50, entry=34, exit=84):
    close_5m = close.resample("5T").last()
    rsi = vbt.RSI.run(close=close_5m, window=rsi_window, short_name="rsi").rsi
    rsi, _ = rsi.align(close,
                       broadcast_axis=0,
                       method='ffill',
                       join='right')
    close = close.to_numpy()
    rsi = rsi.to_numpy()
    ma = vbt.MA.run(close=close, window=ma_window, short_name="ma").ma.to_numpy()
    trend = np.where(rsi > exit, -1, 0)
    trend = np.where((rsi < entry) & (close < ma), 1, trend)
    return trend


ind = vbt.IndicatorFactory(
    class_name="Combination",
    short_name="comb",
    input_names=["close"],
    param_names=["rsi_window", "ma_window", "entry", "exit"],
    output_names=["value"]
).from_apply_func(
    custom_indicator,
    rsi_window=14,
    ma_window=50,
    entry=34,
    exit=84,
    keep_pd=True)

result = ind.run(price,
                 rsi_window=np.arange(10, 40, step=3, dtype=int),
                 #ma_window=np.arange(10, 200, step=20, dtype=int),
                 entry=np.arange(10, 40, step=4, dtype=int),
                 # exit=np.arange(60, 85, step=4, dtype=int),
                 param_product=True)

# print(result.value.to_string())

entries = result.value == 1.0
exits = result.value == -1.0

pf = vbt.Portfolio.from_signals(price, entries, exits)

# print(pf.stats())
returns = pf.total_return()
returns = returns[returns.index.isin(["XMR-USD"], level="symbol")]
print(returns.to_string())
print(returns.max())
print(returns.idxmax())
#

fig = returns.vbt.heatmap(
    x_level="comb_rsi_window",
    y_level="comb_entry"
)
fig.show()
