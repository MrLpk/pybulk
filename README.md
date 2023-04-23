# PyBulk 🚀
[简体中文](README_CN.md) | English

PyBulk is a Python module that wraps PyMySQL to allow simple and fast bulk data insertion into databases. With PyBulk, you can insert thousands of records into a database table in just a few lines of code.

PyBulk builds on top of the PyMySQL library and connection pool to efficiently reuse connections and minimize latency. It handles all the low-level details of executing multiple INSERT statements while protecting your database from overload.

Some of the main features of PyBulk include:
* **Simple API**: Insert bulk data with just a few function calls. No complicated setup required.
* **Speed**: Leverages PyMySQL's connection pool to quickly insert thousands of records.
* **Reliability**: Includes error handling and recovery mechanisms to handle transient database errors. Retries failed queries automatically.
* **Support for REPLACE INTO**: Upsert support allows you to replace existing records in a table or insert new ones.
* **Compatibility**: Works with MySQL, MariaDB and AWS RDS. Compatible with Python 2 and 3.

PyBulk allows you to focus on your application's logic rather than spending time building infrastructure to handle database load. It is a robust but lightweight solution ideal for batch data processing applications. 
## 💾 Installation

```
pip install pybulk
```

## 🔧 Usage:
```
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

# You can also run sql in pybulk like:

data = db.excute_sql('select * from school')
```