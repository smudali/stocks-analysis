from firestore_db import Firestore
from models import Submission, Number, TickerCIK

# Config path
CONFIG_PATH = 'config'

db = Firestore(config_path=CONFIG_PATH)

ticker_cik = TickerCIK(config_path=CONFIG_PATH)
sub = Submission(db=db, ticker_cik=ticker_cik)
num = Number(db=db)
