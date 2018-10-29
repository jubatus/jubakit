# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from ..base import BaseLoader
from ..compat import *
from psycopg2 import connect
from psycopg2.extras import DictCursor
from psycopg2 import sql

class PostgreSQLoader(BaseLoader):
  """
  Loader to process columns of PostgreSQL.

  This loader that load data from PostgreSQL's table as below.
  We access the "test" table of the "test" database in the below example.

  Example:
    from jubakit.loader.postgresql import PostgreSQLoader
    from jubakit.loader.postgresql import PostgreSQLAuthHandler
    
    auth = PostgreSQLAuthHandler(dbname='test', user='postgres', password='postgres', host='localhost', port='5432')
    
    loader = PostgreSQLoader(auth, table='test')
    for row in loader:
      print(row)
    
    # {'id': 1, 'num': 100, 'data': 'abcdef'}
    # {'id': 2, 'num': 200, 'data': 'ghijkl'}
    # {'id': 3, 'num': 300, 'data': 'mnopqr'}
  """

  def __init__(self, auth, table, **kwargs):
    self.auth = auth
    self.table = table
    self.kwargs = kwargs

  def rows(self):
    with connect(self.auth.get()) as connection:
      with connection.cursor(cursor_factory=DictCursor) as cursor:
        cursor.execute(
          sql.SQL("SELECT * FROM {}")
          .format(sql.Identifier(self.table)))
        column_names = [column.name for column in cursor.description]

        for row in cursor:
          yield dict(zip(column_names, row))

class PostgreSQLAuthHandler(object):
  """
  Handles authentication required to access PostgreSQL.
  """

  def __init__(self, **kwargs):
    """
    Authentication information must be specified as follows:

    >>> PostgreSQLAuth(
    ...   user='XXXXXXXXXXXXXXXXXXXX',
    ...   password='XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
    ...   host='XXXXXXXX-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
    ...   port='XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
    ... )

    Any other connection parameter supported by this loader can be passed as a keyword.
    The complete list of the supported parameters are contained the PostgreSQL documentation.
    (https://www.postgresql.org/docs/current/static/libpq-connect.html#LIBPQ-PARAMKEYWORDS)
    """
    auth = ''
    auth_informations = (
      'host', 'hostaddr',
      'port',
      'dbname',
      'user',
      'password', 'passfile',
      'connect_timeout',
      'client_encoding',
      'options',
      'application_name',
      'fallback_application_name',
      'keepalives', 'keepalives_idle', 'keepalives_interval', 'keepalives_count',
      'tty',
      'sslmode', 'requiressl', 'sslcompression', 'sslcert', 'sslkey', 'sslrootcert', 'sslcrl',
      'requirepeer',
      'krbsrvname',
      'gsslib',
      'service',
      'target_session_attrs')
    for auth_key in auth_informations:
      if auth_key in kwargs:
        auth = auth + '%s=%s ' % (auth_key, kwargs[auth_key])
    self.auth = auth

  def get(self):
    return self.auth
