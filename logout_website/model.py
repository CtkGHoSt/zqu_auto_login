from peewee import *
import datetime
import os

# db = SqliteDatabase(':memory:')
db_path = os.path.abspath('.')+'/logout.db'
db = SqliteDatabase(db_path)
db.connect()

class BaseModel(Model):
    """A base model that will use our Sqlite database."""
    class Meta:
        database = db

class logout_comment(BaseModel):
    userid = CharField(primary_key=True)
    token = CharField()
    gentime = DateTimeField(default=datetime.datetime.now())
    ip = CharField()

if __name__ == '__main__':
    db.create_tables([logout_comment])