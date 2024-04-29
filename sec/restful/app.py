from flask import Flask, jsonify, request

# For DataFrame
import pandas as pd

import datetime

# Import extensions and constanta
from extensions import sub, num, ticker_cik
from constants import SubConstants as SubConst, AppConfig

# ---------------------------------------------------------------------------------------
# Constants for Form 10-K and 10-Q
F10K = SubConst.F10K.value
F10Q = SubConst.F10Q.value

# Valid quarters
QTRS = SubConst.QTRS.value

# API version
API_VERSION = AppConfig.API_VERSION.value

# Initialize Flask App
app = Flask(__name__)
app.json.sort_keys = False

# --------------------------------------------------------------------------------------------------

def epoch_to_datetime(epoch:int, dt_fmt:bool=False) -> str:
    '''
    Return the formatted datetime string

    Parameters:
    epoch (int): epoch time
    dt_fmt (boolean): true if we need the epoch time in datetime format else only in date format
    '''
    if dt_fmt:
        return datetime.datetime.fromtimestamp(epoch/1000, tz=datetime.timezone.utc).strftime(
            '%Y-%m-%d %H:%M:%S')
    return datetime.datetime.fromtimestamp(epoch/1000, tz=datetime.timezone.utc).strftime('%Y-%m-%d')
# --------------------------------------------------------------------------------------------------

def create_df_from_docs(docs_list:list, year:int) -> pd.DataFrame:
    '''
    Returns a DF constructed from the a list of documents
    
    Parameters:
    docs_list (list): a list of documents to construct the DF
    year (int): the year to filter records
    
    Returns:
    pd.DataFrame: a DF created from a list of documents

    '''
    # Create a DF using the document list
    df = pd.DataFrame.from_records(docs_list)

    # We will filter all the records outside the year
    dt = datetime.datetime(year, 1, 1)
    # Start of the year - min
    start_ts = dt.replace(tzinfo=datetime.timezone.utc).timestamp() * 1000
    dt = datetime.datetime(year, 12, 31)
    # End of the year - max
    end_ts = dt.replace(tzinfo=datetime.timezone.utc).timestamp() * 1000

    # Only select records within start_ts and end_ts (inclusive)
    df_copy = df.query('(ddate >= @start_ts) and (ddate <= @end_ts)').copy()
    # Convert the date from epoch time
    df_copy['ddate'] = df_copy['ddate'].apply(epoch_to_datetime)
    return df_copy

def get_ticker(ticker:str) -> dict:
    '''
    Returns the CIK associate with the stock symbol
    
    Parameter:
    ticker (str): the ticker symbol for a stock
    
    Returns:
    dict: a dictionary containing attributes for given ticket symbol; none if not found
    '''
    cik = None
    try:
        cik = ticker_cik.get_cik(ticker=ticker)
    except KeyError:
        return None

    title = ticker_cik.get_title(ticker=ticker)    
    # Create a response dictionary
    item = {'id' : cik, 'type' : 'cik'}
    item['attributes'] = {'cik': cik, 'ticker': ticker, 'title': title}
    return item

# End of Helper (Local) Methods --------------------------------------------------------------------

# Start of Web Service Methods ---------------------------------------------------------------------
@app.route('/sec/tickers/', methods=['GET'])
def supported_tickers() -> str:
    args = request.args
    scope = args.get(key='scope')
    if scope is None:
        return jsonify({'error': f'Scope argument (?scope=Y) is missing'}), 404
    scope = scope.upper()

    if scope != 'Y':
        return jsonify({'error': f'Only Y/y is supported for the scope argument'}), 404

    # Create a response dictionary
    res_dict = {'apiVersion': API_VERSION,
                'data' : {'items': [], 'totalItems':2}}
    for ticker in AppConfig.SYMBOLS.value:
        item = get_ticker(ticker=ticker)
        # Add the self link
        item['links'] = {'self': f'/tickers/{ticker}'}
        if item:
            res_dict['data']['items'].append(item)
    return jsonify(res_dict)

@app.route('/sec/tickers/<string:ticker>/', methods=['GET'])
def ticker_by_symbol(ticker:str) -> str:
    '''
    Returns the CIK associate with the stock symbol
    
    Parameter:
    ticker (str): the ticker symbol for a stock
    
    Returns:
    str: CIK associated with given ticket symbol; error if ticker is not found
    '''
    # Create a response dictionary
    res_dict = {'apiVersion': API_VERSION, 'method': 'ticker.get', 'params': {'ticker': ticker}, 'data': {}}
    item = get_ticker(ticker=ticker)
    if item:
        res_dict['data'] = item
    return jsonify(res_dict)
# --------------------------------------------------------------------------------------------------

@app.route('/sec/subs/<string:adsh>/', methods=['GET'])
def subs_by_adsh(adsh:str) -> str:
    '''
    Returns a SUB for an adsh (accession number)
    
    Parameters:
    adsh (str): adsh number
    
    Returns:
    str: SUB associated with given adsh or error if not found

    '''
    doc_dict = sub.get(adsh=adsh)
    if len(doc_dict) == 0:
        # Return error if symbol is not found
        return jsonify({'error': f'Accession Number {adsh} not found'}), 404
    
    # Create a response dictionary
    res_dict = {'apiVersion': API_VERSION, 'method': 'subs.get', 'params': {'adsh': adsh}, 'data': {}}
    
    doc_dict['filed'] = epoch_to_datetime(epoch=doc_dict['filed'])
    doc_dict['period'] = epoch_to_datetime(epoch=doc_dict['period'])
    # Accepted needs datetime format
    doc_dict['accepted'] = epoch_to_datetime(epoch=doc_dict['accepted'], dt_fmt=True)

    item = {'id' : doc_dict.pop('id'), 'type' : 'subs'}
    item['attributes'] = doc_dict
    res_dict['data'] = item

    # Use the adsh for the self link
    res_dict['links'] = {'self': f"/subs/{doc_dict['adsh']}"}
    return jsonify(res_dict)
# --------------------------------------------------------------------------------------------------

@app.route('/sec/subs/', methods=['GET'])
def subs() -> str:
    '''
    Returns SBS(s) for given request parameters
        
    Request parameters:
    ticker (str): ticket symbol must exist in SYMBOLS constant
    year (str): SUB year or none to return all SUB(s)
    qtr (str): SUB for a quarter; qtr must be in the form QTRS constant; if specified, year must be specified
    
    Returns:
    str: json response for given parameters; error is returned for (a) if no SUB(s) found for the ticker (b) missing
    year with qtr
    '''
    args = request.args
    ticker = args.get(key='ticker')
    year = args.get(key='year', type=int)
    qtr = args.get(key='qtr')

    if qtr:
        if year:
            # qtr and year specified
            form = F10Q
        else:
            # qtr specified but year missing
            return jsonify({'error': f'Year missing with qtr'}), 404        
    else:
        # qtr not specified, assume 10_k
        form = F10K
    
    # Use the helper method to get an iterator for submissions
    docs_list = sub.find(ticker=ticker, year=year, form=form, qtr=qtr)

    if len(docs_list) == 0:
        # No SUBS found
        return jsonify({'error': f'No SUB found for Ticker {ticker} and for given inputs'}), 404

    # Create DF from a docs list
    df = pd.DataFrame.from_records(docs_list)
    df['filed'] = df['filed'].apply(epoch_to_datetime)
    df['period'] = df['period'].apply(epoch_to_datetime)
    # Accepted needs datetime format
    df['accepted'] = df['accepted'].apply(epoch_to_datetime, dt_fmt=True)

    # Create a response dictionary
    res_dict = {'apiVersion': API_VERSION, 'method' : 'subs.get', 'params': {'ticker': ticker},
                'data' : {'items': [], 'totalItems':len(df)}}
    
    if year:
        res_dict['params']['year'] = year

    if qtr:
        res_dict['params']['qtr'] = qtr
    
    for index, row in df.iterrows():
        row_dict = row.to_dict()
        item = {'id' : row_dict.pop('id'), 'type' : 'subs'}
        item['attributes'] = row_dict

        # Use the adsh for the self link
        item['links'] = {'self': f"/subs/{row_dict['adsh']}"}
        res_dict['data']['items'].append(item)

    return jsonify(res_dict)
# --------------------------------------------------------------------------------------------------

@app.route('/sec/nums/<string:id>')
def nums_by_id(id:str) -> str:
    '''
    Returns a NUM for given document id

    Parameters:
    id (str): document id to search
    
    Returns:
    str: NUM for given document id or error if not found
    
    '''
    doc_dict = num.get(id=id)
    if not doc_dict:
        return jsonify({'error': f'No NUM found for {id}'}), 404

    # Create a response dictionary
    res_dict = {'apiVersion': API_VERSION, 'method' : 'nums.get', 'params': {'id': id}, 'data' : {}}

    doc_dict['ddate'] = epoch_to_datetime(epoch=doc_dict['ddate'])
    item = {'id' : doc_dict.pop('id'), 'type' : 'nums'}
    item['attributes'] = doc_dict
    adsh = doc_dict.pop('adsh')
    item['relationships'] = {'SUB':{'data': {'type': 'subs', 'id':adsh}, 'links':{'self':f'/subs/{adsh}'}}}
    res_dict['data'] = item
    return jsonify(res_dict)

# --------------------------------------------------------------------------------------------------

@app.route('/sec/nums/')
def nums() -> str:
    '''
    Returns NUM details for a ticker, year, form and quarter passed as request parameters
    
    Request Parameters:
    ticker (str): ticket symbol must exist in SYMBOLS constant
    year (str): year for the tag name
    tag (str): optional tag name for a tag in a specific taxonomy release; can pass a partial identifier, e.g. Assets.
    qtr (str): optional qtr must be in the form QTRS constant
    
    Returns:
    str: json response for given parameters; error is returned for (a) if no sumbmissions found for ticker,
    (b) no tags found, and (c) invalid quarter passed
    '''
    args = request.args
    ticker = args.get(key='ticker')
    year = args.get(key='year', type=int)
    qtr = args.get(key='qtr')
    tag = args.get(key='tag')

    if qtr:
        qtr = qtr.upper()
        if qtr not in QTRS:
            return jsonify({'error': f'Invalid quarter, it must be one of {QTRS}'}), 404
        form = F10Q
    else:
        form = F10K

    # Get an iterator to submissions
    sub_list = sub.find(ticker=ticker, year=year, form=form, qtr=qtr)

    if len(sub_list) == 0:
        # No Submissions found
        return jsonify({'error': f'No SUBs found for Ticker {ticker}'}), 404
    
    # Get a list of submission adsh numbers
    sub_adsh = [item['adsh'] for item in sub_list]
    docs_list = num.find(adsh_list=sub_adsh, tag=tag)
    if len(docs_list) == 0:
        # No Numbers found
        return jsonify({'error': f'No tag values found for Ticker {ticker} and {tag} for given inputs'}), 404

    # Create DF from a docs list
    if year:
        df = create_df_from_docs(docs_list=docs_list, year=year)
    else:
        df = pd.DataFrame.from_records(docs_list)
        df['ddate'] = df['ddate'].apply(epoch_to_datetime)
    
    # Create a response dictionary
    res_dict = {'apiVersion': API_VERSION, 'method' : 'nums.get',
                'params': {'ticker': ticker, 'year': year,'form':form},
                'data' : {'items': [], 'totalItems':len(df)}}
    if qtr:
        res_dict['params']['qtr'] = qtr
    
    if tag:
        res_dict['params']['tag'] = tag

    for index, row in df.iterrows():
        row_dict = row.to_dict()
        doc_id = row_dict.pop('id')
        item = {'id' : doc_id, 'type' : 'nums'}
        item['attributes'] = row_dict
        item['links'] = {'self': f'/nums/{doc_id}'}
        adsh = row_dict.pop('adsh')
        item['relationships'] = {'SUB':{'data': {'type': 'subs', 'id':adsh}, 'links':{'self':f'/subs/{adsh}'}}}
        res_dict['data']['items'].append(item)
    return jsonify(res_dict)

# --------------------------------------------------------------------------------------------------

if __name__ == '__main__':
   app.run(port=5000, debug=True)