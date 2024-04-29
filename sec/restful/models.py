# For firebase access
from google.cloud.firestore_v1.base_query import FieldFilter
# For DataFrame
import pandas as pd
# To read company tickers file json files
import json
# To access datetime
import datetime
# To access local files
import os

from constants import SubConstants as SubConst, FirestoreConstants

# ---------------------------------------------------------------------------------------
# Read Limit
READ_LIMIT = FirestoreConstants.READ_LIMIT.value

# Constants for Form 10-K and 10-Q
F10K = SubConst.F10K.value
F10Q = SubConst.F10Q.value

# Valid quarters
QTRS = SubConst.QTRS.value

# --------------------------------------------------------------------------------------------------

class TickerCIK:
    def __init__(self, config_path) -> None:
        '''
        Returns a DataFrame consists of CIK, ticker symbols
        
        Returns:
        pd.DataFrame: a DataFrame consists of CIK, ticker symbols or None for any errors
        '''    
        # Specify the full path to load JSON data
        file_name = f"{os.path.join(config_path, 'company_tickers.json')}"

        # DF to return
        self.df = pd.DataFrame()    
        try:
            # Open the file in read mode
            with open(file_name, 'r') as file:
                # Use json.load() to parse the JSON data from the file
                self.df = pd.json_normalize(pd.json_normalize(json.load(file), max_level=0).to_numpy()[0])
                self.df.set_index('ticker',inplace=True)
        except FileNotFoundError:
            print(f"File '{file_name}' not found.")
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON data: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")

    def get_cik(self, ticker:str) -> int:
        '''
        Returns the CIK associated with given ticker or KeyError is thrown if not found

        Parameter:
        ticker(str): ticker symbol

        Returns:
        CIK associated with given ticker or KeyError if not found
        '''
        return int(self.df.loc[ticker.upper()]['cik_str'])

    def get_title(self, ticker:str) -> str:
        '''
        Returns the title associated with given ticker or KeyError is thrown if not found

        Parameter:
        ticker(str): ticker symbol

        Returns:
        Ttitle associated with given ticker or KeyError if not found
        '''
        return self.df.loc[ticker.upper()]['title']

class Submission:
    def __init__(self, db, ticker_cik):
        self.db = db
        self.ticker_cik = ticker_cik

    def get(self, adsh:str) -> dict:
        '''
        Returns the submissions for acession number
        
        Parameters:
        adsh (str): accession number
        
        Returns:
        dict: a dictiory for adsh or empty dict if adsh not found
        '''
        docs = self.db.get_sub_collection().where(
            filter=FieldFilter('adsh', '==', adsh)).get()

        for doc in docs:
            # Should be only 1 record; we can quit
            doc_dict = doc.to_dict()
            doc_dict['id'] = doc.id
            # Only one item; safe to return
            return doc_dict
        # Return an empty dictionary if symbol is not found
        return {}

    def find(self, ticker:str, form:str=F10K, year:int=None, qtr:str=None) -> list:
        '''
        Returns the submission(s) for a symbol and given parameters
        
        Parameters:
        ticker (str): ticket symbol
        form (str): either F10K or F10Q
        year (str): SUB year or none to return all SUB(s)
        qtr (str): SUB for a quarter; qtr must be in the form QTRS constant; if specified, year must be specified
        
        Returns:
        list: a list of SUB for given symbol and year (optional); empty list is
        returned if the given ticker symbol is not found
        '''
        # Check for null value for the ticker
        assert ticker is not None, 'Ticker must not be null'
        # Get the CIK for given symbol
        try:
            cik = self.ticker_cik.get_cik(ticker=ticker)
        except KeyError:
            # Return an empty dictionary if not found
            return {}

        # Set the form depends on the passed period; defaults to 10-K
        assert cik is not None, 'cik must not be null'
        # Must be form 10-K or 10-Q
        assert form in [F10K, F10Q], f'form must be either {F10K} or {F10Q}'

        if form == F10K:
            if year:
                docs = (
                    self.db.get_sub_collection().where(
                        filter=FieldFilter('cik', '==', cik)).where(
                            filter=FieldFilter('form', '==', F10K)).where(
                                filter=FieldFilter('fy', '==', year)).stream()
                )
            else:
                docs = (
                    self.db.get_sub_collection().where(
                        filter=FieldFilter('cik', '==', cik)).where(
                            filter=FieldFilter('form', '==', F10K)).stream()
                )
        else:
            # Form 10_Q
            assert year is not None, f'year is a must for for {F10Q}'
            assert qtr in QTRS, f'qtr is must be one of {QTRS}'

            docs = (
                self.db.get_sub_collection().where(
                    filter=FieldFilter('cik', '==', cik)).where(
                        filter=FieldFilter('form', '==', form)).where(
                            filter=FieldFilter('fy', '==', year)).where(
                                filter=FieldFilter('fp', '==', qtr)).stream()
            )
        # List of documents to process
        docs_list = []
        for doc in docs:
            doc_dict = doc.to_dict()
            # Add the doc id to the dictionary
            doc_dict['id'] = doc.id
            docs_list.append(doc_dict)

        return docs_list

class Number:
    def __init__(self, db):
        self.db = db

    def get(self, id:str) -> dict:
        '''
        Returns the number as a dictionary for a document id
        
        Parameters:
        id (str): document id
        
        Returns:
        dict: a dictionary for id or none if no number found for id
        '''
        doc = self.db.get_num_collection().document(id).get()
        doc_dict = doc.to_dict()
        if doc_dict:
            doc_dict['id'] = doc.id
        return doc_dict
    
    def find(self, adsh_list:list, tag:str=None) -> list:
        '''
        Returns NUM details for a list of adsh numbers and tag (if specified)
        
        Request Parameters:
        adsh_list (list): list of adsh numbers to search
        tag (str): optional tag name for a tag in a specific taxonomy release; can pass a partial identifier, e.g. Assets.
        
        Returns:
        list: a list of NUM records matching adsh numbers and tag (if specified); an empty list is returned if not found
        '''
        # Search for the tag if specified
        if tag:
            docs = (self.db.get_num_collection().where(
                filter=FieldFilter('adsh', 'in', adsh_list)).order_by('tag').start_at(
                    {'tag': tag}).end_at({'tag': f'{tag}\uf8ff'}).limit(READ_LIMIT).stream()
            )
        else:
            # Numbers filter on submission adsh
            docs = (self.db.get_num_collection().where(
                filter=FieldFilter('adsh', 'in', adsh_list)).limit(READ_LIMIT).stream()
            )
        # List of documents to process
        docs_list = []
        for doc in docs:
            doc_dict = doc.to_dict()
            # Add the doc id to the dictionary
            doc_dict['id'] = doc.id
            docs_list.append(doc_dict)
        return docs_list