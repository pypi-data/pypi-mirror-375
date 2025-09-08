_C='postgres'
_B='json_api'
_A=None
import time,json,pandas as pd
from pandas.api.extensions import no_default
import project.sparta_5354ac8663.sparta_f5fe72cd94.qube_0a0b1fb4d9 as qube_0a0b1fb4d9
from project.sparta_5354ac8663.sparta_f5fe72cd94.sparta_cbc4efd1ee.qube_95497896e8 import AerospikeConnector
from project.sparta_5354ac8663.sparta_f5fe72cd94.sparta_ea4914f5d3.qube_7195efb1fd import CassandraConnector
from project.sparta_5354ac8663.sparta_f5fe72cd94.sparta_711a2e5090.qube_4b7274073c import ClickhouseConnector
from project.sparta_5354ac8663.sparta_f5fe72cd94.sparta_b77cb71215.qube_0168cd15b3 import CouchdbConnector
from project.sparta_5354ac8663.sparta_f5fe72cd94.sparta_827b78df95.qube_3b046bcdd2 import CsvConnector
from project.sparta_5354ac8663.sparta_f5fe72cd94.sparta_962a94c412.qube_ca76b030d6 import DuckDBConnector
from project.sparta_5354ac8663.sparta_f5fe72cd94.sparta_99a42326ca.qube_a7c0b3a46e import JsonApiConnector
from project.sparta_5354ac8663.sparta_f5fe72cd94.sparta_a701f15d02.qube_211113824c import InfluxdbConnector
from project.sparta_5354ac8663.sparta_f5fe72cd94.sparta_52157295b4.qube_287627930d import MariadbConnector
from project.sparta_5354ac8663.sparta_f5fe72cd94.sparta_4871e47b35.qube_51d7a9b9f9 import MongoConnector
from project.sparta_5354ac8663.sparta_f5fe72cd94.sparta_ed029b0d6d.qube_db3a70558e import MssqlConnector
from project.sparta_5354ac8663.sparta_f5fe72cd94.sparta_bfa657be1d.qube_f90fd16343 import MysqlConnector
from project.sparta_5354ac8663.sparta_f5fe72cd94.sparta_064c61e546.qube_43bce05dfd import OracleConnector
from project.sparta_5354ac8663.sparta_f5fe72cd94.sparta_e51296d656.qube_af388e1da6 import ParquetConnector
from project.sparta_5354ac8663.sparta_f5fe72cd94.sparta_0853e62d69.qube_6e086b54aa import PostgresConnector
from project.sparta_5354ac8663.sparta_f5fe72cd94.sparta_ac52f8af37.qube_ad7a833e98 import PythonConnector
from project.sparta_5354ac8663.sparta_f5fe72cd94.sparta_955fd206ab.qube_384ebfb188 import QuestDBConnector
from project.sparta_5354ac8663.sparta_f5fe72cd94.sparta_976fab5e7f.qube_0a5c548583 import RedisConnector
from project.sparta_5354ac8663.sparta_f5fe72cd94.sparta_74b76bc1a8.qube_d5f6f3a668 import ScylladbConnector
from project.sparta_5354ac8663.sparta_f5fe72cd94.sparta_6f26ec2bf4.qube_4e169fdded import SqliteConnector
from project.sparta_5354ac8663.sparta_f5fe72cd94.sparta_88c2330bb9.qube_d39c190cd2 import WssConnector
from project.logger_config import logger
class Connector:
	def __init__(A,db_engine=_C):A.db_engine=db_engine
	def close_db(A):
		try:A.connector.close()
		except:pass
	def init_with_model(C,connector_obj):
		A=connector_obj;E=A.host;F=A.port;G=A.user;H=A.password_e
		try:B=qube_0a0b1fb4d9.sparta_3cd4c7f32a(H)
		except:B=_A
		try:
			if A.password is not _A:B=A.password
		except:pass
		I=A.database;J=A.oracle_service_name;K=A.keyspace;L=A.library_arctic;M=A.database_path;N=A.read_only;O=A.json_url;P=A.socket_url;Q=A.db_engine;R=A.csv_path;S=A.csv_delimiter;T=A.token;U=A.organization;V=A.lib_dir;W=A.driver;X=A.trusted_connection;D=[]
		if A.dynamic_inputs is not _A:
			try:D=json.loads(A.dynamic_inputs)
			except:pass
		Y=A.py_code_processing;C.db_engine=Q;C.init_with_params(host=E,port=F,user=G,password=B,database=I,oracle_service_name=J,csv_path=R,csv_delimiter=S,keyspace=K,library_arctic=L,database_path=M,read_only=N,json_url=O,socket_url=P,dynamic_inputs=D,py_code_processing=Y,token=T,organization=U,lib_dir=V,driver=W,trusted_connection=X)
	def init_with_params(A,host,port,user=_A,password=_A,database=_A,oracle_service_name='orcl',csv_path=_A,csv_delimiter=_A,keyspace=_A,library_arctic=_A,database_path=_A,read_only=False,json_url=_A,socket_url=_A,redis_db=0,token=_A,organization=_A,lib_dir=_A,driver=_A,trusted_connection=True,dynamic_inputs=_A,py_code_processing=_A):
		J=keyspace;I=py_code_processing;H=dynamic_inputs;G=database_path;F=database;E=password;D=user;C=port;B=host
		if A.db_engine=='aerospike':A.db_connector=AerospikeConnector(host=B,port=C,user=D,password=E,database=F)
		if A.db_engine=='cassandra':A.db_connector=CassandraConnector(host=B,port=C,user=D,password=E,keyspace=J)
		if A.db_engine=='clickhouse':A.db_connector=ClickhouseConnector(host=B,port=C,database=F,user=D,password=E)
		if A.db_engine=='couchdb':A.db_connector=CouchdbConnector(host=B,port=C,user=D,password=E)
		if A.db_engine=='csv':A.db_connector=CsvConnector(csv_path=csv_path,csv_delimiter=csv_delimiter)
		if A.db_engine=='duckdb':A.db_connector=DuckDBConnector(database_path=G,read_only=read_only)
		if A.db_engine=='influxdb':A.db_connector=InfluxdbConnector(host=B,port=C,token=token,organization=organization,bucket=F,user=D,password=E)
		if A.db_engine==_B:A.db_connector=JsonApiConnector(json_url=json_url,dynamic_inputs=H,py_code_processing=I)
		if A.db_engine=='mariadb':A.db_connector=MariadbConnector(host=B,port=C,user=D,password=E,database=F)
		if A.db_engine=='mongo':A.db_connector=MongoConnector(host=B,port=C,user=D,password=E,database=F)
		if A.db_engine=='mssql':A.db_connector=MssqlConnector(host=B,port=C,trusted_connection=trusted_connection,driver=driver,user=D,password=E,database=F)
		if A.db_engine=='mysql':A.db_connector=MysqlConnector(host=B,port=C,user=D,password=E,database=F)
		if A.db_engine=='oracle':A.db_connector=OracleConnector(host=B,port=C,user=D,password=E,database=F,lib_dir=lib_dir,oracle_service_name=oracle_service_name)
		if A.db_engine=='parquet':A.db_connector=ParquetConnector(database_path=G)
		if A.db_engine==_C:A.db_connector=PostgresConnector(host=B,port=C,user=D,password=E,database=F)
		if A.db_engine=='python':A.db_connector=PythonConnector(py_code_processing=I,dynamic_inputs=H)
		if A.db_engine=='questdb':A.db_connector=QuestDBConnector(host=B,port=C,user=D,password=E,database=F)
		if A.db_engine=='redis':A.db_connector=RedisConnector(host=B,port=C,user=D,password=E,db=redis_db)
		if A.db_engine=='scylladb':A.db_connector=ScylladbConnector(host=B,port=C,user=D,password=E,keyspace=J)
		if A.db_engine=='sqlite':A.db_connector=SqliteConnector(database_path=G)
		if A.db_engine=='wss':A.db_connector=WssConnector(socket_url=socket_url,dynamic_inputs=H,py_code_processing=I)
	def get_db_connector(A):return A.db_connector
	def test_connection(A):return A.db_connector.test_connection()
	def preview_output_connector_bowler(A):return A.db_connector.preview_output_connector_bowler()
	def get_error_msg_test_connection(A):return A.db_connector.get_error_msg_test_connection()
	def get_available_tables(A):B=A.db_connector.get_available_tables();return B
	def get_available_views(A):B=A.db_connector.get_available_views();return B
	def get_table_columns(A,table_name):B=A.db_connector.get_table_columns(table_name);return B
	def get_data_table(A,table_name):
		if A.db_engine==_B:return A.db_connector.get_json_api_dataframe()
		else:
			B=A.db_connector.get_data_table(table_name)
			if isinstance(B,pd.DataFrame):return B
			return pd.DataFrame(B)
	def get_data_table_top(A,table_name,top_limit=100):
		if A.db_engine==_B:return A.db_connector.get_json_api_dataframe()
		else:
			B=A.db_connector.get_data_table_top(table_name,top_limit)
			if isinstance(B,pd.DataFrame):return B
			return pd.DataFrame(B)
	def get_data_table_query(A,sql,table_name=_A):return A.db_connector.get_data_table_query(sql,table_name=table_name)