import sqlite3

from squyrrel.db.connection import SqlDatabaseConnection


class SqliteInmemoryConnection(SqlDatabaseConnection):

    database_error_cls = sqlite3.Error
    integrity_error_cls = sqlite3.IntegrityError

    def connect(self, select_version=False, foreign_keys=True, **kwargs):
        self.c = sqlite3.connect(':memory:', **kwargs)
        if select_version:
            self.execute('SELECT sqlite_version();')
        if foreign_keys:
            self.execute('PRAGMA foreign_keys = ON;')
