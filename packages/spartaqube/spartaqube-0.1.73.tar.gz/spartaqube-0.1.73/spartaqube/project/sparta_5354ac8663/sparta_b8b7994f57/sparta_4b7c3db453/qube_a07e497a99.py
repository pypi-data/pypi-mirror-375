_F='Example to run a simple linear regression'
_E='code'
_D='sub_description'
_C='description'
_B='title'
_A='from spartaqube import Spartaqube as Spartaqube'
def sparta_043e1830d4():A=_A;type='STL';return[{_B:f"{type.capitalize()}",_C:_F,_D:'',_E:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")

# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='stl',
  x=apple_price_df.index,
  y=apple_price_df['Close'],
  title='Example',
  height=500
)
plot_example"""}]
def sparta_471a8cb5f1():A=_A;type='Wavelet';return[{_B:f"{type.capitalize()}",_C:_F,_D:'',_E:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")

# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='wavelet',
  x=apple_price_df.index,
  y=apple_price_df['Close'],
  title='Example',
  height=500
)
plot_example"""}]
def sparta_f5b3f408d0():A=_A;type='HMM';return[{_B:f"{type.capitalize()}",_C:_F,_D:'',_E:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")

# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='hmm',
  x=apple_price_df.index,
  y=apple_price_df['Close'],
  title='Example',
  height=500
)
plot_example"""}]
def sparta_8dafa0e303():A=_A;type='CUSUM';return[{_B:f"{type.capitalize()}",_C:_F,_D:'',_E:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")

# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='cusum',
  x=apple_price_df.index,
  y=apple_price_df['Close'],
  title='Example',
  height=500
)
plot_example"""}]
def sparta_dc36e52ece():A=_A;type='Ruptures';return[{_B:f"{type.capitalize()}",_C:_F,_D:'',_E:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")

# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='ruptures',
  x=apple_price_df.index,
  y=apple_price_df['Close'],
  title='Example',
  height=500
)
plot_example"""}]
def sparta_7caa7dd349():A=_A;type='Z-score';return[{_B:f"{type.capitalize()}",_C:_F,_D:'',_E:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")

# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='zscore',
  x=apple_price_df.index,
  y=apple_price_df['Close'],
  title='Example',
  height=500
)
plot_example"""}]
def sparta_4375cccda4():A=_A;type='Prophet Outlier';return[{_B:f"{type.capitalize()}",_C:_F,_D:'',_E:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")

# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='prophet_outlier',
  x=apple_price_df.index,
  y=apple_price_df['Close'],
  title='Example',
  height=500
)
plot_example"""}]
def sparta_5e17eebfa7():A=_A;type='Isolation Forest';return[{_B:f"{type.capitalize()}",_C:_F,_D:'',_E:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")

# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='isolation_forest',
  x=apple_price_df.index,
  y=apple_price_df['Close'],
  title='Example',
  height=500
)
plot_example"""}]
def sparta_2aac8a9f46():A=_A;type='MAD';return[{_B:f"{type.capitalize()}",_C:_F,_D:'',_E:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")

# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='mad',
  x=apple_price_df.index,
  y=apple_price_df['Close'],
  title='Example',
  height=500
)
plot_example"""}]
def sparta_1e88e19bb7():A=_A;type='SARIMA';return[{_B:f"{type.capitalize()}",_C:_F,_D:'',_E:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")

# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='sarima',
  x=apple_price_df.index,
  y=apple_price_df['Close'],
  title='Example',
  height=500
)
plot_example"""}]
def sparta_338f6767f0():A=_A;type='ETS';return[{_B:f"{type.capitalize()}",_C:_F,_D:'',_E:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")

# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='ets',
  x=apple_price_df.index,
  y=apple_price_df['Close'],
  title='Example',
  height=500
)
plot_example"""}]
def sparta_809444fece():A=_A;type='Prophet Forecast';return[{_B:f"{type.capitalize()}",_C:_F,_D:'',_E:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")

# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='prophet_forecast',
  x=apple_price_df.index,
  y=apple_price_df['Close'],
  title='Example',
  height=500
)
plot_example"""}]
def sparta_0a9bc99ced():A=_A;type='VAR';return[{_B:f"{type.capitalize()}",_C:_F,_D:'',_E:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
data_df = yf.Ticker(\"AAPL\").history(period=\"1y\")

# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='var',
  x=data_df.index,
  y=[data_df['Close'], data_df['Volume']],
  title='Example',
  height=500
)
plot_example"""}]
def sparta_7b28a7ce45():A=_A;type='ADF Test';return[{_B:f"{type.capitalize()}",_C:_F,_D:'',_E:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")

# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='adf_test',
  x=apple_price_df.index,
  y=apple_price_df['Close'],
  title='Example',
  height=500
)
plot_example"""}]
def sparta_6d8d2c98bc():A=_A;type='KPSS Test';return[{_B:f"{type.capitalize()}",_C:_F,_D:'',_E:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")

# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='kpss_test',
  x=apple_price_df.index,
  y=apple_price_df['Close'],
  title='Example',
  height=500
)
plot_example"""}]
def sparta_f9dc69ec0d():A=_A;type='Perron Test';return[{_B:f"{type.capitalize()}",_C:_F,_D:'',_E:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")

# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='perron_test',
  x=apple_price_df.index,
  y=apple_price_df['Close'],
  title='Example',
  height=500
)
plot_example"""}]
def sparta_7e2f851ba7():A=_A;type='Zivot-Andrews Test';return[{_B:f"{type.capitalize()}",_C:_F,_D:'',_E:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")

# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='zivot_andrews_test',
  x=apple_price_df.index,
  y=apple_price_df['Close'],
  title='Example',
  height=500
)
plot_example"""}]
def sparta_c85204cb1d():A=_A;type='Granger Test';return[{_B:f"{type.capitalize()}",_C:_F,_D:'',_E:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for SPX (ticker symbol: ^SPX)
spx_price_df = yf.Ticker(\"^SPX\").history(period=\"1y\")[['Close']]
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")[['Close']]
apple_price_df = apple_price_df.reindex(spx_price_df.index)
data_df = pd.concat([spx_price_df, apple_price_df], axis=1).pct_change().dropna()
data_df.columns = ['SPX', 'AAPL']

# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='granger_test',
  x=data_df['SPX'],
  y=data_df['AAPL'],
  title='Example',
  height=500
)
plot_example"""}]
def sparta_d5fe121175():A=_A;type='Cointegration Test';return[{_B:f"{type.capitalize()}",_C:_F,_D:'',_E:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for SPX (ticker symbol: ^SPX)
spx_price_df = yf.Ticker(\"^SPX\").history(period=\"1y\")[['Close']]
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")[['Close']]
apple_price_df = apple_price_df.reindex(spx_price_df.index)
data_df = pd.concat([spx_price_df, apple_price_df], axis=1).pct_change().dropna()
data_df.columns = ['SPX', 'AAPL']

# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='cointegration_test',
  x=data_df['SPX'],
  y=data_df['AAPL'],
  title='Example',
  height=500
)
plot_example"""}]
def sparta_dbbde63f9b():A=_A;type='Canonical Correlation';return[{_B:f"{type.capitalize()}",_C:_F,_D:'',_E:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
data_df = yf.Ticker(\"AAPL\").history(period=\"1y\")

# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='canonical_corr',
  x=[data_df['Close'], data_df['Open']],
  y=[data_df['High'], data_df['Volume']],
  title='Example',
  height=500
)
plot_example"""}]