# stocks-analysis
Stocks analysis using python packages

## Jupyter notebooks
### yf_ta_part1
This notebook plots the following stock charts:
1. CandleStick chart
2. Price and Volume charts
3. Price, SMA and EMA charts
4. Price, SMA-50 and SMA-200 charts

_yf_ta_part1.properties_ under _config_ folder has the following parameters that you can configure to pass to the notebook:
- TICKER - Ticker symbol, e.g., MSFT, this must be a ticker symbol
- START - start date, e.g. 2021-01-01. This property needs to be adjusted for a ticker as some of them may not have older data
- TEMPLATE - template for diaplay, it must be one of plotly's template types, e.g. plotly_dark, check [Theming and templates in Python](https://plotly.com/python/templates/) for other templates


Stock Technical Analysis uses the following main packages:
- yfinance - reading stocks data
- TA Lib - Technical Analysis, e.g., SMA, EMA calculations
- plotly - plotting graphs
- jproperties - reading the property file
- pandas - date utilities

Here is an example for CandleStick chart:   
![candlesticks](https://github.com/smudali/stocks-analysis/assets/30547825/7b1d56a9-063c-4faa-a588-d111ea9269c0)

And a chart showing Price and Volume:
![newplot (2)](https://github.com/smudali/stocks-analysis/assets/30547825/278d291d-5805-4bc5-b0e6-75653f68a396)
