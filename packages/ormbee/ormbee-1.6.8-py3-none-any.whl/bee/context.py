# import sqlite3
# import pymysql
import threading

from bee.bee_enum import LocalType
from bee.config import HoneyConfig
from bee.conn_builder import ConnectionBuilder
from bee.factory import BeeFactory
from bee.osql.const import DatabaseConst, SysConst


class HoneyContext:
    '''
    Context for Bee framework.
    '''

    dbname = None

    @staticmethod
    def get_connection():
        '''
        get connection.
        '''

        factory = BeeFactory()
        conn = factory.get_connection()
        if conn:
            if HoneyContext.is_active_conn(conn):
                return conn

        config = HoneyConfig().get_db_config_dict()
        HoneyContext.__setDbName(config)
        conn = ConnectionBuilder.build_connect(config)
        factory.set_connection(conn)
        return conn

    @staticmethod
    def __setDbName(config):
        if SysConst.dbname in config:
            dbname = config.get(SysConst.dbname, None)
            if dbname:
                HoneyContext.dbname = dbname

    @staticmethod
    def get_placeholder():
        '''
        get placeholder for current database.
        '''

        dbname = HoneyConfig().get_dbname()

        if not dbname:
            return "?"
        elif dbname == DatabaseConst.MYSQL.lower() or dbname == DatabaseConst.PostgreSQL.lower():
            return "%s"
        elif dbname == DatabaseConst.SQLite.lower():
            return "?"
        elif dbname == DatabaseConst.ORACLE.lower():
            # query = "SELECT * FROM users WHERE username = :username AND age = :age"
            return ":"
        else:
            return HoneyConfig.sql_placeholder

    @staticmethod
    def is_active_conn(conn):
        '''
        check the connection whether is active.
        :param conn: connection
        :return: if connection is active return True, else return False.
        '''
        dbname = HoneyConfig().get_dbname()

        if dbname is None:
            return False
        elif dbname == DatabaseConst.MYSQL.lower():
            try:
                conn.ping(reconnect = True)
                return True
            except Exception:
                return False
        # elif dbname == DatabaseConst.SQLite.lower():
        #     try:
        #         # SQLite doesn't have a direct way to ping, but we can execute a simple query to check connectivity
        #         conn.execute('SELECT 1')
        #         return True
        #     except Exception:
        #         return False
        elif dbname == DatabaseConst.ORACLE.lower():
            try:
                # For Oracle, we can use the `ping` method if using cx_Oracle
                conn.ping()
                return True
            except Exception:
                return False
        # elif dbname == DatabaseConst.PostgreSQL.lower():
        #     try:
        #         # PostgreSQL can be checked with a simple query as well
        #         conn.execute('SELECT 1')
        #         return True
        #     except Exception:
        #         return False
        # # todo: support other DB

        return False

    # 使用单个通用的 thread-local 存储
    __local_data = threading.local()

    @staticmethod
    def _get_storage():
        """获取线程存储字典，如果不存在则初始化（静态方法）"""
        if not hasattr(HoneyContext.__local_data, 'storage'):
            HoneyContext.__local_data.storage = {}
        return HoneyContext.__local_data.storage

    @staticmethod
    def _set_data(local_type:LocalType, key = None, value = None):
        # 设置线程局部数据（静态方法）
        # :param local_type: DataType 枚举值，指定要存储的数据类型
        # :param key: 存储的key
        # :param value: 要存储的值

        storage = HoneyContext._get_storage()

        if not value or not key or not key.strip():
            return
        if local_type not in storage:
            storage[local_type] = {}

        storage[local_type][key] = value

    @staticmethod
    def get_data(local_type:LocalType, key = None):
        # 获取线程局部数据（静态方法）
        """
        Retrieve thread local data
        :param local_type: DataType enum.
        :param key: the key of data.
        :return: storage data or None
        """
        storage = HoneyContext._get_storage()

        if local_type not in storage or not key:
            return None
        return storage[local_type].get(key)

    @staticmethod
    def _remove_data(local_type:LocalType, key = None):
        # 移除线程局部数据（静态方法）
        # :param local_type: DataType 枚举值
        # :param key: 存储的key

        storage = HoneyContext._get_storage()

        if local_type in storage and key:
            storage[local_type].pop(key, None)

    @staticmethod
    def _remove_one_local_type(local_type:LocalType):
        storage = HoneyContext._get_storage()
        if local_type in storage:
            storage.pop(local_type, None)

    @staticmethod
    def isMySql():
        dbname = HoneyConfig().get_dbname()
        return dbname == DatabaseConst.MYSQL.lower()

    @staticmethod
    def isSQLite():
        dbname = HoneyConfig().get_dbname()
        return dbname == DatabaseConst.SQLite.lower()

    @staticmethod
    def isOracle():
        dbname = HoneyConfig().get_dbname()
        return dbname == DatabaseConst.ORACLE.lower()

    @staticmethod
    def get_dbname():
        '''
        get database name.
        '''
        return HoneyConfig().get_dbname()

