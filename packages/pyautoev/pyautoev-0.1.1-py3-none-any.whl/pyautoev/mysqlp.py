# -*- coding: utf-8 -*-
from pymysql.cursors import DictCursor


class MysqlTools:
    def __init__(self, conn):
        self.conn = conn

    def connect(self):
        """
        Establish a database connection with DictCursor.

        :return: Cursor object
        """
        return self.conn.cursor(cursor=DictCursor)

    def close_connection(self):
        """
        Close the database connection.
        """
        self.conn.close()

    @staticmethod
    def _process_args(args):
        """
        Process input arguments to determine if they should be passed to SQL execution.

        :param args: Arguments passed to SQL method
        :return: Processed arguments or empty string
        """
        if args and args[0]:
            return args
        return ''

    def fetch_all(self, sql, *args):
        """
        Execute a query and return all results.

        :param sql: SQL query statement
        :param args: Parameters for SQL query (can be a single list/tuple)
        :return: List of records
        """
        args = self._process_args(args)
        cursor = self.connect()
        try:
            if args and isinstance(args[0], (list, tuple)):
                cursor.execute(sql, tuple(args[0]))  # 自动转换并拆包
            else:
                cursor.execute(sql, args or None)
            return cursor.fetchall()
        finally:
            cursor.close()

    def fetch_one(self, sql, *args):
        """
        Execute a query and return a single record.

        :param sql: SQL query statement
        :param args: Parameters for SQL query
        :return: Single record or None
        """
        args = self._process_args(args)
        cursor = self.connect()
        try:
            if args and isinstance(args[0], (list, tuple)):
                cursor.execute(sql, tuple(args[0]))
            else:
                cursor.execute(sql, args or None)
            return cursor.fetchone()
        finally:
            cursor.close()

    def execute_sql(self, sql, *args):
        """
        Execute an SQL statement (INSERT, UPDATE, DELETE).

        :param sql: SQL statement
        :param args: Parameters for SQL statement
        :return: Number of affected rows
        """
        args = self._process_args(args)
        cursor = self.connect()
        try:
            row_count = cursor.execute(sql, args or None)
            self.conn.commit()
            return row_count
        finally:
            cursor.close()

    def database_name(self):
        """
        Get the current database name.

        :return: Database name as string
        """
        return self.conn.db.decode('utf-8')
