import pybulk

cfg = {
    'port':  3306,
    'host': 'localhost',
    'user':  'user',
    'password': 'guest123***',
    'db': 'info',
    'charset': 'utf8mb4',
}
db = pybulk.client(cfg)

print(db.execute_sql('select * from ads limit 20'))