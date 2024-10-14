import math

from . import base_db


class DBInterface(object):

    def __init__(self, db_setting=None, alchemy=True):
        if alchemy:
            self.db = base_db.Dbalchemy(**db_setting)
        else:
            self.db = base_db.Database(**db_setting)
            
    def push_data(self, storage_type, datas, size=200, keys=None):
        '''
        往指定表添加数据，遇到重复数据时忽略 
        param：storage_type，表名 
        param：datas，数据 
        '''  
        if len(datas) == 0:
            return
        if keys is None:
            keys = datas[0].keys()
        self.insert(storage_type, datas, operator='ignore', size=size, keys=keys) 
 
    def replace_data(self, storage_type, datas, size=200, keys=None): 
        ''' 
        往指定表添加数据，遇到重复数据时，删除原有数据后再插入 
        param：storage_type，表名 
        param：datas，数据 
        '''  
        if len(datas) == 0:
            return
        if keys is None:
            keys = datas[0].keys()
        self.insert(storage_type, datas, operator='replace', size=size, keys=keys) 
 
    def insert(self, storage_type, datas, operator, size, keys): 
        ''' 
        往指定表添加数据
        param：storage_type，表名
        param：datas，数据
        param：operator, 操作
        ''' 
        conn = self.db.connect()
        try:
            total = len(datas)
            if total % size == 0:
                max_pg = total // size
            else:
                max_pg = (total // size) + 1
            for pg in range(max_pg):
                start = pg * size
                end = (pg + 1) * size
                params = {
                    'operator': operator,
                    'table': storage_type,
                    'values': datas[start:end],
                }
                if self.db.is_sqllite:
                    params['operator'] = 'insert'
                sql = self.db.get_insert_sql(params, keys=keys)
                try:
                    self.db.execute_sql_once(conn, sql)
                except Exception as e:
                    print(sql[:2500])
                    raise e
        finally:
            conn.close()

    def update_same_val(self, table, vals, ids, key='id', size=1000):
        '''
        更新数据，当所有要更新的值都相同时才可以使用
        '''
        if len(ids) == 0:
            return
        conn = self.db.connect()
        try:
            sql = [f'update {table} set']
            _vals = []
            for k, v in vals.items():
                if type(v) is str:
                    _vals.append(f'{k}="{v}"')
                elif type(v) in (int, float):
                    _vals.append(f'{k}={v}')
                elif v is None:
                    _vals.append(f'{k}=null')
                else:
                    raise Exception(f'update_same_val val type error:{type(v)}')
            sql.append(','.join(_vals))
            for pg in range(math.ceil(len(ids)/size)):
                start, end = pg*size, (pg+1)*size
                if type(ids[0]) is str:
                    ids_txt = '","'.join(ids[start:end])
                    where_sql = f'where {key} in ("{ids_txt}")'
                elif type(ids[0]) in (int, float):
                    ids_txt = ','.join((str(x)for x in ids[start:end]))
                    where_sql = f'where {key} in ({ids_txt})'
                else:
                    raise Exception(f'update_same_val id type error:{ids[0]}')
                self.db.execute_sql_once(conn, ' '.join(sql + [where_sql]))
        finally:
            conn.close()

    def _update_data(self, storage_type, datas, key='id'):
        '''
        非事务方式更新数据，不适合大批量数据更新
        
        param：storage_type，表名
        param：datas，数据
        param：key，主键
        '''
        if len(datas) == 0:
            return
        conn = self.db.connect()
        try:
            for _data in datas:
                params = {
                    'update': storage_type,
                    'set': _data,
                    'where':[
                        (key, 'equals', str(_data[key])),
                    ],
                }
                sql = self.db.get_sql(params)
                try:
                    self.db.execute_sql_once(conn, sql)
                except Exception as e:
                    print(_data)
                    print(sql)
                    raise e
        finally:
            conn.close()
            
    def update_data(self, storage_type, datas, key='id', size=1000):
        '''
        批量更新数据，采用事务方式

        param：storage_type，表名
        param：datas，数据
        param：key，主键
        '''
        return self.batch_update(storage_type, datas, key)

    def batch_update(self, storage_type, datas, key='id', size=1000):
        '''
        批量更新数据，采用事务方式

        param：storage_type，表名
        param：datas，数据
        param：key，主键
        '''
        if len(datas) == 0:
            return
        for pg in range(0, len(datas), size):
            _datas = datas[pg:pg + size]
            if len(_datas) <= 20:
                self._update_data(storage_type, _datas, key)
            else:
                self._batch_update(storage_type, _datas, key)

    def _batch_update(self, storage_type, datas, key='id'):
        '''
        批量更新数据，采用事务方式

        param：storage_type，表名
        param：datas，数据
        param：key，主键
        '''
        if len(datas) == 0:
            return
        with self.db.engine.begin() as conn:
            for _data in datas:
                params = {
                    'update': storage_type,
                    'set': _data,
                    'where':[
                        (key, 'equals', str(_data[key])),
                    ],
                }
                sql = self.db.get_sql(params)
                try:
                    sql = sql.replace('%', '%%')
                    conn.execute(sql)
                except Exception as e:
                    print(sql)
                    raise e

    def execute_sql(self, sql):
        '''
        执行一次SQL
        param:sql,SQL语句
        '''
        return self.db.execute_sql(sql)

    def sign_length(self, storage_type, sign='sign'):
        '''
        获取指定表sign字段的数量
        param：storage_type，表名
        '''
        params = {
            'select': ['count(%s)' %sign],
            'from': [storage_type],
        }
        sql = self.db.get_sql(params)
        data = self.db.execute_sql(sql)
        return data[0][0]

    def get_signs_in_set(self, storage_type, sign='sign'):
        '''
        获取指定表所有sign字段内容
        param：storage_type，表名
        '''
        result = set()
        limit = 100000
        for pg in range(99999):
            sql = ' '.join((
                'select %s' %sign,
                'from %s' %storage_type,
                'order by id',
                'limit %d, %d' %(pg * limit, limit),
            ))
            datas = self.db.execute_sql(sql)
            if len(datas) == 0:
                break
            for data in datas:
                result.add(data[sign])
        return result

    def clean_table(self, table_name):
        self.execute_sql('TRUNCATE %s' %table_name)

    def rename(self, old_name, new_name):
        '''
        重命名
        '''
        sql = '\n'.join((
            'ALTER TABLE `%s`' %old_name,
            'RENAME TO `%s`;' %new_name,
        ))
        self.execute_sql(sql)

    def exist_table(self, table_name):
        '''
        检查表是否存在
        '''
        sql = f'show tables like "{table_name}"'
        return True if len(self.execute_sql(sql)) > 0 else False

    def get_column_names(self, table_name):
        '''
        获取数据表的所有字段名称
        '''
        sql = ' '.join((
            'select column_name from information_schema.columns',
            f'where table_name="{table_name}"',
        ))
        res = self.execute_sql(sql)
        try:
            return [x['column_name']for x in res]
        except Exception as e:
            return [x['COLUMN_NAME']for x in res]

    def get_same_keys(self, keys, table):
        '''
        将两份字段列表进行对比，找出相同的字段名称
        params:
            keys(list) 第一份字段名列表
            table(str) 数据表名称，用来确定目标表
        '''
        db_keys = self.get_column_names(table)
        return set(keys) & set(db_keys)

    def not_warn(self):
        '''
        pymysql不要进行警告
        '''
        self.db.not_warn()
        
    def all_tb_name(self, db_name):
        sql = ' '.join((
            'select table_name',
            'from information_schema.tables',
            f'where table_schema="{db_name}"'
        ))
        res = self.execute_sql(sql)
        return [x['table_name']for x in res]
    
    def close(self):
        pass

CLS_NAME = DBInterface
