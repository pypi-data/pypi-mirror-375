class SqlException(Exception):
    pass


class SqlIntegryException(SqlException):
    pass


class DatabaseConnectionException(Exception):
    pass
