"""
Stock dashboard - initial version with 2 pages - Home with summmary and Earnings page
"""

import streamlit as st
from streamlit_autorefresh import st_autorefresh
import pandas as pd

# Read stocks
import yfinance as yf

# For plotting
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# To calculate TAs
import talib as ta

from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.sql import text

# End of imports ----------------------------------------------------

# Constants ---------------------------------------------------------

MARGIN = dict(l=0,r=10,b=10,t=25)
TICKERS = ['MSFT', 'AAPL', 'GOOG']

# End of Constants ---------------------------------------------------------

st.set_page_config(layout='wide', page_title='Stock Dashboard', page_icon=':dollar:')

# update every 5 mins
st_autorefresh(interval=5 * 60 * 1000, key="dataframerefresh")

# Store the DB in a session
db = 'sqlite:///db/stock_data.db'
engine = create_engine(db, echo=False)
st.session_state.engine = engine

def read_yf(yf_data, start_date):
    # print('Start date: {}'.format(start_date))
    df = pd.DataFrame()
    try:
        df = yf_data.history(start=start_date)[['Open', 'Close', 'Volume']]
    except Exception as e:
        print("The error is: ", e)
    if not df.empty:
        # Create a Date column
        df['Date'] = df.index.date
        # Drop the Date as index
        df.reset_index(drop=True, inplace=True)
        # Added extra columns
        df['Ticker'] = st.session_state.ticker
        df['Refreshed Date'] = datetime.now()
    return df

def full_history_load():
    with engine.connect() as conn:
        df = pd.read_sql('SELECT * FROM history WHERE Ticker=(:tk)',
                         params=dict(tk=st.session_state.ticker),
                         con=conn, parse_dates={"Date"})
        return df

def load_history_data(yf_data):
    """
    Loads hostory data
    :param yf_data: YF object to read history data
    :return history data as a DataFrame for the current ticker
    """
    # Any existing recrods in the DB for the ticker?
    with engine.connect() as conn:
        res = conn.execute(text('SELECT MAX(Date) FROM history WHERE Ticker = :tk'),
                           {'tk' : ticker}).fetchone()

    # print('Start date: {}'.format(res))
    # print(type(res))
    start_date = res[0]

    if start_date == None:
        # No history data found; set the start date to two years ago
        print('no history found; reading full 2 years of data')
        start_date = datetime.now() + pd.DateOffset(years=-2)
        # Read YF data
        df_full = read_yf(yf_data, start_date)
        if not df_full.empty:
            with engine.connect() as conn:
                # Save YF data to the sql table
                df_full.to_sql("history", conn, if_exists="append", index=False)
                
        # Load agin from the DB to ensure that dates are parsed correctly
        df = full_history_load()
        print('Size of df full is {}'.format(len(df)))
    else:
        # Found in the history; set the start to the latest date to get the delta
        print('Start date for delete is: {}'.format(start_date))
        # Read YF data stating from the latest date in the db
        df_delta = read_yf(yf_data, start_date)
        if not df_delta.empty:
            # We also need to delete the latest existing record as delta has the most recent info
            sql = '''
                DELETE FROM history WHERE Date=(:dt) AND Ticker=(:tk)
            '''
            with engine.connect() as conn:
                rc = conn.execute(text(sql), {'dt' : start_date, 'tk' : ticker}).rowcount
                # print("deleted {}".format(rc))
                conn.commit()

            with engine.connect() as conn:
                # Save the delta to the table
                df_delta.to_sql("history", conn, if_exists="append", index=False)

        # Check the history in the cache
        if "history" in st.session_state:
            # Cache copy exists but may not have records for the selected ticker
            df = st.session_state.history
            df = df[df.Ticker == st.session_state.ticker]
            if df.empty:
                print('Cache is empty, full load from the database')
                # Load from the DB as there are no existing records for the selected ticker
                df = full_history_load()
            else:
                print("Using the cache")
            # Remove the latest entry from the df
            df = df[:-1]

            # Read delta records from the DB; this will ensure that dates are parsed correctly
            sql = '''
                SELECT * FROM history WHERE Ticker = (:tk) AND Date = (:dt)
            '''
            with engine.connect() as conn:
                df_delta = pd.read_sql(text(sql), params=dict(tk=st.session_state.ticker, dt=start_date),
                                 con = conn, parse_dates={"Date"})

            print('Using delta records')

            # Concatenate the df in memory with delta df
            df = pd.concat([df, df_delta], axis=0)
            df.reset_index(drop=True, inplace=True)
        else:
            print('No cache found, full load from the database')
            df = full_history_load()

    # Calculate the MAs for graphs
    df['SMA-50'] = ta.SMA(df['Close'],timeperiod=50)
    df['SMA-200'] = ta.SMA(df['Close'], timeperiod =200)
    st.session_state.history = df

def date_breaks():
    # build complete timeline from start date to end date
    dt_all = pd.date_range(start=df.iloc[0]['Date'], end=df.iloc[-1]['Date'])
    # retrieve the dates that are in the original datset
    dt_obs = [d.strftime("%Y-%m-%d") for d in pd.to_datetime(df['Date'])]
    # define dates with missing values
    return [d for d in dt_all.strftime("%Y-%m-%d").tolist() if not d in dt_obs]

def format_number(number):
    """
    Formats a number to display in Trillion(T), Billion(B) or Million(M)
    :param number: input number
    :return formatted string
    """
    if abs(number) >= 1_000_000_000_000:
        return f"{number / 1_000_000_000_000:.2f}T"
    elif abs(number) >= 1_000_000_000:
        return f"{number / 1_000_000_000:.2f}B"
    elif abs(number) >= 1_000_000:
        return f"{number / 1_000_000:.2f}M"
    else:
        return str(number)
    
st.sidebar.header("Choose your filter: ")
ticker = st.sidebar.selectbox('Choose Ticker', options=TICKERS,
                              help = 'Select a ticker', key='ticker')
selected_range = st.sidebar.selectbox(
    'Select Period', options=['1m', '6m', 'YTD', '1y', 'all']
)

# YF object to read financial data
yf_data = yf.Ticker(ticker)

# Load the histori data into 'history' session object
load_history_data(yf_data)

df_history = st.session_state.history

min_date = df_history.iloc[0]['Date']
max_date = df_history.iloc[-1]['Date']

# print(max_date)
# print(min_date)

start_m1 = max_date + pd.DateOffset(months=-1)
start_m6 = max_date + pd.DateOffset(months=-6)
start_ytd = max_date.replace(month=1, day=1)
start_y1 = max_date + pd.DateOffset(months=-12)
start_all = min_date
end_date = max_date

match selected_range:
    case '1m':
        start_date = start_m1
    case '6m':
        start_date = start_m6
    case 'YTD':
        start_date = start_ytd
    case '1y' :
        start_date = start_y1
    case default:
        start_date = start_all

df = df_history[(df_history['Date'] >= start_date) & (df_history['Date'] <= end_date)]

# Subheader with company name and symbol
st.session_state.page_subheader = '{0} ({1})'.format(yf_data.info['shortName'], yf_data.info['symbol'])
st.subheader(st.session_state.page_subheader)
st.divider()

price_change = yf_data.info['currentPrice'] - yf_data.info['previousClose']
price_change_ratio = (abs(price_change) / yf_data.info['previousClose'] * 100)
price_change_direction = lambda i: ("+" if i > 0 else "-")

st.metric(label='Current', value=round(yf_data.info['currentPrice'], 2), delta="{:.2f} ({}{:.2f}%)".format(
    price_change, price_change_direction(price_change), price_change_ratio))
col1, col2, col3, col4, col5, col6 = st.columns([1,1,1,1,1,4.5])
with col1:
    st.text('Previous Close')
    st.text(yf_data.info['previousClose'])
    st.divider()
    st.text('EPS (TTM)')
    st.text(yf_data.info['trailingEps'])
    st.divider()
    st.text('Bid')
    st.text('{0:.2f} x {1}'.format(yf_data.info['bid'], yf_data.info['bidSize']))
    st.divider()
    st.text('Beta')
    st.text('{:.2f}'.format(yf_data.info['beta']))
with col2:
    st.text('Open')
    st.text(yf_data.info['open'])
    st.divider()
    st.text('Fwd Div & Yield')
    if 'dividendRate' in yf_data.info:
        st.text('{0} ({1:.2f})%'.format(yf_data.info['dividendRate'], yf_data.info['dividendYield'] * 100))
    else:
        st.text('NA')
    st.divider()
    st.text('Ask')
    st.text('{0:.2f} x {1}'.format(yf_data.info['ask'], yf_data.info['askSize']))
    st.divider()
    st.text('Market Cap')
    st.text(format_number(yf_data.info['marketCap']))
with col3:
    st.text('Day\'s Range')
    st.text('{0} - {1}'.format(yf_data.info['dayLow'], yf_data.info['dayHigh']))
    st.divider()
    st.text('PE Ratio (TTM)')
    st.text('{0:.2f}'.format(yf_data.info['trailingPE']))
    st.divider()
    st.text('Average Volume')
    st.text('{:,}'.format(yf_data.info['averageVolume']))
    st.divider()
    st.text('200-Day Average')
    st.text('{0:.2f}'.format(yf_data.info['twoHundredDayAverage']))
with col4:
    st.text('52-Week Range')
    st.text('{0:.2f} - {1:.2f}'.format(yf_data.info['fiftyTwoWeekLow'], yf_data.info['fiftyTwoWeekHigh']))
    st.divider()
    st.text('Volume')
    st.text('{:,}'.format(yf_data.info['volume']))
    st.divider()
    st.text('50-Day Average')
    st.text('{0:.2f}'.format(yf_data.info['fiftyDayAverage']))
with col6:
    # Construct a 2 x 1 Plotly figure for MA and Volume charts
    fig = make_subplots(rows=2, cols=1, vertical_spacing=0.01, shared_xaxes=True)
    # Remove dates without values
    fig.update_xaxes(rangebreaks=[dict(values=date_breaks())])

    # Plot the Price chart
    fig.add_trace(go.Scatter(x=df['Date'], y=df['Close'], name='Price', marker_color='#C39BD3'),
                    row=1, col=1)
    # Color maps for different MAs
    COLORS_MAPPER = {
        'SMA-50': '#38BEC9',
        'SMA-200': '#E67E22'
    }

    for ma, col in COLORS_MAPPER.items():
        fig.add_trace(go.Scatter(x=df['Date'], y=df[ma], name=ma, marker_color=col))

    # Colours for the Bar chart
    colors = ['#B03A2E' if row['Open'] - row['Close'] >= 0 
        else '#27AE60' for index, row in df.iterrows()]
    
    # Adds the volume as a bar chart
    fig.add_trace(go.Bar(x=df['Date'], y=df['Volume'], showlegend=False, marker_color=colors), row=2, col=1)
    # Adds the volume as a bar chart
    layout = go.Layout(title='Price, MA and Volume', height=500, margin=MARGIN)
    fig.update_layout(layout)
    st.plotly_chart(fig, theme='streamlit', use_container_width=True)