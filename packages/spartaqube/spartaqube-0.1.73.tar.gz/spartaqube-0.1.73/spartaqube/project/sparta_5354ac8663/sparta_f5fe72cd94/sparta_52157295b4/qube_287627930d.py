import time
from project.sparta_5354ac8663.sparta_f5fe72cd94.qube_8046f903de import EngineBuilder
from project.logger_config import logger
class MariadbConnector(EngineBuilder):
	def __init__(A,host,port,user,password,database):super().__init__(host=host,port=port,user=user,password=password,database=database,engine_name='mysql');A.connector=A.connect_db()
	def connect_db(A):return A.build_mariadb()
	def test_connection(A):
		B=False
		try:
			if A.connector.is_connected():A.connector.close();return True
			else:return B
		except Exception as C:logger.debug(f"Error: {C}");return B