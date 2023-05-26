import time

import pymysql

from sqlalchemy import create_engine

def str_quote(s):
    if s is None or isinstance(s, int) or isinstance(s, float):
        return s
    s = s.replace("\\'", "'")
    s = s.replace("'", "''")
    s = s.replace("\\", "\\\\")
    return s


class Database(object):
    is_sqllite = False
    def __init__(self, user=None, password=None, db=None, host='localhost', port=3306,
            charset='utf8', sqllite_path=None, recycle=300, size=50, timeout=20, interval=1):
        self.user = user
        self.pwd = password
        self.db = db
        self.host = host
        self.port = port
        self.charset = charset
        self.sqllite_path = sqllite_path
        self.recycle = recycle
        self.size = size
        self.timeout = timeout
        self.interval = interval

    def connect(self):
        connection = pymysql.connect(
                            host=self.host,
                            port=self.port,
                            user=self.user,
                            password=self.pwd,
                            db=self.db,
                            charset=self.charset,
                            cursorclass=pymysql.cursors.DictCursor)
        return connection

    def execute_sql_once(self, connection, sql):
        with connection.cursor() as cursor:
            cursor.execute(sql)
            result = cursor.fetchall()
            connection.commit()
            return result

    def execute_sql(self, sql):
        connection = self.connect()
        try:
            return self.execute_sql_once(connection, sql)
        finally:
            connection.close()

    def get_sql(self, parameters):
        if 'update' in parameters:
            sections = ['update']
            sections.append(parameters['update'])
            sections.append('set')
            s_sections = []
            k, v = '', ''
            if 'where' in parameters:
                k, _, v  = parameters['where'][0]
            for column, value in parameters['set'].items():
                # 此处似乎有bug 存在value = v的情况
                if column != k and value != v:
                    value = str_quote(value)
                    if value is None:
                        s_sections.append(f"`{column}`=null")
                    else:
                        s_sections.append(f"`{column}`='{value}'")
            if len(s_sections) > 1:
                s_sections = ', '.join(s_sections)
            else:
                s_sections = ''.join(s_sections)
            sections.append(s_sections)
        else:
            sections = ['select']
            if 'select' not in parameters:
                sections.append('*')
            else:
                sections.append(', '.join(parameters['select']))
            sections.append('from')
            sections.append(', '.join(parameters['from']))
        if 'join' in parameters:
            sections.append('t1 JOIN ( select id from')
            sections.append(', '.join(parameters['from']))
        if 'where' in parameters:
            sub_sections = []
            for item in parameters['where']:
                i = 0
                w_sections = []
                while i < len(item):
                    column, operator, value = item[i:i+3]
                    i += 3
                    if value == "":
                        break
                    if operator == 'equals':
                        if isinstance(value, str):
                            if not value.startswith(('t1.', 't2')):
                                value = "'".join(('', value, ''))
                        w_sections.append('='.join((column, value)))
                    elif operator == 'gte':
                        if isinstance(value, str):
                            value = "'".join(('', value, ''))
                        else:
                            value = str(value)
                        _s = ' >= '.join((column, value))
                        w_sections.append(_s)
                    elif operator == 'like':
                        _s = ' like '.join((column, '%'.join(("'", value, "'"))))
                        w_sections.append(_s)
                    elif operator == 'between':
                        if value[0] == "" or value[1] == "":
                            break
                        v1 = "'".join(('', value[0], ''))
                        v2 = "'".join(('', value[1], ''))
                        _s = ' between '.join((column, ' and '.join((v1, v2))))
                        w_sections.append(_s)
                    if i == 3:
                        w_sections[-1] = '(' + w_sections[-1]
                    if i == len(item):
                        w_sections[-1] = w_sections[-1] + ')'
                if len(w_sections) > 0:
                    sub_sections.append(' or '.join(w_sections))
            if len(sub_sections) > 0:
                sections.append('where')
                sections.append(' and '.join(sub_sections))
        if 'group_by' in parameters:
            sections.append('group by')
            sections.append(', '.join(parameters['group_by']))
        if 'order_by' in parameters:
            sections.append('order by')
            sen = ', '.join([' '.join(_o) for _o in parameters['order_by']])
            sections.append(sen)
        if 'limit' in parameters:
            sections.append('limit')
            sections.append(', '.join(parameters['limit']))
        if 'join' in parameters:
            sections.append(') t2 on t1.id=t2.id')
        sections.append(';')
        sql = ' '.join(sections)
        return sql

    def get_insert_sql(self, param, keys):
        sections = []
        if 'operator' not in param or param['operator'] == 'insert':
            sections.append('insert into')
        elif param['operator'] == 'ignore':
            sections.append('insert ignore into')
        elif param['operator'] == 'replace':
            sections.append('replace into')
        sections.append(param['table'])
        values = []
        datas = param['values']
        if not isinstance(datas, list):
            datas = [datas]
        for data in datas:
            vals = []
            for key in keys:
                try:
                    val = str_quote(data[key])
                except Exception as e:
                    print(data)
                    raise e
                if val is None:
                    vals.append("null")
                else:
                    vals.append("'{}'".format(val))
            values.append(','.join(vals).join(('(', ')')))
        sections.append('`, `'.join(keys).join(('(`', '`)')))
        sections.append('values')
        sections.append(','.join(values))
        sql = ' '.join(sections)
        return sql
    
    def not_warn(self):
        from warnings import filterwarnings
        filterwarnings('ignore',category=pymysql.Warning)


class Dbalchemy(Database):
    _engine = None

    @property
    def engine(self):
        if self._engine is None:
            if self.sqllite_path is not None:
                uri = 'sqlite+pysqlite:///%s' %self.sqllite_path
                self._engine = create_engine(uri)
                self.is_sqllite = True
            else:
                parma = 'mysql+pymysql://{}:{}@{}:{}/{}?charset={}'
                uri = parma.format(
                    self.user,
                    self.pwd,
                    self.host,
                    self.port,
                    self.db,
                    self.charset)
                self._engine = create_engine(
                    uri, 
                    pool_size=self.size,
                    pool_recycle=self.recycle)
        return self._engine
        
    def connect(self):
        for x in range(5):
            try:
                return self.engine.connect()
            except Exception as e:
                pass
        return self.engine.connect()

    def execute_sql_once(self, connection, sql):
        sql = sql.replace('%', '%%')
        endtime = time.time() + self.timeout
        while True:
            try:
                result = connection.execute(sql)
                if result.returns_rows:
                    return result.fetchall()
                else:
                    return None
            except Exception as e:
                if 'Lost connection to' in str(e) or 'MySQL server has gone away' in str(e):
                    print(f'与数据库失去连接，等待重试...')
                    time.sleep(self.interval)
                else:
                    raise e
            if time.time() > endtime:
                raise Exception('数据库连接超时')

    def execute_sql(self, sql):
        connection = self.connect()
        try:
            result = self.execute_sql_once(connection, sql)
        finally:
            connection.close()
        return result

