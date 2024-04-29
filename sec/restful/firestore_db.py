import os

# For firebase access
import firebase_admin
from firebase_admin import credentials, firestore

class Firestore:
    def __init__(self, config_path):
        self.config_path = config_path
        self.connect()

    def connect(self):
        cred = credentials.Certificate(f"{os.path.join(self.config_path,'keys.json')}")
        default_app = firebase_admin.initialize_app(cred)
        self.db = firestore.client()

    def get_db(self):
        if not self.db:
            return self.connect()
        return self.db
    
    def get_sub_collection(self):
        return self.db.collection('sub')
        
    def get_num_collection(self):
        return self.db.collection('num')