import pyodbc
import pymssql
from logger_mod import Logger
import ConfigParser

class DAO(object):
   def __init__(self, connstring):
       self.connstring = connstring

   def execute_query(self, query):
       """
       Run the sql server query
       :param query: query
       :return: output - tuple
       """
       rows = []
       cnxn = None
       try:
           cnxn = pyodbc.connect(self.connstring, autocommit=True, timeout=60)
           cursor = cnxn.cursor()
           Logger.logger.debug("Running query: {0}".format(query))
           cursor.execute(query)
           rows = cursor.fetchall()
           # Logger.logger.debug(rows)
       except Exception as e:
           Logger.logger.error("Query: {0}".format(query))
           Logger.logger.error(e)
       finally:
           if cnxn:
               Logger.logger.debug("Connection being closed.")
               cnxn.close()
       return rows

   #  This command is used for Insert, Update and Delete operations which returns row count
   def execute_non_query(self, query):
       """
       Run the stored procedures.
       :param query: query
       :return: status of execution
       """
       rows = 0
       cnxn = None
       try:
           if query:
               cnxn = pyodbc.connect(self.connstring, autocommit=True, timeout=60)
               cursor = cnxn.cursor()
               cursor.execute(query)
               rows = cursor.rowcount
               Logger.logger.debug("Running query: {0}".format(query))
               Logger.logger.debug(rows)
           else:
               pass
               Logger.logger.error("Please input query")
       except Exception as e:
           Logger.logger.error(e)
       finally:
           if cnxn:
               cnxn.close()

       return rows

   def execute_callproc_query(self, query):
       """
       Run the stored procedure and get he output of execution
       :param query: query
       :return: result of execution
       """
       db_attr = dict()
       result = []
       cnxn = None
       temp = self.connstring.split(";")
       for t in temp:
           attr = t.split("=")
           db_attr[attr[0]] = attr[1]

       try:
           if db_attr['sp']:
               with pymssql.connect(db_attr['SERVER'], db_attr['UID'], db_attr['PWD'], db_attr['DATABASE']) as conn:
                  with conn.cursor(as_dict=True) as cursor:
                      cursor.execute("use {0}".format(db_attr['DATABASE']))
                      cursor.callproc(query)
                      for row in cursor:
                          result.append(row)
                      Logger.logger.debug("Running sp call: {0}".format(query))
                      Logger.logger.debug(result)
           else:
               Logger.logger.error("Please input stored procedure.")
       except Exception as e:
           Logger.logger.error(e)
       finally:
           if cnxn:
              cnxn.close()

       return result

if __name__ == "__main__":
    config = ConfigParser.ConfigParser()
    config.read('config.ini')
    conn_string = ";".join([ele + "=" + config.get("MSSQL_DB_CONFIG_QA", ele.lower()) for ele in ["DRIVER", "SERVER", "DATABASE", "UID", "PWD"]])
    d = DAO(conn_string)
    print d.execute_query("select top 10 * from EventInteraction")