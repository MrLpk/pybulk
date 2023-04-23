# PyBulk 🚀

PyBulk是一个Python模块，使用PyMySQL库实现了简单且快速的批量数据插入数据库功能。使用PyBulk，你可以使用几行代码将数千条记录插入数据库表中。

PyBulk基于PyMySQL库和连接池实现了高效地复用连接和最小化延迟。它处理所有的底层细节，可以执行多个INSERT语句，同时保护数据库不受过载。

PyBulk的一些主要特点包括：

* **简单API**：只需使用几个函数调用即可插入批量数据，无需复杂的设置。
* **速度**：利用PyMySQL的连接池快速插入数千条记录。
* **可靠性**：包括错误处理和重试机制，可以处理瞬时数据库错误。自动重试失败的查询。
* **支持REPLACE INTO**：支持更新已存在的记录或插入新记录。
* **兼容性**：可与MySQL、SQLite等使用SQL语句的数据库。

PyBulk让你可以专注于程序的逻辑本身，而不必花费时间构建处理数据库负载的基础设施。它是一个强大但轻量级的解决方案，非常适合批量写入大量数据的场景，比如爬虫、大数据开发等，相当好用。

## 💾 安装

PyBulk需要在Python3及以上版本中使用。可以通过以下命令安装：

```
pip install pybulk
```

## 🔧 使用示例:

连接数据库
在使用PyBulk之前，需要先连接到目标数据库。PyBulk支持MySQL和SQLite数据库。

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

# 创建db
db = pybulk.client(cfg)

# 创建SQLlite db
db = pybulk.client(sqllite_path="db_path")

```

写入数据
```
my_data = [
{'name': 'Peter', 'age': 21,},
{'name': 'Harry', 'age': 35,},
{'name': 'Mark', 'age': 40,},
]

db.push_data('student', my_data, size=2000)
```

更新数据
```
update=[{'name': 'name1', 'id':1}, {'name': 'name1', 'id':1}]
db.update_data('student', update, key='id')
```

REPLACE INTO
```
db.replace_data('student', my_data, size=2000)
```

清除数据

```
db.clean_table('student')
# 相当于TRUNCATE student
```

当然，你也可以自己写SQL进行执行
```
data = db.excute_sql('select * from school')
```
