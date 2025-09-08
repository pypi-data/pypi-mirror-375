_M="{'defaultColumn': 'moving_averages'}"
_L="{'defaultColumn': 'oscillators'}"
_K="{'defaultColumn': 'performance'}"
_J="{'grouping': 'no_group'}"
_I="{'blockSize': 'volume|1W'}"
_H="{'blockColor': 'Perf.YTD'}"
_G="{'symbol': 'NASDAQ:NVDA'}"
_F='Example to display a technical indicator chart using TradingView'
_E='from spartaqube import Spartaqube as Spartaqube'
_D='code'
_C='sub_description'
_B='description'
_A='title'
import json
from django.conf import settings as conf_settings
def sparta_e47cb63856(type='realTimeStock'):B='Example to display a real time stock using TradingView';A=_E;C=_G;return[{_A:f"{type.capitalize()}",_B:B,_C:'',_D:f"""{A}
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  interactive=False,
  height=500
)
plot_example"""},{_A:f"{type.capitalize()} with custom symbol",_B:B,_C:'',_D:f"""{A}
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  options={C},
  interactive=False,
  height=500
)
plot_example"""}]
def sparta_edcd4cc274():B='Example to display a stock heatmap using TradingView';A=_E;type='stockHeatmap';C="{'dataSource': 'DAX'}";D=_H;E=_I;F=_J;return[{_A:f"{type.capitalize()}",_B:B,_C:'',_D:f"""{A}
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  interactive=False,
  height=500
)
plot_example"""},{_A:f"YTD performance heatmap",_B:B,_C:'',_D:f"""{A}
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  options={D},
  interactive=False,
  height=500
)
plot_example"""},{_A:f"{type.capitalize()} with custom heatmap size",_B:B,_C:'',_D:f"""{A}
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  options={E},
  interactive=False,
  height=500
)
plot_example"""},{_A:f"{type.capitalize()} with custom data source",_B:B,_C:'',_D:f"""{A}
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  options={C},
  interactive=False,
  height=500
)
plot_example"""},{_A:f"{type.capitalize()} without grouping by sectors",_B:'Example to display a stock heatmap using TradingView without grouping the stocks by sector',_C:'',_D:f"""{A}
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  options={F},
  interactive=False,
  height=500
)
plot_example"""}]
def sparta_b490b260e0():B='Example to display an economic calendar using TradingView';A=_E;type='economicCalendar';C="{'countryFilter': 'us,eu,il'}";return[{_A:f"Economic calendar",_B:B,_C:'',_D:f"""{A}
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'],
  interactive=False,
  height=500
)
plot_example"""},{_A:f"Economic calendar with custom countries",_B:B,_C:'',_D:f"""{A}
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  options={C},
  interactive=False,
  height=500
)
plot_example"""}]
def sparta_b67f503106():B='Example to display a etf heatmap using TradingView';A=_E;type='etfHeatmap';C="{'dataSource': 'AllCHEEtf'}";D=_H;E="{'blockSize': 'volume|1M'}";F=_J;return[{_A:f"{type.capitalize()}",_B:B,_C:'',_D:f"""{A}
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  interactive=False,
  height=500
)
plot_example"""},{_A:f"YTD performance heatmap",_B:B,_C:'',_D:f"""{A}
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  options={D},
  interactive=False,
  height=500
)
plot_example"""},{_A:f"{type.capitalize()} with custom heatmap size",_B:B,_C:'',_D:f"""{A}
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  options={E},
  interactive=False,
  height=500
)
plot_example"""},{_A:f"{type.capitalize()} with custom data source",_B:'Example to display etf heatmap using TradingView',_C:'',_D:f"""{A}
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  options={C},
  interactive=False,
  height=500
)
plot_example"""},{_A:f"{type.capitalize()} without grouping by sectors",_B:'Example to display etf heatmap using TradingView without grouping the stocks by sector',_C:'',_D:f"""{A}
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  options={F},
  interactive=False,
  height=500
)
plot_example"""}]
def sparta_333d5bb580():B='Example to display a crypto table using TradingView';A=_E;type='cryptoTable';C=_K;D=_L;E=_M;return[{_A:f"{type.capitalize()}",_B:B,_C:'',_D:f"""{A}
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  interactive=False,
  height=500
)
plot_example"""},{_A:f"{type.capitalize()} with performance data source",_B:B,_C:'',_D:f"""{A}
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  options={C},
  interactive=False,
  height=500
)
plot_example"""},{_A:f"{type.capitalize()} with oscillator data",_B:B,_C:'',_D:f"""{A}
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  options={D},
  interactive=False,
  height=500
)
plot_example"""},{_A:f"{type.capitalize()} with moving average data",_B:B,_C:'',_D:f"""{A}
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  options={E},
  interactive=False,
  height=500
)
plot_example"""}]
def sparta_a441b98535():B='Example to display a crypto heatmap using TradingView';A=_E;type='cryptoHeatmap';C=_H;D=_I;return[{_A:f"{type.capitalize()}",_B:B,_C:'',_D:f"""{A}
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  interactive=False,
  height=500
)
plot_example"""},{_A:f"YTD performance heatmap",_B:B,_C:'',_D:f"""{A}
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  options={C},
  interactive=False,
  height=500
)
plot_example"""},{_A:f"{type.capitalize()} with custom heatmap size",_B:B,_C:'',_D:f"""{A}
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  options={D},
  interactive=False,
  height=500
)
plot_example"""}]
def sparta_db55b1d9ff(type='forex'):B='Example to display a forex live table using TradingView';A=_E;C="{'currencies': ['USD', 'EUR', 'CHF', 'GBP', 'JPY']}";return[{_A:f"{type.capitalize()}",_B:B,_C:'',_D:f"""{A}
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  interactive=False,
  height=500
)
plot_example"""},{_A:f"{type.capitalize()} with custom currencies",_B:B,_C:'',_D:f"""{A}
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  options={C},
  interactive=False,
  height=500
)
plot_example"""}]
def sparta_d7bb74df17():B='Example to display a market data table using TradingView';A=_E;C='{\n        "symbolsGroups": [\n            {\n                "name": "Indices",\n                "originalName": "Indices",\n                "symbols": [\n                    {\n                        "name": "FOREXCOM:SPXUSD",\n                        "displayName": "S&P 500",\n                    },\n                    {\n                        "name": "FOREXCOM:NSXUSD",\n                        "displayName": "US 100",\n                    },\n                ],\n            },\n            {\n                "name": "Futures",\n                "originalName": "Futures",\n                "symbols": [\n                    {\n                        "name": "CME_MINI:ES1!",\n                        "displayName": "S&P 500",\n                    },\n                    {\n                        "name": "CME:6E1!",\n                        "displayName": "Euro",\n                    },\n                ],\n            },\n            {\n                "name": "Bonds",\n                "originalName": "Bonds",\n                "symbols": [\n                    {\n                        "name": "CBOT:ZB1!",\n                        "displayName": "T-Bond",\n                    },\n                    {\n                        "name": "CBOT:UB1!",\n                        "displayName": "Ultra T-Bond",\n                    },\n                ],\n            },\n            {\n                "name": "Forex",\n                "originalName": "Forex",\n                "symbols": [\n                    {\n                        "name": "FX:EURUSD",\n                        "displayName": "EUR to USD",\n                    },\n                    {\n                        "name": "FX:GBPUSD",\n                        "displayName": "GBP to USD",\n                    },\n                ],\n            },\n        ]\n    }';type='marketData';return[{_A:f"{type.capitalize()}",_B:B,_C:'',_D:f"""{A}
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  interactive=False,
  height=500
)
plot_example"""},{_A:f"{type.capitalize()} with custom data",_B:B,_C:'',_D:f"""{A}
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  options={C},
  interactive=False,
  height=500
)
plot_example"""}]
def sparta_b383e71a70():B='Example to display a screener table using TradingView';A=_E;A=_E;type='screener';C=_K;D=_L;E=_M;F="{'defaultScreen': 'top_gainers'}";G="{'market': 'switzerland'}";return[{_A:f"{type.capitalize()}",_B:B,_C:'',_D:f"""{A}
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  interactive=False,
  height=500
)
plot_example"""},{_A:f"{type.capitalize()} with performance data source",_B:B,_C:'',_D:f"""{A}
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  options={C},
  interactive=False,
  height=500
)
plot_example"""},{_A:f"{type.capitalize()} with oscillator data",_B:B,_C:'',_D:f"""{A}
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  options={D},
  interactive=False,
  height=500
)
plot_example"""},{_A:f"{type.capitalize()} with moving average data",_B:B,_C:'',_D:f"""{A}
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  options={E},
  interactive=False,
  height=500
)
plot_example"""},{_A:f"{type.capitalize()} for rising pairs",_B:B,_C:'',_D:f"""{A}
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  options={F},
  interactive=False,
  height=500
)
plot_example"""},{_A:f"{type.capitalize()} for custom market",_B:B,_C:'',_D:f"""{A}
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  options={G},
  interactive=False,
  height=500
)
plot_example"""}]
def sparta_cf2b4acfab():A=_E;type='technicalAnalysis';B=_G;C="{'interval': '1h'}";return[{_A:f"{type.capitalize()}",_B:_F,_C:'',_D:f"""{A}
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  interactive=False,
  height=500
)
plot_example"""},{_A:f"{type.capitalize()} with custom symbol",_B:_F,_C:'',_D:f"""{A}
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  options={B},
  interactive=False,
  height=500
)
plot_example"""},{_A:f"{type.capitalize()} with custom interval (last hour)",_B:_F,_C:'',_D:f"""{A}
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  options={C},
  interactive=False,
  height=500
)
plot_example"""}]
def sparta_3c04e15ac6():A=_E;type='topStories';B=_G;C="{'feedMode': 'market', 'market': 'crypto'}";D="{'feedMode': 'market', 'market': 'stock'}";E="{'feedMode': 'market', 'market': 'index'}";return[{_A:f"{type.capitalize()} (all symbols)",_B:_F,_C:'',_D:f"""{A}
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  interactive=False,
  height=500
)
plot_example"""},{_A:f"{type.capitalize()} custom symbol",_B:_F,_C:'',_D:f"""{A}
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  options={B},
  interactive=False,
  height=500
)
plot_example"""},{_A:f"{type.capitalize()} for cryptocurrencies",_B:_F,_C:'',_D:f"""{A}
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  options={C},
  interactive=False,
  height=500
)
plot_example"""},{_A:f"{type.capitalize()} for stocks",_B:_F,_C:'',_D:f"""{A}
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  options={D},
  interactive=False,
  height=500
)
plot_example"""},{_A:f"{type.capitalize()} for indices",_B:_F,_C:'',_D:f"""{A}
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  options={E},
  interactive=False,
  height=500
)
plot_example"""}]
def sparta_9e163b47be():B='Example to display a symbol overview using TradingView';A=_E;type='symbolOverview';C=_G;return[{_A:f"{type.capitalize()}",_B:B,_C:'',_D:f"""{A}
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  interactive=False,
  height=500
)
plot_example"""},{_A:f"{type.capitalize()} with custom symbol",_B:B,_C:'',_D:f"""{A}
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  options={C},
  interactive=False,
  height=500
)
plot_example"""}]
def sparta_b853abedd5(type='tickerTape'):B='Example to display a ticker tape using TradingView';A=_E;C='{\n        "symbols": [\n            {\n                "proName": "FOREXCOM:SPXUSD",\n\t\t\t    "title": "S&P 500",\n            },\n            {\n                "proName": "FOREXCOM:NSXUSD",\n\t\t\t    "title": "US 100",\n            },\n        ]\n}';return[{_A:f"{type.capitalize()}",_B:B,_C:'',_D:f"""{A}
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  interactive=False,
  height=500
)
plot_example"""},{_A:f"{type.capitalize()} with custom symbols",_B:B,_C:'',_D:f"""{A}
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  options={C},
  interactive=False,
  height=500
)
plot_example"""}]
def sparta_6c889c0dcd():return sparta_b853abedd5('tickerWidget')