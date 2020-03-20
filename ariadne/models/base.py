from context import DB
import orm

class BaseModel(orm.Model):
    __database__ = DB.db
    __metadata__ = DB.metadata
