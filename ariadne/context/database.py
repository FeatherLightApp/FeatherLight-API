import os
import databases
import sqlalchemy
from helpers.mixins import LoggerMixin

class DBConnection(LoggerMixin):

    def __init__(self):
        self.db = databases.Database(os.environ.get('DB_HOST'))
        self.metadata = sqlalchemy.MetaData()
        self._username = os.environ.get('DB_USERNAME')
        self._password = os.environ.get('DB_PASSWORD')
        self.engine = None

    def create(self):
        self.logger.info('initializing SQL database')
        self.engine = sqlalchemy.create_engine(str(self.db.url))
        self.metadata.create_all(self.engine)