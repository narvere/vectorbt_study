import vectorbt as vbt
import datetime as dt

end = dt.datetime.now()
start = end - dt.timedelta(days=365)

close = vbt.YFData.download(["XMR-USD"], start=start, end=end, missing_index="drop").get(
    "Close")

rsi = vbt.RSI.run(close=close, window=4, short_name="rsi")
entries = rsi.rsi_crossed_below(24)
exits = rsi.rsi_crossed_above(84)

pf = vbt.Portfolio.from_signals(close, entries, exits)

print(pf.stats())
pf.plot().show()
# print(pf.total_return().to_string())
