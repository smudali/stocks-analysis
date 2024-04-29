from enum import Enum

# Constants for Submissions
class SubConstants(Enum):
    F10K = '10-K'
    F10Q = '10-Q'
    QTRS = ['Q1', 'Q2', 'Q3', 'Q4']

# Enum for App Configuration Constants with functions
class AppConfig(Enum):
    CONFIG_PATH = 'config'
    API_VERSION = '0.1'
    # Symbols we are interested
    SYMBOLS = ['GOOG','NVDA','ADBE', 'MSFT','AMZN','TSLA','WMT']

class FirestoreConstants(Enum):
    READ_LIMIT = 100
