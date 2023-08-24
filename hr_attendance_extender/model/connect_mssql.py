# -*- coding: utf-8 -*-
import pyodbc
import textwrap

import logging

_logger = logging.getLogger(__name__)


def get_log(server, database, username, password, query_date):
    """" connect """
    try:
        connection = pyodbc.connect(
            'DRIVER={ODBC Driver 13 for SQL Server};SERVER=' + server + ';DATABASE='
            + database + ';UID=' + username + ';PWD=' + password)
        cursor = connection.cursor()
        sql = textwrap.dedent("""
    SELECT CONVERT(nVarchar(32), DATEADD(s,[nDateTime], '1970-01-01'), 20), [nUserID]
        FROM [BioStar].[dbo].[TB_EVENT_LOG] 
        WHERE nUserID >0 and CONVERT(nVarchar(32), DATEADD(s,[nDateTime], '1970-01-01'), 20) >= '%s' """) % query_date
        cursor.execute(sql)
        rows = cursor.fetchall()
        return rows
    except:
        error = str(pyodbc.ProgrammingError)
        _logger.info('MSSQL Error: %s' % error)
        return False
