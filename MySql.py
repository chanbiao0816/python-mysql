# coding: utf-8
""" MySQL工具类 """
import pymysql
import os
import threading

OperationalError = pymysql.OperationalError

class MySQL(object):
    """ 保证是单例模式 """
    Lock = threading.Lock()
    error = ''
    __instance = None
    _isConnection = False
    _conn = None
    _cur = None

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            try:
                cls.Lock.acquire()
                # double check
                if not cls.__instance:
                    cls.__instance = object.__new__(cls)
            finally:
                cls.Lock.release()
        return cls.__instance

    def connect(self, host, user, password, database, port=3306,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor):
        """
        :func  connect      通过指定参数连接数据库
        :return:            连接状态                bool
        """
        try:
            self._conn = pymysql.connect(host=host, port=port, user=user, passwd=password, database=database,
                                        charset=charset, cursorclass=cursorclass)
            self._conn.autocommit(False)
            self._conn.set_charset(charset)
            self._cur = self._conn.cursor()
            self._isConnection = True
        except pymysql.Error as e:
            self.error = "Mysql connect error %d: %s" % (e.args[0], e.args[1])

        return self._isConnection

    def connect_from_file(self, fileName: str):
        """ 通过文件连接数据库 """
        if not os.path.exists(fileName) and fileName.endswith('.cnf'):
            self.error = '数据库文件错误'
            return False
        try:
            self._conn = pymysql.connect(read_default_file=fileName, charset='utf8mb4',
                                         cursorclass=pymysql.cursors.DictCursor)
            self._conn.autocommit(False)
            self._cur = self._conn.cursor()
            self._isConnection = True
        except pymysql.Error as e:
            self.error = "Mysql connect error " + str(e)
            return False

        return self._isConnection

    def get_state(self):
        """ 返回数据库连接状态 """
        return self._isConnection

    def query(self, table_name, field, condition=''):
        """
        :func   query   查询
        :param table_name:
        :param field:
        :param condition:
        :return:        查询状态    bool
        """
        if isinstance(field, list):
            field = ','.join(field)
        sql = ' '.join(['select ', field, 'from', table_name])
        if isinstance(condition, dict):
            condition = ' and '.join(['%s = "%s"' % (key, value) for key, value in condition.items()])
        sql = "".join([sql, " WHERE " + condition if condition else ''])

        return self.fetchAll() if self.execute(sql) else False

    def fetchRow(self):
        """
        :func   fetchRow    获取结果的一行数据
        :return:            结果                set
        """
        result = self._cur.fetchone()
        return result

    def fetchAll(self):
        """ 获取所有结果 """
        res = False
        if self._isConnection and self._cur:
            res = self._cur.fetchall()
        return res

    def isEmpty(self):
        """
        :func   isEmpty     结果是否为空
        :return:            结果状态      bool
        """
        return not bool(self.rowcount())

    def insert(self, table_name, data, condition=None, autocommit=True):
        """ 改进后，不需要为data的value添加引号
        :func   insert      数据库插入操作
        :param table_name:  数据库表名   str
        :param data:        插入数据    dict
        :param condition:   条件        待处理   FIXME
        :param autocommit:  自动提交    bool
        :return:            执行状态    bool
        """
        columns = [ele for ele in data.keys()]
        _prefix = "".join(['INSERT INTO ', table_name])
        _fields = ",".join(columns)
        _params = [str(data[key]) for key in columns]
        if len(_params) < 2:  # 修正list长度为1时，删掉转化成元祖多出来的逗号
            _params = '(' + str(_params[0]) + ')'
        else:
            _params = str(tuple(_params))
        _sql = "".join([_prefix, "(", _fields, ") VALUES ", _params])

        if not self.execute(_sql):
            return False

        return self.commit() if autocommit else True

    def replace(self, table_name, data, condition=None, autocommit=True):
        """ 插入操作，若存在，则替换
        :func   insert      数据库替换操作
        :param table_name:  数据库表名   str
        :param data:        插入数据    dict
        :param condition:   条件        待处理   FIXME
        :param autocommit:  自动提交    bool
        :return:            执行状态    bool
        """
        columns = [ele for ele in data.keys()]
        _prefix = "".join(['REPLACE INTO ', table_name])
        _fields = ",".join(columns)
        _params = [str(data[key]) for key in columns]
        if len(_params) < 2:  # 修正list长度为1时，删掉转化成元祖多出来的逗号
            _params = '(' + str(_params[0]) + ')'
        else:
            _params = str(tuple(_params))
        _sql = "".join([_prefix, "(", _fields, ") VALUES ", _params])

        if not self.execute(_sql):
            return False

        return self.commit() if autocommit else True

    def update(self, table_name, data, condition=None, autocommit=True):
        """ 改进后，不需要为data的value添加引号
        :func   update      更新数据库
        :param table_name:  数据库表名    str
        :param data:        新数据        dict
        :param condition:   条件          str or dict
        :param autocommit:  是否需要提交  bool
        :return:            执行状态      bool
        """
        _fields = []
        _prefix = "".join(['UPDATE ', table_name, ' SET '])
        for key in data.keys():
            if isinstance(key, str):
                _fields.append("%s = '%s'" % (key, data[key]))
            else:
                _fields.append("%s = %s" % (key, data[key]))

        if isinstance(condition, dict):
            condition = ' and '.join(['%s = "%s"' % (key, value) for key, value in condition.items()])

        _sql = "".join([_prefix, ','.join(_fields), " WHERE "+condition if condition else ''])

        if not self.execute(_sql):
            return False

        return self.commit() if autocommit else True

    def delete(self, table_name, condition, autocommit=True):
        """
        :func   delete         删除数据
        :param table_name:     数据库表名   str
        :param condition:      条件         str or dict
        :param autocommit:     自动提交     bool
        :return:               执行状态     bool
        """
        _prefix = "".join(['DELETE FROM ', table_name, ' WHERE '])
        if isinstance(condition, dict):
            condition = ' and '.join(['%s = "%s"' % (key, value) for key, value in condition.items()])
        _sql = "".join([_prefix, condition])
        if not self.execute(_sql):
            return False

        return self.commit() if autocommit else True

    def getLastInsertId(self):
        """
        :func       获取最后一次操作的ID
        :return:    数据的ID               int
        """
        return self._cur.lastrowid

    def rowcount(self):
        """
        :func   rowcount    操作数据的总行数
        :return:            总行数             int
        """
        return self._cur.rowcount

    def execute(self, sql):
        """
        :func   excute  执行操作
        :param sql:     sql语句     str
        :return:        执行状态    bool
        """
        if len(sql):
            try:
                self._cur.execute(sql)
            except Exception as e:
                self.error = "Mysql error:%s SQL:%s" % (e, sql)
                return False
        return True

    def excuteMany(self, table_name, fields, dataMatrix):
        """
        :func   excuteMany  插入多行数据
        :param table_name:  数据表名称   str
        :param fields:      列名称       list or str
        :param dataMatrix:  数据列表     list(内含list)
        :return:            执行状态     bool
        """
        if not dataMatrix:
            self.error = 'No data!!!'
            return False
        _prefix = "".join(['INSERT INTO ', table_name])
        if isinstance(fields, str):
            _fields = fields
        else:
            _fields = ",".join(fields)
        _positions = ",".join("%s" for i in range(len(dataMatrix[0])))
        _sql = "".join([_prefix, "(", _fields, ") VALUES (", _positions, ") "])
        try:
            self._cur.executemany(_sql, dataMatrix)
        except Exception as e:
            self.error = "Mysql query error:%s SQL:%s" % (e, _sql.format(dataMatrix))
            return False

        self.commit()
        return True

    def commit(self):
        """
        :func   commit  确认提交
        :return:        执行状态    bool
        """
        try:
            self._conn.commit()
            return True
        except Exception as e:
            self.error = "Commit fail: " + str(e)
            return False

    def rollback(self):
        """
        :func   rollback    撤销操作
        :return:            执行状态    bool
        """
        try:
            self._conn.rollback()
            return True
        except Exception as e:
            self.error = "Rollback fail: " + str(e)
            return False

    def close(self):
        """
        :func   close   关闭数据库
        :return:        执行状态    bool
        """
        # noinspection PyBroadException
        try:
            if self._isConnection:
                self._cur.close()
                self._conn.close()
                self._isConnection = False
            return True
        except Exception as e:
            return False
