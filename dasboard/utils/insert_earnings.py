# Requests to AV
import requests

# DataFrame
import pandas as pd

# Access to sqlite DB
import sqlite3
import argparse

# To access home dir
import os

# ------------------------------------------------------------------------
# Constants

# Function to call at Av
FUNCTION = 'EARNINGS'

# Base URL for the AV end point
BASE_URL = 'https://www.alphavantage.co/query?'
DB = os.path.expanduser('~') + '/poc/dashboard/db/stock_data.db'

# List of fields we need to convert from string to float
FIELDS_TO_FLOAT = [
     'reportedEPS','estimatedEPS','surprise','surprisePercentage'
]
# ------------------------------------------------------------------------

"""
Calls AV endpoint for earnings for given ticker
:param ticker: ticker symbol
:param key: API key to access AV
:return: earnings as a Json response; includes both annual and quarterly earnings
"""
def get_income_statements(ticker, key):
    response = requests.get(f'{BASE_URL}function={FUNCTION}&symbol={ticker}&apikey={key}')
    return response.json()

"""
This method returns a DF earning which can be Annual or Quarterly
:param earnings: earnings in json format
:param report_type: either A (Annual) or Q (quarterly)
:return: earnings as a DataFrmae object
"""
def create_earnings_df(earnings, report_type):
    if report_type.upper() == 'Q':
        df_earnings = pd.DataFrame(earnings['quarterlyEarnings'])
        # Convert reported date which is only applicable to quarterly earnings from string
        df_earnings['reportedDate'] = pd.to_datetime(df_earnings['reportedDate'])
    
        for field in FIELDS_TO_FLOAT:
            # non numeric are converted to NaN
            df_earnings[field] = pd.to_numeric(df_earnings[field], errors='coerce')
    elif report_type.upper() == 'A':
        df_earnings = pd.DataFrame(earnings['annualEarnings'])
        # Only reportedEPS is present for Annual
        df_earnings['reportedEPS'] = pd.to_numeric(df_earnings['reportedEPS'], errors='coerce')
    else:
        raise Exception('Unknown report type, valid types are Q or A')

    # Convert to dates which are in strings in raw format
    df_earnings['fiscalDateEnding'] = pd.to_datetime(df_earnings['fiscalDateEnding'])

    return df_earnings

def delete_earnings(conn, table, ticker):
    """
    Delete an earnings by ticker
    :param conn:  Connection to the SQLite database
    :param table: name of DB table
    :param ticker: ticker symbol
    :return: none
    """
    sql = 'DELETE FROM ' + table + ' WHERE ticker=?'
    cur = conn.cursor()
    cur.execute(sql, (ticker,))
    conn.commit()

def main(args):
    ticker = args.ticker
    # Get the earnings data from AV
    earnings = get_income_statements(ticker, args.api)

    # DFs to collect all the annual and quarterly earnings for tickers
    df_annual = pd.DataFrame()
    df_quarterly = pd.DataFrame()

    df_annual = pd.concat([df_annual, create_earnings_df(earnings, 'A')])
    df_quarterly = pd.concat([df_quarterly, create_earnings_df(earnings, 'Q')])

    # Add ticker columns to both DFs
    df_annual['Ticker'] = ticker
    df_quarterly['Ticker'] = ticker

    # Rename columns to align with the sqlite columns
    df_annual.rename(columns={'fiscalDateEnding': 'Fiscal Date', 'reportedEPS': 'Reported EPS'}, inplace=True)
    df_quarterly.rename(columns={'fiscalDateEnding' : 'Fiscal Date', 'reportedDate' : 'Reported Date',
                             'reportedEPS' : 'Reported EPS',	'estimatedEPS' : 'Estimated EPS',
                             'surprise' : 'Surprise', 'surprisePercentage' : 'Surprise Percent'}, inplace=True)

    # print(df_annual.head())
    # create a database connection
    conn = conn = sqlite3.connect(DB)

    with conn:
        table = 'annual_earnings'
        # Delete all earnings for the ticker before inserting
        delete_earnings(conn, table, ticker)
        df_annual.to_sql(table, conn, if_exists='append', index=False)

        table = 'quarterly_earnings'
        delete_earnings(conn, table, ticker)
        df_quarterly.to_sql(table, conn, if_exists='append', index=False)
    
    print('Updated Earnings DB at {0}'.format(DB))

if __name__ == "__main__":
    # Initialize parser
    parser = argparse.ArgumentParser()

    # Adding optional argument
    parser.add_argument('--ticker', '-t', type=str, help='Ticker')
    parser.add_argument('--api', '-a', type=str, help='Alpha Vantage API Key')

    # Read arguments from command line
    args = parser.parse_args()
    main(args)
