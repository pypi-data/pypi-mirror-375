_F='Example to run a simple linear regression'
_E='code'
_D='sub_description'
_C='description'
_B='title'
_A='from spartaqube import Spartaqube as Spartaqube'
def sparta_fd8f337faa():A=_A;type='OLS';return[{_B:f"{type.capitalize()}",_C:_F,_D:'',_E:f"""{A}
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
  chart_type='OLS',
  x=data_df['SPX'],
  y=data_df['AAPL'],
  title='Example',
  height=500
)
plot_example"""}]
def sparta_67a66adc0d():A=_A;type='Polynomial Regression';return[{_B:f"{type.capitalize()}",_C:_F,_D:'',_E:f"""{A}
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
  chart_type='PolynomialRegression',
  x=data_df['SPX'],
  y=data_df['AAPL'],
  title='Example',
  height=500
)
plot_example"""}]
def sparta_a4f3333044():A=_A;type='Decision Tree Regression';return[{_B:f"{type.capitalize()}",_C:_F,_D:'',_E:f"""{A}
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
  chart_type='DecisionTreeRegression',
  x=data_df['SPX'],
  y=data_df['AAPL'],
  title='Example',
  height=500
)
plot_example"""}]
def sparta_38004f4984():A=_A;type='Random Forest Regression';return[{_B:f"{type.capitalize()}",_C:_F,_D:'',_E:f"""{A}
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
  chart_type='RandomForestRegression',
  x=data_df['SPX'],
  y=data_df['AAPL'],
  title='Example',
  height=500
)
plot_example"""}]
def sparta_1f5e2aa72c():A=_A;type='Clustering';return[{_B:f"{type.capitalize()}",_C:_F,_D:'',_E:f"""{A}
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
  chart_type='clustering',
  x=data_df['SPX'],
  y=data_df['AAPL'],
  title='Example',
  height=500
)
plot_example"""}]
def sparta_7f5339d211():A=_A;type='Correlation Network';return[{_B:f"{type.capitalize()}",_C:_F,_D:'',_E:f"""{A}
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
  chart_type='correlation_network',
  x=data_df['SPX'],
  y=data_df['AAPL'],
  title='Example',
  height=500
)
plot_example"""}]
def sparta_1ef5f1da46():A=_A;type='PCA';return[{_B:f"{type.capitalize()}",_C:_F,_D:'',_E:f"""{A}
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
  chart_type='pca',
  x=data_df['SPX'],
  y=data_df['AAPL'],
  title='Example',
  height=500
)
plot_example"""}]
def sparta_b1db67a90e():A=_A;type='TSNE';return[{_B:f"{type.capitalize()}",_C:_F,_D:'',_E:f"""{A}
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
  chart_type='tsne',
  x=data_df['SPX'],
  y=data_df['AAPL'],
  title='Example',
  height=500
)
plot_example"""}]
def sparta_465f82310a():A=_A;type='Features importance';return[{_B:f"{type.capitalize()}",_C:_F,_D:'',_E:f"""{A}
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
  chart_type='features_importance',
  x=data_df['SPX'],
  y=data_df['AAPL'],
  title='Example',
  height=500
)
plot_example"""}]
def sparta_0f0f5d5182():A=_A;type='Mutual Information';return[{_B:f"{type.capitalize()}",_C:_F,_D:'',_E:f"""{A}
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
  chart_type='mutual_information',
  x=data_df['SPX'],
  y=data_df['AAPL'],
  title='Example',
  height=500
)
plot_example"""}]
def sparta_7301ce4365():A=_A;type='Quantile Regression';return[{_B:f"{type.capitalize()}",_C:_F,_D:'',_E:f"""{A}
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
  chart_type='quantile_regression',
  x=data_df['SPX'],
  y=data_df['AAPL'],
  title='Example',
  height=500
)
plot_example"""}]
def sparta_bd8855ccc9():A=_A;type='Rolling Regression';return[{_B:f"{type.capitalize()}",_C:_F,_D:'',_E:f"""{A}
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
  chart_type='rolling_regression',
  x=data_df['SPX'],
  y=data_df['AAPL'],
  title='Example',
  height=500
)
plot_example"""}]
def sparta_286bbdfb05():A=_A;type='Recursive Regression';return[{_B:f"{type.capitalize()}",_C:_F,_D:'',_E:f"""{A}
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
  chart_type='recursive_regression',
  x=data_df['SPX'],
  y=data_df['AAPL'],
  title='Example',
  height=500
)
plot_example"""}]