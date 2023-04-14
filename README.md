# pybulk
PyBulk is a Python module that wraps PyMySQL to allow simple and fast bulk data insertion into databases. With PyBulk, you can insert thousands of records into a database table in just a few lines of code.
PyBulk builds on top of the PyMySQL library and connection pool to efficiently reuse connections and minimize latency. It handles all the low-level details of executing multiple INSERT statements while protecting your database from overload.
Some of the main features of PyBulk include:
•Simple API: Insert bulk data with just a few function calls. No complicated setup required.
•Speed: Leverages PyMySQL's connection pool to quickly insert thousands of records.
•Safety: Limits the number of SQL queries executed at a time to protect your database from overload.
•Reliability: Includes error handling and recovery mechanisms to handle transient database errors. Retries failed queries automatically.
•Support for REPLACE INTO: Upsert support allows you to replace existing records in a table or insert new ones.
•Compatibility: Works with MySQL, MariaDB and AWS RDS. Compatible with Python 2 and 3.
PyBulk allows you to focus on your application's logic rather than spending time building infrastructure to handle database load. It is a robust but lightweight solution ideal for batch data processing applications.
