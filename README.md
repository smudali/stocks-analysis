# stocks-analysis
Stocks analysis using python packages

## Jupyter notebooks
### [yf_ta_part1](yf_ta_part1.ipynb)
This notebook plots the following stock charts:
1. Price and Volume charts
2. Price, SMA, and EMA charts
4. Price, SMA-50, and SMA-200 charts

_yf_ta_part1.properties_ under _config_ folder has the following parameters that you can configure to pass to the notebook:
- TICKER - Ticker symbol, e.g., MSFT, this must be a ticker symbol
- START - start date, e.g. 2021-01-01. This property needs to be adjusted for a ticker as some of them may not have older data
- TEMPLATE - template for display, it must be one of plotly's template types, e.g. plotly_dark, check [Theming and templates in Python](https://plotly.com/python/templates/) for other templates
- TICKERS  -  list of similar stocks to compare performance. You can also add an index such as Nasdaq 100 (^NDX) to the list


Stock Technical Analysis uses the following main packages:
- yfinance - reading stocks data
- TA Lib - Technical Analysis, e.g., SMA, EMA calculations
- plotly - plotting graphs
- jproperties - reading the property file
- pandas - date utilities

An example of a chart showing Price and Volume:![newplot (4)](https://github.com/smudali/stocks-analysis/assets/30547825/69aa318a-c6cf-4516-9060-17eb8522d749)

#### Medium Article
- [Plot Moving Averages using Python APIs](https://medium.com/@sugath.mudali/plot-moving-averages-using-python-apis-9a313b2b75ae)

## [yf_ta_part2](yf_ta_part2.ipynb)
This notebook plots the following stock charts:
1. Candlestick
2. RSI and Volume
3. Bollinger Bands
4. MACD

#### Medium Article
- [Plot Candlestick, RSI, Bollinger Bands, and MACD charts using yfinance Python API](https://medium.com/@sugath.mudali/plot-candlestick-rsi-bollinger-bands-and-macd-charts-using-yfinance-python-api-1c2cb182d147)

## [av_insert_earnings](av_insert_earnings.ipynb)
This notebook inserts Earnings data into MongoDB Atlas database

#### Medium Article
- [Company Earnings and Income Dashboards with MongoDB and Alpha Vantage API](https://medium.com/@sugath.mudali/company-earnings-and-income-dashboards-with-mongodb-and-alpha-vantage-api-8c03341f8d3c)

## [av_insert_income_statements](av_insert_income_statements.ipynb)
#### Medium Article
- [Company Earnings and Income Dashboards with MongoDB and Alpha Vantage API](https://medium.com/@sugath.mudali/company-earnings-and-income-dashboards-with-mongodb-and-alpha-vantage-api-8c03341f8d3c)

## [fh_analyst_trends](fh_analyst_trends.ipynb)
#### Medium Article
- [Plot Recommendation Trends from Finnhub using Plotly Library for Python](https://medium.com/@sugath.mudali/plot-recommendation-trends-from-finnhub-using-plotly-library-for-python-6487a9c9e4ec)

## [yf_wacc](ya_wacc.ipynb), [av_wacc](av_wacc.ipynb)
#### Medium Article
- [Calculate Weighted Average Cost of Capital (WACC) using Python APIs](https://medium.com/@sugath.mudali/calculate-weighted-average-cost-of-capital-wacc-using-python-apis-f5f06d257a9d)

## [yf_dcf](ya_dcf.ipynb), [yf_dcf_v2](ya_dcf_v2.ipynb), [av_dcf](av_dcf.ipynb)
#### Medium Article
- [How to Calculate Intrinsic Value of a Stock Using DCF model in Python](https://medium.com/@sugath.mudali/how-to-calculate-intrinsic-value-of-a-stock-using-dcf-model-in-python-4e99bf771b3b)

## [yf_stock_picker_p1](yf_stock_picker_p1.ipynb)
#### Medium Article
- [A Simple Stock Picking Strategy with 6 key Financial Metrics - Part 1](https://medium.com/@sugath.mudali/a-simple-stock-picking-strategy-with-6-key-financial-metrics-part-1-dab0effb80f8)

## [yf_stock_picker_p2](yf_stock_picker_p2.ipynb)
#### Medium Article
- [A Simple Stock Picking Strategy with 6 key Financial Metrics - Part 2](https://medium.com/@sugath.mudali/a-simple-stock-picking-strategy-with-6-key-financial-metrics-part-2-3c8086d2564c)

## [dividend_scanner](asx/dividend_scanner.ipynb)
#### Medium Article
- [Scan for ASX dividend stocks with 5 Key Financial Metrics](https://medium.com/@sugath.mudali/scan-for-asx-dividend-stocks-with-5-key-financial-metrics-d31e659555ca)

## [yf_dashboard](yf_dashboard.ipynb)
#### Medium Article
- [Creating a simple Stock Portfolio Dashboard in Python](https://medium.com/@sugath.mudali/creating-a-simple-stock-portfolio-dashboard-in-python-702187bbe0d6) 

## [yf_valuation](yf_valuation.ipynb)
#### Medium Article
- [Historical P/E Ratio as a Valuation Analysis Technique](https://medium.com/@sugath.mudali/historical-p-e-ratio-as-a-valuation-analysis-technique-e5f9326be833)

## [yf_stock_screener](yf_stock_screener.ipynb)
#### Medium Article
- [Fundamental Analysis for ranking Stocks with Python API](https://medium.com/@sugath.mudali/fundamental-analysis-for-ranking-stocks-with-python-api-0bf44cffd6da)

## [yf_piotroski_score](yf_piotroski_score.ipynb)
#### Medium Article
- [Piotroski Score to find value stocks with Python API](https://medium.com/@sugath.mudali/piotroski-score-to-find-value-stocks-with-python-api-18021f92e538)

## [sec_load_findata.ipynb](sec/sec_load_findata.ipynb)
#### Medium Article
- [Accessing company financials using the SEC Financial Statement Data Sets](https://medium.com/@sugath.mudali/accessing-company-financials-using-the-sec-financial-statement-data-sets-29de4770ce64)

## [sec_load_findata_p2.ipynb](sec/sec_load_findata_p2.ipynb)
#### Medium Article
- [Accessing company financials using the SEC Financial Statement Data Sets - Part 2 (Enhancements)](https://medium.com/@sugath.mudali/accessing-company-financials-using-the-sec-financial-statement-data-sets-part-2-enhancements-3d01894dfd97)

## [yf_altman_z-score.ipynb](yf_altman_z-score.ipynb)
#### Medium Article
- [How to calculate Altman Z-Score using yfinance Python API](https://medium.com/@sugath.mudali/how-to-calculate-altman-z-score-using-yfinance-python-api-c3b80e9e993d)
