"""
Pybulk Library
~~~~~~~~~~~~~~~~~~~~~

Pybulk is a library help you to insert/update data to database more easiesly and more faster

Usage:

import pybulk

cfg = {
    'host': 'localhost',
    'port':  3306,
    'user':  'root',
    'password': 'root',
    'db': 'info',
    'charset': 'utf8',
}

db = pybulk.client(cfg)

my_data = [
    {'name': 'Peter', 'age': 21,},
    {'name': 'Harry', 'age': 35,},
    {'name': 'Mark', 'age': 40,},
]

db.push_data('student', my_data, size=2000)

You can also run sql in pybulk like:

data = db.excute_sql('select * from school')

"""
    

from .dbinterface import DBInterface

def client(cfg=None, alchemy=True):
    try:
        from settings import db_config
    except ModuleNotFoundError:
        db_config = None
    if cfg is None:
        cfg = db_config
    db = DBInterface(cfg, alchemy=alchemy)
    return db
